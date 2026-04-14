"""
Scuba Cat - Streamlit Web App
Motion detection triggers the scuba cat video in the browser.
"""

import streamlit as st
import cv2
import numpy as np
from pathlib import Path
import base64
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🐱 Scuba Cat",
    page_icon="🐱",
    layout="centered",
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_video_b64(path: str) -> str:
    """Return the mp4 file as a base64 data-URI."""
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def motion_percentage(prev_frame, curr_frame, h, w) -> float:
    """Frame-differencing motion detection (mirrors gesture_detector.py)."""
    diff = cv2.absdiff(prev_frame, curr_frame)
    gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    rs, re = int(h * 0.2), int(h * 0.8)
    cs, ce = int(w * 0.2), int(w * 0.95)
    roi = gray[rs:re, cs:ce]

    _, thresh = cv2.threshold(roi, 15, 255, cv2.THRESH_BINARY)
    pixels = cv2.countNonZero(thresh)
    size = (re - rs) * (ce - cs)
    return pixels / size if size > 0 else 0.0


# ── Session state ─────────────────────────────────────────────────────────────
for key, default in {
    "prev_frame": None,
    "frame_count": 0,
    "last_trigger": 0.0,
    "video_triggered": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

REQUIRED_FRAMES = 5
MOTION_THRESHOLD = 0.01
COOLDOWN_SECONDS = 4

# ── Video path ────────────────────────────────────────────────────────────────
VIDEO_PATH = Path(__file__).parent / "scuba_cat.mp4"
video_b64 = load_video_b64(str(VIDEO_PATH)) if VIDEO_PATH.exists() else None

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style='text-align:center; font-size:2.8rem;'>🐱 Scuba Cat</h1>
    <p style='text-align:center; color:gray;'>
        Move your hand in front of the camera — Scuba Cat appears!
    </p>
    """,
    unsafe_allow_html=True,
)

st.divider()

# Video player (hidden until triggered)
video_placeholder = st.empty()

if st.session_state["video_triggered"] and video_b64:
    video_placeholder.markdown(
        f"""
        <video autoplay controls style='width:100%; border-radius:12px;'>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        """,
        unsafe_allow_html=True,
    )
else:
    video_placeholder.markdown(
        "<p style='text-align:center; color:#aaa; font-size:1.1rem;'>"
        "🎬 Video will play here when motion is detected</p>",
        unsafe_allow_html=True,
    )

st.divider()

# Camera feed
col1, col2 = st.columns([3, 1])

with col1:
    camera_image = st.camera_input("📷 Camera feed — move your hand to trigger!", label_visibility="visible")

with col2:
    st.markdown("### Status")
    status_box = st.empty()
    motion_bar_label = st.empty()
    motion_bar = st.empty()
    reset_btn = st.button("🔄 Reset", use_container_width=True)

if reset_btn:
    st.session_state["video_triggered"] = False
    st.session_state["prev_frame"] = None
    st.session_state["frame_count"] = 0
    st.rerun()

# ── Motion processing ─────────────────────────────────────────────────────────
if camera_image is not None:
    # Decode captured frame
    file_bytes = np.frombuffer(camera_image.getvalue(), np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]

    if st.session_state["prev_frame"] is not None:
        mp = motion_percentage(st.session_state["prev_frame"], rgb, h, w)

        # Update detection counter
        if mp > MOTION_THRESHOLD:
            st.session_state["frame_count"] += 1
        else:
            st.session_state["frame_count"] = max(0, st.session_state["frame_count"] - 1)

        # Trigger if enough consecutive motion frames & cooldown elapsed
        now = time.time()
        if (
            st.session_state["frame_count"] >= REQUIRED_FRAMES
            and (now - st.session_state["last_trigger"]) > COOLDOWN_SECONDS
        ):
            st.session_state["video_triggered"] = True
            st.session_state["last_trigger"] = now
            st.session_state["frame_count"] = 0
            st.rerun()

        # Status display
        pct = min(st.session_state["frame_count"] / REQUIRED_FRAMES, 1.0)
        if st.session_state["video_triggered"]:
            status_box.success("🐱 Scuba Cat!")
        elif st.session_state["frame_count"] > 0:
            status_box.warning(f"👋 Detecting… {st.session_state['frame_count']}/{REQUIRED_FRAMES}")
        else:
            status_box.info("👀 Watching…")

        motion_bar_label.caption(f"Charge: {int(pct*100)}%")
        motion_bar.progress(pct)

    st.session_state["prev_frame"] = rgb

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    "<br><p style='text-align:center; color:#bbb; font-size:0.8rem;'>"
    "Made with 🐾 for my favourite person</p>",
    unsafe_allow_html=True,
)

"""
Scuba Cat - Streamlit Web App
Motion detection runs in the browser via JS (no click needed).
When motion is detected, the scuba cat video plays automatically.
"""

import streamlit as st
import base64
from pathlib import Path

st.set_page_config(page_title="🐱 Scuba Cat", page_icon="🐱", layout="centered")

# ── Load video as base64 ──────────────────────────────────────────────────────
VIDEO_PATH = Path(__file__).parent / "scuba_cat.mp4"

if not VIDEO_PATH.exists():
    st.error("scuba_cat.mp4 not found next to app.py!")
    st.stop()

with open(VIDEO_PATH, "rb") as f:
    video_b64 = base64.b64encode(f.read()).decode()

# ── Main UI ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style='text-align:center;'>🐱 Scuba Cat</h1>
    <p style='text-align:center; color:gray;'>
        Move your hand in front of the camera — Scuba Cat appears!
    </p>
    """,
    unsafe_allow_html=True,
)

# ── Self-contained HTML/JS component ─────────────────────────────────────────
html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; font-family: sans-serif; }}

  #container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 14px;
    padding: 10px;
  }}

  #videoBox {{
    position: relative;
    width: 100%;
    max-width: 520px;
  }}

  #webcam {{
    width: 100%;
    border-radius: 12px;
    display: block;
    transform: scaleX(-1);
  }}

  #overlay {{
    position: absolute;
    top: 10px; left: 10px;
    background: rgba(0,0,0,0.55);
    color: #fff;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 13px;
    pointer-events: none;
  }}

  #meterWrap {{
    width: 100%;
    max-width: 520px;
  }}

  #meterLabel {{
    font-size: 13px;
    color: #555;
    margin-bottom: 4px;
  }}

  #meter {{
    width: 100%;
    height: 12px;
    background: #e0e0e0;
    border-radius: 6px;
    overflow: hidden;
  }}

  #meterFill {{
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #4CAF50, #8BC34A);
    border-radius: 6px;
    transition: width 0.1s;
  }}

  #catVideo {{
    display: none;
    width: 100%;
    max-width: 520px;
    border-radius: 12px;
  }}

  #status {{
    font-size: 15px;
    font-weight: 600;
    color: #333;
  }}

  #resetBtn {{
    padding: 8px 22px;
    border: none;
    border-radius: 8px;
    background: #f0f0f0;
    cursor: pointer;
    font-size: 14px;
  }}
  #resetBtn:hover {{ background: #ddd; }}

  canvas {{ display: none; }}
</style>
</head>
<body>
<div id="container">

  <div id="videoBox">
    <video id="webcam" autoplay playsinline muted></video>
    <div id="overlay">👀 Watching for motion…</div>
  </div>

  <div id="meterWrap">
    <div id="meterLabel">Motion charge: 0%</div>
    <div id="meter"><div id="meterFill"></div></div>
  </div>

  <div id="status">Move your hand to trigger!</div>

  <video id="catVideo" src="data:video/mp4;base64,{video_b64}" controls></video>

  <button id="resetBtn" onclick="resetApp()">🔄 Reset</button>

</div>

<canvas id="canvas"></canvas>

<script>
const webcam      = document.getElementById('webcam');
const canvas      = document.getElementById('canvas');
const ctx         = canvas.getContext('2d');
const catVideo    = document.getElementById('catVideo');
const overlay     = document.getElementById('overlay');
const meterFill   = document.getElementById('meterFill');
const meterLabel  = document.getElementById('meterLabel');
const statusEl    = document.getElementById('status');

/* ── Tuning knobs (matched to the working Python detector) ── */
const MOTION_THRESHOLD  = 0.01;    // 1% of ROI pixels must differ (was 1.2%)
const REQUIRED_FRAMES   = 5;      // consecutive motion frames needed (was 6)
const COOLDOWN_MS       = 4000;
const PIXEL_DIFF_THRESH = 15;     // per-channel difference (was 20)
const DECAY_DELAY_MS    = 400;    // hold charge for this long after last motion

/* ── Downsample factor for noise reduction ── */
const DS = 4;                     // compare at 1/4 resolution

let prevSmall      = null;
let frameCount     = 0;
let lastTrigger    = 0;
let lastMotionTime = 0;
let triggered      = false;
let prevTime       = 0;           // webcam frame dedup

/* ── Small canvas used for downsampled comparison ── */
const smallCanvas = document.createElement('canvas');
const smallCtx    = smallCanvas.getContext('2d');

navigator.mediaDevices.getUserMedia({{ video: true, audio: false }})
  .then(stream => {{
    webcam.srcObject = stream;
    webcam.onloadedmetadata = () => {{
      canvas.width  = webcam.videoWidth;
      canvas.height = webcam.videoHeight;
      smallCanvas.width  = Math.floor(webcam.videoWidth  / DS);
      smallCanvas.height = Math.floor(webcam.videoHeight / DS);
      requestAnimationFrame(tick);
    }};
  }})
  .catch(err => {{
    statusEl.textContent = '⚠️ Camera access denied: ' + err.message;
  }});

function tick() {{
  if (triggered) {{ requestAnimationFrame(tick); return; }}

  /* ── Skip duplicate frames ─────────────────────────────────
     requestAnimationFrame fires at ~60 fps but the webcam only
     delivers new frames at ~30 fps.  If we compare an identical
     frame we get 0 motion and wrongly decrement the counter.
     We detect duplicates by checking the video's currentTime. */
  const vt = webcam.currentTime;
  if (vt === prevTime) {{
    requestAnimationFrame(tick);
    return;
  }}
  prevTime = vt;

  /* ── Downsample: draw webcam → small canvas (acts as blur) ── */
  const sw = smallCanvas.width;
  const sh = smallCanvas.height;
  smallCtx.drawImage(webcam, 0, 0, sw, sh);
  const frame = smallCtx.getImageData(0, 0, sw, sh);
  const data  = frame.data;

  if (prevSmall) {{
    const rs = Math.floor(sh * 0.20), re = Math.floor(sh * 0.80);
    const cs = Math.floor(sw * 0.20), ce = Math.floor(sw * 0.95);
    const roiSize = (re - rs) * (ce - cs);
    let changed = 0;

    for (let y = rs; y < re; y++) {{
      for (let x = cs; x < ce; x++) {{
        const i = (y * sw + x) * 4;
        const dr = Math.abs(data[i]   - prevSmall[i]);
        const dg = Math.abs(data[i+1] - prevSmall[i+1]);
        const db = Math.abs(data[i+2] - prevSmall[i+2]);
        if (dr > PIXEL_DIFF_THRESH || dg > PIXEL_DIFF_THRESH || db > PIXEL_DIFF_THRESH) {{
          changed++;
        }}
      }}
    }}

    const mp  = changed / roiSize;
    const now = Date.now();

    if (mp > MOTION_THRESHOLD) {{
      frameCount++;
      lastMotionTime = now;
    }} else {{
      /* Time-based decay: only drain the meter if no motion
         has been seen for DECAY_DELAY_MS.  This prevents the
         charge from bouncing due to brief inter-frame lulls. */
      if (now - lastMotionTime > DECAY_DELAY_MS) {{
        frameCount = Math.max(0, frameCount - 1);
      }}
    }}

    const pct = Math.min(frameCount / REQUIRED_FRAMES, 1.0);
    meterFill.style.width  = (pct * 100) + '%';
    meterLabel.textContent = 'Motion charge: ' + Math.round(pct * 100) + '%';

    if (frameCount > 0 && frameCount < REQUIRED_FRAMES) {{
      overlay.textContent  = '👋 Detecting… ' + frameCount + '/' + REQUIRED_FRAMES;
      statusEl.textContent = 'Keep moving!';
    }} else if (frameCount === 0) {{
      overlay.textContent  = '👀 Watching for motion…';
      statusEl.textContent = 'Move your hand to trigger!';
    }}

    if (frameCount >= REQUIRED_FRAMES && (now - lastTrigger) > COOLDOWN_MS) {{
      triggerCat();
      lastTrigger = now;
      frameCount  = 0;
    }}
  }}

  prevSmall = new Uint8ClampedArray(data);
  requestAnimationFrame(tick);
}}

function triggerCat() {{
  triggered = true;
  catVideo.style.display = 'block';
  catVideo.currentTime   = 0;
  catVideo.play();
  overlay.textContent    = '🐱 SCUBA CAT!';
  statusEl.textContent   = '🐱 Scuba Cat activated!';
  meterFill.style.width  = '100%';
  meterFill.style.background = 'linear-gradient(90deg,#ff9800,#f44336)';

  catVideo.onended = () => {{
    triggered = false;
    catVideo.style.display = 'none';
    meterFill.style.background = 'linear-gradient(90deg,#4CAF50,#8BC34A)';
    statusEl.textContent = 'Move your hand to trigger again!';
    overlay.textContent  = '👀 Watching for motion…';
    meterFill.style.width = '0%';
    meterLabel.textContent = 'Motion charge: 0%';
  }};
}}

function resetApp() {{
  triggered   = false;
  frameCount  = 0;
  prevData    = null;
  catVideo.pause();
  catVideo.currentTime   = 0;
  catVideo.style.display = 'none';
  meterFill.style.width  = '0%';
  meterFill.style.background = 'linear-gradient(90deg,#4CAF50,#8BC34A)';
  meterLabel.textContent = 'Motion charge: 0%';
  overlay.textContent    = '👀 Watching for motion…';
  statusEl.textContent   = 'Move your hand to trigger!';
}}
</script>
</body>
</html>
"""

st.components.v1.html(html, height=720, scrolling=False)

st.markdown(
    "<p style='text-align:center; color:#bbb; font-size:0.8rem; margin-top:8px;'>"
    "Made with 🐾 for my favourite person</p>",
    unsafe_allow_html=True,
)

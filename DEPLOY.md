# 🐱 Scuba Cat — Streamlit Web App

Motion detection in the browser triggers the scuba cat meme video. Works on any device with a camera — including your phone!

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## Deploy Free on Streamlit Community Cloud (recommended)

1. Push this repo to GitHub (make sure `scuba_cat.mp4` is committed).
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
3. Click **"New app"** → select your repo → set **Main file path** to `app.py`.
4. Hit **Deploy** — you'll get a public URL to share with anyone! 🎉

> **Note:** The free tier has a 1 GB memory limit, so make sure `scuba_cat.mp4` isn't too large.
> If the file is large, compress it first with:
> ```bash
> ffmpeg -i scuba_cat.mp4 -vcodec libx264 -crf 28 scuba_cat_compressed.mp4
> ```

---

## How It Works

| Component | Description |
|-----------|-------------|
| `app.py` | Streamlit app — camera feed + motion detection + video playback |
| `gesture_detector.py` | Original motion logic (reference) |
| `scuba_cat.mp4` | The meme video |

The app uses `st.camera_input` to grab frames from the browser webcam, runs frame-differencing to detect hand motion, and plays the video via an embedded HTML5 `<video>` tag when triggered.

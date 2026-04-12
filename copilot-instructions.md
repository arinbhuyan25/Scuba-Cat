# Scuba Cat Gesture Detector - Project Setup

A gesture detection application that uses your webcam to detect the scuba cat movement and plays a meme video.

## Setup Checklist

- [x] Project scaffolded with Python structure
- [x] Dependencies specified in requirements.txt
- [x] Core modules created (gesture_detector.py, video_player.py, main.py)
- [x] Documentation (README.md) completed
- [ ] Dependencies installed
- [ ] Video file added to assets/
- [ ] Application tested

## Installation Steps

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Add your scuba cat meme video to the `assets/` folder with the name `scuba_cat.mp4`

3. Run the application:
```bash
python main.py
```

## How to Use

- Put LEFT hand near mouth/face
- Move RIGHT hand in scooping motion
- Hold for ~0.3 seconds
- Video plays automatically!

Press 'q' to quit.

## Project Details

- **Language**: Python 3.8+
- **Main Technologies**: OpenCV, MediaPipe, Threading
- **entry Point**: main.py

## Notes

- Requires a webcam
- Works best in good lighting
- Supports MP4, AVI, MOV, MKV video formats
- Real-time performance optimized for standard laptops

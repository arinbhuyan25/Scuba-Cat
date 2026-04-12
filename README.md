# Scuba Cat Gesture Detector 🐱

A real-time gesture detection application that captures camera feed and plays the scuba cat meme when you perform the scuba cat gesture!

## Features

- **Real-time gesture detection** using MediaPipe hand tracking
- **Automatic video playback** when gesture is detected
- **Gesture recognition** for scuba cat movement (left hand on face + right hand scooping motion)
- **Webcam integration** with live feedback
- **Cooldown system** to prevent multiple rapid triggers

## Requirements

- Python 3.8+
- Webcam/Camera
- Scuba cat meme video file (MP4, AVI, MOV, or MKV)

## Installation

1. Clone or download this project

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Add your scuba cat meme video:
   - Place your video file in the `assets/` folder
   - Name it `scuba_cat.mp4` (or edit `main.py` line 13 with your filename)

## Usage

1. Run the application:
```bash
python main.py
```

2. **Perform the scuba cat gesture:**
   - Put your LEFT hand near your mouth/face area
   - Move your RIGHT hand in a scooping motion
   - Hold the gesture for about 0.3 seconds
   - The scuba cat meme will play!

3. **Controls:**
   - Press `q` to quit the application
   - Press `p` to manually play the video (for testing)

## Project Structure

```
scuba cat/
├── main.py                   # Main application
├── gesture_detector.py       # Hand gesture detection logic
├── video_player.py           # Video playback handler
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── assets/
    └── scuba_cat.mp4        # Your scuba cat meme video (add this)
```

## How It Works

### Gesture Detection Algorithm

The gesture detector uses Google's MediaPipe library to track hand positions in real-time:

1. **Left Hand Detection**: Checks if left hand is in the face/mouth region
2. **Right Hand Movement**: Detects motion in the right hand (scooping gesture)
3. **Confirmation**: Requires the gesture to be held for ~10 frames (~0.3 seconds) before triggering
4. **Cooldown**: Prevents multiple rapid triggers (2-second cooldown)

### System Components

- **GestureDetector**: Analyzes hand landmarks to identify the scuba cat gesture
- **VideoPlayer**: Handles video playback in a separate thread for smooth operation
- **Main Loop**: Captures camera frames, detects gestures, and manages UI

## Troubleshooting

### Camera not detected
- Check that your webcam is connected and working
- Try changing `CAMERA_INDEX` in `main.py` (0 for default, 1, 2, etc. for other cameras)

### Gesture not detected
- Ensure good lighting conditions
- The detector works best with clear hand visibility
- Try adjusting the `min_detection_confidence` in `gesture_detector.py` (line 14)
- Lower values = more sensitive but less accurate

### Video not playing
- Verify the video file exists in `assets/` folder
- Check the file format (MP4, AVI, MOV, MKV supported)
- Try using a different video format or converting it

### Performance issues
- Reduce camera resolution in `main.py`
- Comment out the landmark drawing line for better performance
- Close other applications consuming CPU/GPU

## Customization

### Change the gesture
Edit the `detect_scuba_cat_gesture()` method in `gesture_detector.py` to detect different hand movements

### Adjust sensitivity
- `required_frames` in `GestureDetector.__init__()`: How long gesture must be held (default: 10 frames)
- `cooldown_frames` in `main.py`: Delay between consecutive triggers (default: 60 frames)
- `min_detection_confidence` in `gesture_detector.py`: Hand detection confidence threshold (0-1)

### Use different video
Update `VIDEO_PATH` in `main.py` to point to your custom video file

## Tips for Best Results

1. **Lighting**: Good lighting helps hand detection
2. **Distance**: Keep hands 1-2 feet from camera
3. **Movement**: Make smooth, deliberate gestures
4. **Patience**: The gesture needs to be held for a moment (~0.3 seconds)

## Credits

- Hand detection: [MediaPipe](https://mediapipe.dev/)
- Video playback: [OpenCV](https://opencv.org/)

## License

Free to use and modify for personal projects.


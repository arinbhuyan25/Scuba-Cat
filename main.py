"""
Scuba Cat Gesture Detection
Main application that captures camera feed and detects scuba cat gesture
When detected, plays the scuba cat meme video
"""

import cv2
import sys
from pathlib import Path
from gesture_detector import GestureDetector
from video_player import VideoPlayer


def main():
    # Configuration
    VIDEO_PATH = "assets/scuba_cat.mp4"  # Replace with your scuba cat meme video path
    CAMERA_INDEX = 0  # Default camera
    
    # Check if video file exists
    if not Path(VIDEO_PATH).exists():
        print(f"Error: Video file not found at {VIDEO_PATH}")
        print(f"Please place your scuba cat meme video at: {Path(VIDEO_PATH).absolute()}")
        print("\nSupported formats: MP4, AVI, MOV, MKV")
        return
    
    # Initialize gesture detector and video player
    detector = GestureDetector()
    player = VideoPlayer(VIDEO_PATH)
    
    # Open camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera at index {CAMERA_INDEX}")
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("Scuba Cat Gesture Detector Started!")
    print("=" * 50)
    print("Instructions:")
    print("1. Click on the camera window to focus it")
    print("2. Put your LEFT hand near your mouth/face")
    print("3. Move your RIGHT hand in a scooping motion")
    print("4. Hold the gesture for ~0.3 seconds")
    print("5. Scuba cat meme will play!")
    print("\nPress 'q' to quit")
    print("=" * 50)
    
    cv2.namedWindow("Scuba Cat Detector", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Scuba Cat Detector", 640, 480)
    
    frame_count = 0
    last_trigger_frame = 0
    cooldown_frames = 100  # Prevent multiple triggers within ~3+ seconds
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to read frame from camera")
                break
            
            # Flip frame for selfie-view
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect gesture
            gesture_detected = detector.detect_scuba_cat_gesture(frame, rgb_frame)
            
            # Trigger video playback with cooldown
            if gesture_detected and (frame_count - last_trigger_frame) > cooldown_frames:
                if not player.is_currently_playing():
                    print("🐱 Scuba Cat gesture detected! Playing video...")
                    player.play()
                    last_trigger_frame = frame_count
            
            # Draw landmarks for debugging (optional - comment out for performance)
            # frame = detector.draw_landmarks(frame, rgb_frame)
            
            # Add UI text to frame
            status_text = "Gesture Status: Ready"
            if detector.frame_count > 0:
                status_text = f"Gesture Status: Detecting... {detector.frame_count}/{detector.required_frames}"
            
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            
            # Show motion percentage for debugging
            motion_text = f"Motion: {detector.last_motion_percentage*100:.2f}%"
            cv2.putText(frame, motion_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (100, 100, 255), 1)
            
            if player.is_currently_playing():
                cv2.putText(frame, "Video Playing!", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (0, 0, 255), 2)
            
            cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display frame
            cv2.imshow("Scuba Cat Detector", frame)
            
            # Handle key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quitting...")
                break
            elif key == ord('p'):
                # Manual trigger for testing
                if not player.is_currently_playing():
                    print("Playing video (manual trigger)...")
                    player.play()
            
            frame_count += 1
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Cleanup
        player.stop()
        cap.release()
        cv2.destroyAllWindows()
        print("Scuba Cat Detector closed.")


if __name__ == "__main__":
    main()

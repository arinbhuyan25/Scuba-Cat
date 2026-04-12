"""
Gesture Detection Module
Detects the scuba cat gesture (hand on mouth + hand movement)
"""

import cv2
import math
from typing import Tuple, Optional
import numpy as np


class GestureDetector:
    def __init__(self):
        self.left_hand_landmarks = None
        self.right_hand_landmarks = None
        self.gesture_detected = False
        self.frame_count = 0
        self.required_frames = 5  # Require gesture for 5 frames (~0.17 seconds)
        self.prev_frame = None
        self.last_motion_percentage = 0  # For debugging
        
    def distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def detect_scuba_cat_gesture(self, frame, rgb_frame) -> bool:
        """
        Detect scuba cat gesture using frame differencing and motion detection
        - Left hand on face/mouth area
        - Right hand moving (making the scooping motion)
        """
        h, w, c = frame.shape
        
        # Initialize previous frame if needed
        if self.prev_frame is None:
            self.prev_frame = rgb_frame.copy()
            return False
        
        # Calculate frame difference
        diff = cv2.absdiff(self.prev_frame, rgb_frame)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
        
        # Blur to reduce noise
        gray_diff = cv2.GaussianBlur(gray_diff, (5, 5), 0)
        
        # Look for motion in the right side and center (hand area only)
        roi_height_start = int(h * 0.2)
        roi_height_end = int(h * 0.8)
        roi_width_start = int(w * 0.2)
        roi_width_end = int(w * 0.95)
        
        roi = gray_diff[roi_height_start:roi_height_end, roi_width_start:roi_width_end]
        
        # Lower threshold for more sensitivity
        _, thresh = cv2.threshold(roi, 15, 255, cv2.THRESH_BINARY)
        motion_pixels = cv2.countNonZero(thresh)
        roi_size = (roi_height_end - roi_height_start) * (roi_width_end - roi_width_start)
        motion_percentage = motion_pixels / roi_size if roi_size > 0 else 0
        
        # Store for debugging
        self.last_motion_percentage = motion_percentage
        
        # Update previous frame
        self.prev_frame = rgb_frame.copy()
        
        # Check if we have significant motion (threshold: 1%)
        if motion_percentage > 0.01:
            self.frame_count += 1
            print(f"Motion {self.frame_count}/{self.required_frames}: {motion_percentage*100:.2f}%")
            if self.frame_count >= self.required_frames:
                self.gesture_detected = True
                self.frame_count = 0
                return True
        else:
            if self.frame_count > 0:
                print(f"Motion reset (was {self.frame_count})")
            self.frame_count = max(0, self.frame_count - 1)
        
        return False
    
    def draw_landmarks(self, frame, rgb_frame):
        """Draw motion areas for debugging"""
        h, w = frame.shape[:2]
        
        # Draw ROI rectangle
        roi_height_start = int(h * 0.15)
        roi_height_end = int(h * 0.75)
        roi_width_start = int(w * 0.3)
        roi_width_end = w
        
        cv2.rectangle(frame, (roi_width_start, roi_height_start), (roi_width_end, roi_height_end), (0, 255, 0), 2)
        
        return frame

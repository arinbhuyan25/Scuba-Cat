"""
Video Player Module
Handles playing video files in a separate window
"""

import cv2
import os
from threading import Thread
from pathlib import Path


class VideoPlayer:
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.is_playing = False
        self.playback_thread = None
        
    def play(self):
        """Play video in a separate thread"""
        if not os.path.exists(self.video_path):
            print(f"Error: Video file not found at {self.video_path}")
            return False
        
        if self.is_playing:
            return False
        
        self.is_playing = True
        self.playback_thread = Thread(target=self._play_video, daemon=True)
        self.playback_thread.start()
        return True
    
    def _play_video(self):
        """Internal method to play video"""
        try:
            cap = cv2.VideoCapture(self.video_path)
            
            if not cap.isOpened():
                print(f"Error: Could not open video {self.video_path}")
                self.is_playing = False
                return
            
            window_name = "Scuba Cat Meme!"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 640, 480)
            
            while self.is_playing:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Resize frame for display
                frame = cv2.resize(frame, (640, 480))
                cv2.imshow(window_name, frame)
                
                # Press 'q' to stop playback early
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyWindow(window_name)
            self.is_playing = False
            
        except Exception as e:
            print(f"Error playing video: {e}")
            self.is_playing = False
    
    def stop(self):
        """Stop video playback"""
        self.is_playing = False
        if self.playback_thread:
            self.playback_thread.join(timeout=2)
    
    def is_currently_playing(self) -> bool:
        """Check if video is currently playing"""
        return self.is_playing


def convert_video_format(input_path: str, output_path: str, codec: str = 'mp4v'):
    """
    Convert video to a supported format if needed
    Useful for converting various video formats to MP4
    """
    try:
        cap = cv2.VideoCapture(input_path)
        
        if not cap.isOpened():
            print(f"Error: Could not open video {input_path}")
            return False
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        
        cap.release()
        out.release()
        print(f"Video converted successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error converting video: {e}")
        return False

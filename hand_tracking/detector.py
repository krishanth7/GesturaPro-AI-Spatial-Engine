import cv2
import mediapipe as mp
import numpy as np
import os
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
from mediapipe.tasks.python.core import base_options
from utils.config import Config

class HandDetector:
    """Production Hand Detector using MediaPipe Tasks API."""
    
    def __init__(self, model_name="hand_landmarker.task"):
        # Resolve model path relative to the project root
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_path, model_name)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        # Configure Hand Landmarker
        base_opts = base_options.BaseOptions(model_asset_path=model_path)
        options = HandLandmarkerOptions(
            base_options=base_opts,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=Config.MAX_NUM_HANDS,
            min_hand_detection_confidence=Config.MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=Config.MIN_TRACKING_CONFIDENCE,
            min_tracking_confidence=Config.MIN_TRACKING_CONFIDENCE
        )
        self.detector = HandLandmarker.create_from_options(options)
        self.results = None
        self.frame_timestamp_ms = 0

    def find_hands(self, img, draw=True):
        """Processes image and extracts hand landmarks using Tasks API."""
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Detect landmarks with temporal context (VIDEO mode)
        self.frame_timestamp_ms += 33 # Assume approx 30fps for tracker logic
        self.results = self.detector.detect_for_video(mp_image, self.frame_timestamp_ms)
        
        all_hands = []
        h, w, _ = img.shape
        
        if self.results.hand_landmarks:
            for idx, hand_lms in enumerate(self.results.hand_landmarks):
                my_hand = {}
                lm_list = []
                for id, lm in enumerate(hand_lms):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy, lm.z])
                
                my_hand["lm_list"] = lm_list
                # Tasks API handedness
                hand_type = self.results.handedness[idx][0].category_name
                my_hand["type"] = hand_type # 'Left' or 'Right'
                all_hands.append(my_hand)
                
                if draw:
                    self._draw_landmarks(img, lm_list)
                    
        return all_hands, img

    def _draw_landmarks(self, img, lm_list):
        """Advanced 'Skeletal Scanning' visualization."""
        # Color Palette
        cyan = (0, 255, 255)
        white = (255, 255, 255)
        
        # Draw connections with a glow effect
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4), # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8), # Index
            (9, 10), (10, 11), (11, 12),    # Middle
            (13, 14), (14, 15), (15, 16),   # Ring
            (17, 18), (18, 19), (19, 20),   # Pinky
            (5, 9), (9, 13), (13, 17), (0, 17) # Palm
        ]
        
        # Glow Layer (Manual Blur logic)
        for start, end in connections:
            p1 = (lm_list[start][1], lm_list[start][2])
            p2 = (lm_list[end][1], lm_list[end][2])
            cv2.line(img, p1, p2, cyan, 1) # Thin primary line
            
        for id, x, y, z in lm_list:
            # Joint points
            color = white if id in [4, 8, 12, 16, 20] else cyan
            radius = 4 if id in [4, 8, 12, 16, 20] else 2
            cv2.circle(img, (x, y), radius, color, -1)
            
            # Highlight fingertips
            if id in [4, 8, 12, 16, 20]:
                cv2.circle(img, (x, y), 8, cyan, 1)


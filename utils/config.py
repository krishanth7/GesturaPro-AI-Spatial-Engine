import yaml
import os

class Config:
    """Central configuration management."""
    
    # Camera settings
    CAMERA_ID = 0
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
    
    # MediaPipe settings
    MIN_DETECTION_CONFIDENCE = 0.7
    MIN_TRACKING_CONFIDENCE = 0.7
    MAX_NUM_HANDS = 2
    
    # Smoothing settings
    SMOOTHING_FACTOR = 0.2  # Moving average factor (0-1)
    KALMAN_Q = 1e-5         # Process noise covariance
    KALMAN_R = 1e-2         # Measurement noise covariance
    
    # Gesture thresholds
    PINCH_THRESHOLD = 0.05   # Normalized distance for pinch
    RESET_THRESHOLD = 0.8    # Palm openness threshold
    
    # Object settings
    INITIAL_SCALE = 1.0
    MIN_SCALE = 0.2
    MAX_SCALE = 5.0
    
    @classmethod
    def load_config(cls, path="config.yaml"):
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                for key, value in data.items():
                    if hasattr(cls, key):
                        setattr(cls, key, value)
    
    @classmethod
    def save_config(cls, path="config.yaml"):
        data = {k: v for k, v in cls.__dict__.items() if not k.startswith("__") and not callable(v)}
        with open(path, 'w') as f:
            yaml.dump(data, f)

# Initial default config
if __name__ == "__main__":
    Config.save_config()

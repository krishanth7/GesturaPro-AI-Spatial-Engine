import numpy as np
from utils.config import Config

class ExponentialSmoothing:
    def __init__(self, alpha=Config.SMOOTHING_FACTOR):
        self.alpha = alpha
        self.last_value = None

    def smooth(self, value):
        if self.last_value is None:
            self.last_value = value
            return value
        
        smoothed = self.alpha * value + (1 - self.alpha) * self.last_value
        self.last_value = smoothed
        return smoothed

class KalmanFilter:
    def __init__(self, q=Config.KALMAN_Q, r=Config.KALMAN_R):
        self.x = 0.0  # State estimate
        self.p = 1.0  # Estimate error covariance
        self.q = q    # Process noise covariance
        self.r = r    # Measurement noise covariance
        self.k = 0.0  # Kalman gain
        self.initialized = False

    def update(self, measurement):
        if not self.initialized:
            self.x = measurement
            self.initialized = True
            return measurement

        # Prediction step
        self.p = self.p + self.q

        # Correction step
        self.k = self.p / (self.p + self.r)
        self.x = self.x + self.k * (measurement - self.x)
        self.p = (1 - self.k) * self.p

        return self.x

class MultiValueSmoother:
    """Convenience class to smooth multiple values (e.g., [x, y, z])."""
    def __init__(self, count, type='exp', **kwargs):
        if type == 'exp':
            self.smoothers = [ExponentialSmoothing(**kwargs) for _ in range(count)]
        else:
            self.smoothers = [KalmanFilter(**kwargs) for _ in range(count)]

    def smooth(self, values):
        return [s.smooth(v) if hasattr(s, 'smooth') else s.update(v) for s, v in zip(self.smoothers, values)]

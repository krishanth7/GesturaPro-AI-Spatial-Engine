from utils.config import Config
from utils.math_helpers import clamp

class ScalingController:
    """Handles scaling logic based on gesture input."""
    
    def __init__(self, initial_scale=Config.INITIAL_SCALE):
        self.scale = initial_scale
        self.reference_dist = None
        self.initial_obj_scale = None

    def update(self, is_pinching, current_dist):
        if is_pinching:
            if self.reference_dist is None:
                self.reference_dist = current_dist
                self.initial_obj_scale = self.scale
            
            # Simple linear scaling based on relative distance change
            # Optimization: could be logarithmic for better feel
            scale_diff = current_dist / self.reference_dist if self.reference_dist > 0 else 1.0
            self.scale = clamp(self.initial_obj_scale * scale_diff, Config.MIN_SCALE, Config.MAX_SCALE)
        else:
            self.reference_dist = None
            self.initial_obj_scale = None
            
        return self.scale

    def reset(self):
        self.scale = Config.INITIAL_SCALE
        self.reference_dist = None

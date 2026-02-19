class RotationController:
    """Handles rotation logic based on hand angle."""
    
    def __init__(self):
        self.angle = 0
        self.reference_angle = None
        self.initial_obj_angle = None

    def update(self, is_pinching, current_angle):
        if is_pinching:
            if self.reference_angle is None:
                self.reference_angle = current_angle
                self.initial_obj_angle = self.angle
            
            angle_diff = current_angle - self.reference_angle
            self.angle = (self.initial_obj_angle + angle_diff) % 360
        else:
            self.reference_angle = None
            self.initial_obj_angle = None
            
        return self.angle

    def reset(self):
        self.angle = 0
        self.reference_angle = None

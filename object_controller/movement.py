from utils.config import Config

class MovementController:
    """Handles 2D/3D movement logic."""
    
    def __init__(self, initial_pos=(Config.FRAME_WIDTH//2, Config.FRAME_HEIGHT//2)):
        self.pos = list(initial_pos)
        self.reference_pos = None
        self.initial_obj_pos = None

    def update(self, is_pinching, current_pos):
        if is_pinching:
            if self.reference_pos is None:
                self.reference_pos = current_pos
                self.initial_obj_pos = list(self.pos)
            
            dx = current_pos[0] - self.reference_pos[0]
            dy = current_pos[1] - self.reference_pos[1]
            
            self.pos[0] = self.initial_obj_pos[0] + dx
            self.pos[1] = self.initial_obj_pos[1] + dy
        else:
            self.reference_pos = None
            self.initial_obj_pos = None
            
        return self.pos

    def reset(self, initial_pos=(Config.FRAME_WIDTH//2, Config.FRAME_HEIGHT//2)):
        self.pos = list(initial_pos)
        self.reference_pos = None

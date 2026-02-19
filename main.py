import cv2
import numpy as np
import sys
from utils.config import Config
from hand_tracking.detector import HandDetector
from gesture_engine.gesture_classifier import GestureClassifier
from gesture_engine.smoothing import MultiValueSmoother
from object_controller.scaling import ScalingController
from object_controller.rotation import RotationController
from object_controller.movement import MovementController
from ui.visualizer import Visualizer
from ui.canvas import CanvasManager
from utils.math_helpers import calculate_distance

class GesturaPro:
    """Production-grade AI Hand Gesture Interaction System."""
    
    def __init__(self):
        # Load external configuration
        Config.load_config()
        
        # Initialize Core Components
        self.cap = cv2.VideoCapture(Config.CAMERA_ID)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
        
        if not self.cap.isOpened():
            print("[ERROR] Camera initialization failed. Please check hardware.")
            sys.exit(1)
            
        self.detector = HandDetector()
        self.classifier = GestureClassifier()
        self.visualizer = Visualizer()
        self.canvas = CanvasManager()
        
        # Signal Smoother (Kalman Filtering)
        self.smoother = MultiValueSmoother(4, type='kalman')
        
        # State Controllers
        self.scaling = ScalingController()
        self.rotation = RotationController()
        self.movement = MovementController()
        
        self.running = True

    def run(self):
        """Entry point for the production engine with boot sequence."""
        print("--- GESTURA PRO ENGINE STARTED ---")
        
        # Professional Boot Sequence
        boot_frames = 45
        for i in range(boot_frames):
            success, frame = self.cap.read()
            if not success: break
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # Booting UI
            progress = i / boot_frames
            cv2.rectangle(frame, (0, 0), (w, h), (10, 10, 10), -1)
            cv2.putText(frame, "INITIALIZING AI CORE...", (w//2 - 150, h//2 - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 1)
            cv2.rectangle(frame, (w//2 - 150, h//2 + 10), (w//2 + 150, h//2 + 20), (50, 50, 50), -1)
            cv2.rectangle(frame, (w//2 - 150, h//2 + 10), (w//2 - 150 + int(300 * progress), h//2 + 20), (0, 255, 255), -1)
            
            cv2.imshow("Gestura Pro - AI Spatial Interaction", frame)
            cv2.waitKey(20)

        while self.running:
            success, frame = self.cap.read()
            if not success: break
            
            frame = cv2.flip(frame, 1) # Mirror for natural interaction
            
            # 1. Processing Pipeline
            hands_data, frame = self.detector.find_hands(frame)
            hands_info = []
            
            # 2. Logic Dispatcher
            if len(hands_data) == 1:
                self._process_single_hand(hands_data[0], hands_info)
            elif len(hands_data) == 2:
                self._process_dual_hands(hands_data, hands_info)
            else:
                self._handle_idle_state()
                
            # 3. Canvas Layer
            self.canvas.draw(frame)
                
            # 4. State Synthesis & Smoothing
            raw_state = [self.scaling.scale, self.rotation.angle, self.movement.pos[0], self.movement.pos[1]]
            s = self.smoother.smooth(raw_state)
            obj_state = {'scale': s[0], 'angle': s[1], 'pos': (s[2], s[3])}
            
            # 5. Rendering
            # Draw our target 3D object only if not drawing/dragging
            if not self.canvas.drawing and self.canvas.selected_shape_idx == -1:
                self.visualizer.draw_object(frame, obj_state)
                
            self.visualizer.draw_hud(frame, hands_info, obj_state)
            
            cv2.imshow("Gestura Pro - AI Spatial Interaction", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                
        self._shutdown()

    def _process_single_hand(self, hand, info):
        lms = hand["lm_list"]
        is_p, p_dist = self.classifier.is_pinch(lms)
        is_o = self.classifier.is_open_palm(lms)
        angle, center = self.classifier.get_spatial_state(lms)
        
        # Advanced interaction logic:
        # Index point up = DRAW
        # Pinch = DRAG / SELECT
        # Open Palm = CLEAR
        
        # 1. Check for Pointing (Drawing)
        is_pointing = self.classifier.is_pointing(lms)
        index_tip = (lms[8][1], lms[8][2])
        
        state_label = "TRACKING"
        if is_o:
            self.canvas.clear()
            state_label = "COMMAND: CLEAR"
        elif is_p:
            if self.canvas.selected_shape_idx == -1:
                self.canvas.select_at(center)
            self.canvas.drag(center)
            state_label = "COMMAND: DRAG"
        elif is_pointing:
            if not self.canvas.drawing:
                self.canvas.start_drawing(index_tip)
            self.canvas.update_drawing(index_tip)
            state_label = "COMMAND: DRAW"
        else:
            if self.canvas.drawing:
                self.canvas.end_drawing()
            self.canvas.selected_shape_idx = -1
            
        lengths = self.classifier.get_finger_lengths(lms)
        bentness = self.classifier.get_finger_bentness(lms)
        info.append({
            "type": hand["type"], 
            "gesture": state_label,
            "lengths": lengths,
            "bentness": bentness
        })
        
        # Update spatial controllers for legacy support
        if is_p:
            self.scaling.update(True, p_dist * 600)
            self.rotation.update(True, angle)
            self.movement.update(True, center)
        else:
            self.scaling.update(False, 0)
            self.rotation.update(False, 0)
            self.movement.update(False, (0,0))

    def _process_dual_hands(self, hands, info):
        # Implementation for high-end dual-hand scaling
        h1_lms = hands[0]["lm_list"]
        h2_lms = hands[1]["lm_list"]
        
        is_p1, _ = self.classifier.is_pinch(h1_lms)
        is_p2, _ = self.classifier.is_pinch(h2_lms)
        
        _, p1_center = self.classifier.get_spatial_state(h1_lms)
        _, p2_center = self.classifier.get_spatial_state(h2_lms)
        
        info.append({"type": hands[0]["type"], "gesture": "DUAL-TRACK"})
        info.append({"type": hands[1]["type"], "gesture": "DUAL-TRACK"})
        
        if is_p1 and is_p2:
            dist = calculate_distance(p1_center, p2_center)
            mid = ((p1_center[0] + p2_center[0]) // 2, (p1_center[1] + p2_center[1]) // 2)
            self.scaling.update(True, dist)
            self.movement.update(True, mid)

    def _handle_idle_state(self):
        self.scaling.update(False, 0)
        self.rotation.update(False, 0)
        self.movement.update(False, (0,0))

    def _shutdown(self):
        self.cap.release()
        cv2.destroyAllWindows()
        print("--- GESTURA PRO SHUTDOWN CLEANLY ---")

if __name__ == "__main__":
    app = GesturaPro()
    app.run()


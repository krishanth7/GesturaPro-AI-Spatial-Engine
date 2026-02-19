import cv2
import time
import numpy as np
from utils.config import Config

class Visualizer:
    """Industrial-grade UI visualization for Gestura Pro."""
    
    def __init__(self):
        self.p_time = 0
        self.fps = 0
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.boot_start = time.time()
        
    def draw_hud(self, img, hands_info, obj_state):
        """Draws a professional, futuristic industrial HUD."""
        h, w, _ = img.shape
        
        # 1. Digital Frame / Border
        color_main = (0, 255, 255) # Cyan
        thickness = 2
        margin = 20
        
        # Corners
        cv2.line(img, (margin, margin), (margin + 50, margin), color_main, thickness)
        cv2.line(img, (margin, margin), (margin, margin + 50), color_main, thickness)
        
        cv2.line(img, (w - margin, margin), (w - margin - 50, margin), color_main, thickness)
        cv2.line(img, (w - margin, margin), (w - margin, margin + 50), color_main, thickness)
        
        cv2.line(img, (margin, h - margin), (margin + 50, h - margin), color_main, thickness)
        cv2.line(img, (margin, h - margin), (margin, h - margin - 50), color_main, thickness)
        
        cv2.line(img, (w - margin, h - margin), (w - margin - 50, h - margin), color_main, thickness)
        cv2.line(img, (w - margin, h - margin), (w - margin, h - margin - 50), color_main, thickness)

        # 2. Header Status
        c_time = time.time()
        self.fps = 1 / (c_time - self.p_time) if (c_time - self.p_time) > 0 else 0
        self.p_time = c_time
        
        cv2.rectangle(img, (30, 30), (450, 70), (20, 20, 20), -1)
        cv2.putText(img, f"GESTURA PRO v1.0 | LIVE FEED", (45, 58), self.font, 0.6, (255, 255, 255), 1)
        cv2.putText(img, f"FPS: {int(self.fps)}", (380, 58), self.font, 0.5, color_main, 1)

        # 3. Telemetry Sidebar (Right)
        sidebar_x = w - 280
        cv2.rectangle(img, (sidebar_x, 100), (w - 30, 480), (10, 10, 10), -1) # Taller for diagnostics
        cv2.rectangle(img, (sidebar_x, 100), (w - 30, 480), color_main, 1)
        
        cv2.putText(img, "SPATIAL SYSTEMS", (sidebar_x + 20, 130), self.font, 0.5, color_main, 2)
        cv2.line(img, (sidebar_x + 20, 140), (w - 50, 140), (50, 50, 50), 1)
        
        # Telemetry Values
        self._draw_value_with_bar(img, "SCALE", obj_state['scale'], 0, 5, sidebar_x + 20, 175)
        self._draw_value_with_bar(img, "ANGLE", obj_state['angle'], 0, 360, sidebar_x + 20, 215)
        self._draw_value_with_bar(img, "POS-X", obj_state['pos'][0], 0, w, sidebar_x + 20, 255)
        self._draw_value_with_bar(img, "POS-Y", obj_state['pos'][1], 0, h, sidebar_x + 20, 295)

        # 3.1 Interaction Diagnostics (NEW)
        cv2.putText(img, "INTERACTION DIAGNOSTICS", (sidebar_x + 20, 345), self.font, 0.4, color_main, 1)
        cv2.line(img, (sidebar_x + 20, 355), (w - 50, 355), (50, 50, 50), 1)

        # Activity Status Lights
        active_pinching = any("PINCH" in h['gesture'] for h in hands_info)
        active_palm = any("PALM" in h['gesture'] for h in hands_info)
        
        self._draw_status_indicator(img, "PINCH ENGINE", active_pinching, sidebar_x + 20, 385)
        self._draw_status_indicator(img, "RESET SYSTEM", active_palm, sidebar_x + 20, 415)
        self._draw_status_indicator(img, "SIGNAL STABILITY", int(self.fps) > 20, sidebar_x + 20, 445)

        # 4. Hand Info Cards (Left)
        for idx, hand in enumerate(hands_info):
            y_off = 100 + (idx * 300) 
            cv2.rectangle(img, (30, y_off), (350, y_off + 280), (10, 10, 10), -1)
            cv2.rectangle(img, (30, y_off), (350, y_off + 280), color_main, 1)
            
            cv2.putText(img, f"SOURCE: {hand['type'].upper()}", (45, y_off + 30), self.font, 0.5, (180, 180, 180), 1)
            cv2.putText(img, f"GESTURE: {hand['gesture']}", (45, y_off + 60), self.font, 0.5, (255, 255, 255), 1)
            
            # Biometric Telemetry
            cv2.putText(img, "LENGTH | FLEXION", (45, y_off + 95), self.font, 0.4, color_main, 1)
            cv2.line(img, (45, y_off + 105), (320, y_off + 105), (50, 50, 50), 1)
            
            l_off = 135
            if "lengths" in hand and "bentness" in hand:
                for f_name in ["IDX", "MID", "RNG", "PNK"]:
                    l_val = hand["lengths"].get(f_name, 0)
                    b_val = hand["bentness"].get(f_name, 0)
                    
                    # Label
                    cv2.putText(img, f_name, (45, y_off + l_off), self.font, 0.4, (200, 200, 200), 1)
                    
                    # Length Bar (Cyan)
                    l_w = 100
                    cv2.rectangle(img, (90, y_off + l_off - 8), (90 + l_w, y_off + l_off - 3), (40, 40, 40), -1)
                    cv2.rectangle(img, (90, y_off + l_off - 8), (90 + int(l_w * min(1, l_val/2)), y_off + l_off - 3), color_main, -1)
                    
                    # Flexion Bar (Magenta/Purple for contrast)
                    f_w = 100
                    cv2.rectangle(img, (210, y_off + l_off - 8), (210 + f_w, y_off + l_off - 3), (40, 40, 40), -1)
                    cv2.rectangle(img, (210, y_off + l_off - 8), (210 + int(f_w * b_val), y_off + l_off - 3), (255, 0, 255), -1)
                    
                    l_off += 35

    def _draw_status_indicator(self, img, label, is_active, x, y):
        """Draws a professional status light (Green for active, Dim for inactive)."""
        color = (0, 255, 0) if is_active else (50, 50, 50)
        cv2.circle(img, (x + 10, y - 5), 6, color, -1)
        cv2.putText(img, label, (x + 30, y), self.font, 0.4, (200, 200, 200), 1)

    def _draw_value_with_bar(self, img, label, val, min_v, max_v, x, y, bar_w=150):
        cv2.putText(img, f"{label}: {val:.2f}" if isinstance(val, float) else f"{label}: {int(val)}", (x, y), self.font, 0.4, (200, 200, 200), 1)
        pct = (val - min_v) / (max_v - min_v) if max_v != min_v else 0
        pct = max(0, min(1, pct))
        cv2.rectangle(img, (x, y + 5), (x + bar_w, y + 10), (50, 50, 50), -1)
        cv2.rectangle(img, (x, y + 5), (x + int(bar_w * pct), y + 10), (0, 255, 255), -1)

    def draw_object(self, img, state):
        """Professional 3D glass-cube rendering with glowing edges."""
        cx, cy = int(state['pos'][0]), int(state['pos'][1])
        s = state['scale'] * 120
        a = np.radians(state['angle'])
        
        pts = np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],
                        [-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]]) * s
        
        # Sophisticated Rotation (Multi-Axis)
        rot_z = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
        rot_x = np.array([[1, 0, 0], [0, np.cos(0.3), -np.sin(0.3)], [0, np.sin(0.3), np.cos(0.3)]])
        
        projected = []
        for p in pts:
            r = np.dot(p, rot_z.T)
            r = np.dot(r, rot_x.T)
            z = r[2] + s * 5
            f = 600 / z if z != 0 else 1
            px = int(r[0] * f) + cx
            py = int(r[1] * f) + cy
            projected.append((px, py))
            
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        
        # Glow layer
        overlay = img.copy()
        for s_idx, e_idx in edges:
            cv2.line(overlay, projected[s_idx], projected[e_idx], (0, 255, 255), 8)
        cv2.addWeighted(overlay, 0.2, img, 0.8, 0, img)
        
        # Core edges
        for s_idx, e_idx in edges:
            cv2.line(img, projected[s_idx], projected[e_idx], (255, 255, 255), 2)
        
        # Center marker
        cv2.drawMarker(img, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 20, 1)



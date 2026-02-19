import cv2
import numpy as np

class CanvasManager:
    """Manages spatial drawing, shape recognition, and object manipulation."""
    
    def __init__(self):
        self.shapes = [] # List of {'type': 'line/rect/circle', 'pts': [], 'color': (), 'selected': bool}
        self.current_path = []
        self.drawing = False
        self.selected_shape_idx = -1
        self.drag_offset = (0, 0)
        
    def start_drawing(self, pos):
        self.drawing = True
        self.current_path = [pos]
        
    def update_drawing(self, pos):
        if self.drawing:
            # Simple distance check to avoid redundant points
            if np.linalg.norm(np.array(pos) - np.array(self.current_path[-1])) > 5:
                self.current_path.append(pos)
                
    def end_drawing(self):
        if not self.drawing or len(self.current_path) < 5:
            self.drawing = False
            return
            
        # Recognize shape
        shape = self._recognize_shape(self.current_path)
        self.shapes.append(shape)
        self.drawing = False
        self.current_path = []

    def _recognize_shape(self, path):
        pts = np.array(path, dtype=np.int32)
        
        # 1. Check for Circle
        center, radius = cv2.minEnclosingCircle(pts)
        circle_area = np.pi * (radius ** 2)
        actual_area = cv2.contourArea(pts)
        
        # Calculate perimeter to check roundness
        perimeter = cv2.arcLength(pts, True)
        roundness = (4 * np.pi * actual_area) / (perimeter ** 2) if perimeter > 0 else 0
        
        if roundness > 0.7:
            return {'type': 'circle', 'center': (int(center[0]), int(center[1])), 'radius': int(radius), 'selected': False}
            
        # 2. Check for Rectangle
        rect = cv2.minAreaRect(pts)
        box = cv2.boxPoints(rect)
        box = np.int32(box)
        rect_area = rect[1][0] * rect[1][1]
        if actual_area / rect_area > 0.7:
            return {'type': 'rect', 'box': box, 'center': (int(rect[0][0]), int(rect[0][1])), 'selected': False}
            
        # Default to Line
        return {'type': 'line', 'pts': pts, 'center': (int(np.mean(pts[:,0])), int(np.mean(pts[:,1]))), 'selected': False}

    def select_at(self, pos):
        self.selected_shape_idx = -1
        for i, shape in enumerate(reversed(self.shapes)):
            idx = len(self.shapes) - 1 - i
            dist = np.linalg.norm(np.array(pos) - np.array(shape['center']))
            if dist < 50: # Selection radius
                self.selected_shape_idx = idx
                self.shapes[idx]['selected'] = True
                self.drag_offset = (shape['center'][0] - pos[0], shape['center'][1] - pos[1])
                return True
        return False

    def drag(self, pos):
        if self.selected_shape_idx != -1:
            s = self.shapes[self.selected_shape_idx]
            dx = (pos[0] + self.drag_offset[0]) - s['center'][0]
            dy = (pos[1] + self.drag_offset[1]) - s['center'][1]
            
            s['center'] = (s['center'][0] + dx, s['center'][1] + dy)
            if s['type'] == 'circle':
                s['center'] = (s['center'][0], s['center'][1])
            elif s['type'] == 'rect':
                s['box'] += [dx, dy]
            elif s['type'] == 'line':
                s['pts'] += [dx, dy]

    def clear(self):
        self.shapes = []
        self.selected_shape_idx = -1

    def draw(self, img):
        # Draw permanent shapes
        for i, s in enumerate(self.shapes):
            color = (0, 255, 0) if s['selected'] else (0, 255, 255)
            thickness = 3 if s['selected'] else 2
            
            if s['type'] == 'circle':
                cv2.circle(img, s['center'], s['radius'], color, thickness)
            elif s['type'] == 'rect':
                cv2.drawContours(img, [s['box']], 0, color, thickness)
            elif s['type'] == 'line':
                cv2.polylines(img, [s['pts']], False, color, thickness)
        
        # Draw current path
        if self.drawing and len(self.current_path) > 1:
            cv2.polylines(img, [np.array(self.current_path, np.int32)], False, (255, 255, 255), 2)

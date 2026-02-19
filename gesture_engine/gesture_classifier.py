import numpy as np
from hand_tracking.landmarks import LandmarkIndex as LI
from utils.math_helpers import calculate_distance, calculate_angle
from utils.config import Config

class GestureClassifier:
    """Production-grade gesture classification for spatial interaction."""
    
    @staticmethod
    def is_pinch(lm_list):
        """Returns (bool, float) for pinch state and normalized distance."""
        if not lm_list: return False, 0
        
        thumb_tip = np.array([lm_list[LI.THUMB_TIP][1], lm_list[LI.THUMB_TIP][2]])
        index_tip = np.array([lm_list[LI.INDEX_FINGER_TIP][1], lm_list[LI.INDEX_FINGER_TIP][2]])
        
        # Normalize by hand scale (Wrist to Middle MCP)
        wrist = np.array([lm_list[LI.WRIST][1], lm_list[LI.WRIST][2]])
        middle_mcp = np.array([lm_list[LI.MIDDLE_FINGER_MCP][1], lm_list[LI.MIDDLE_FINGER_MCP][2]])
        hand_scale = np.linalg.norm(wrist - middle_mcp)
        
        dist = np.linalg.norm(thumb_tip - index_tip)
        normalized_dist = dist / hand_scale if hand_scale > 0 else 1.0
        
        return normalized_dist < Config.PINCH_THRESHOLD, normalized_dist

    @staticmethod
    def is_pointing(lm_list):
        """Detects if only the index finger is extended."""
        if not lm_list: return False
        
        # Extended index
        index_tip = lm_list[LI.INDEX_FINGER_TIP][2]
        index_pip = lm_list[LI.INDEX_FINGER_PIP][2]
        
        # Others curled
        other_tips = [LI.MIDDLE_FINGER_TIP, LI.RING_FINGER_TIP, LI.PINKY_TIP]
        other_pips = [LI.MIDDLE_FINGER_PIP, LI.RING_FINGER_PIP, LI.PINKY_PIP]
        
        # Check index up
        if index_tip < index_pip:
            # Check others down
            for tip, pip in zip(other_tips, other_pips):
                if lm_list[tip][2] < lm_list[pip][2]:
                    return False
            return True
        return False

    @staticmethod
    def is_open_palm(lm_list):
        """Detects full open palm state for system reset."""
        if not lm_list: return False
        
        # Check if all four fingers are extended above their PIP joints
        finger_tips = [LI.INDEX_FINGER_TIP, LI.MIDDLE_FINGER_TIP, LI.RING_FINGER_TIP, LI.PINKY_TIP]
        finger_pips = [LI.INDEX_FINGER_PIP, LI.MIDDLE_FINGER_PIP, LI.RING_FINGER_PIP, LI.PINKY_PIP]
        
        extended = 0
        for tip, pip in zip(finger_tips, finger_pips):
            if lm_list[tip][2] < lm_list[pip][2]: # Y-up is negative in image space
                extended += 1
        
        return extended >= 4

    @staticmethod
    def get_finger_bentness(lm_list):
        """Calculates how much each finger is curled (0 = straight, 1 = curled)."""
        if not lm_list: return {}
        
        fingers = {
            "IDX": [LI.INDEX_FINGER_MCP, LI.INDEX_FINGER_PIP, LI.INDEX_FINGER_TIP],
            "MID": [LI.MIDDLE_FINGER_MCP, LI.MIDDLE_FINGER_PIP, LI.MIDDLE_FINGER_TIP],
            "RNG": [LI.RING_FINGER_MCP, LI.RING_FINGER_PIP, LI.RING_FINGER_TIP],
            "PNK": [LI.PINKY_MCP, LI.PINKY_PIP, LI.PINKY_TIP]
        }
        
        bentness = {}
        for name, ids in fingers.items():
            # Angle at the PIP joint
            p1 = np.array([lm_list[ids[0]][1], lm_list[ids[0]][2]])
            p2 = np.array([lm_list[ids[1]][1], lm_list[ids[1]][2]])
            p3 = np.array([lm_list[ids[2]][1], lm_list[ids[2]][2]])
            
            v1 = p1 - p2
            v2 = p3 - p2
            
            angle = np.degrees(np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))))
            # Map 180 deg (straight) to 0, 0 deg (curled) to 1
            bentness[name] = max(0, min(1, (180 - angle) / 150))
            
        return bentness

    @staticmethod
    def get_finger_lengths(lm_list):
        """Calculates normalized lengths of all 5 fingers."""
        if not lm_list: return {}
        
        # Reference scale: Wrist-to-MiddleMCP distance
        wrist = np.array([lm_list[LI.WRIST][1], lm_list[LI.WRIST][2]])
        mcp_mid = np.array([lm_list[LI.MIDDLE_FINGER_MCP][1], lm_list[LI.MIDDLE_FINGER_MCP][2]])
        scale = np.linalg.norm(wrist - mcp_mid)
        if scale == 0: scale = 1.0

        # Finger joint chains
        fingers = {
            "THM": [LI.WRIST, LI.THUMB_CMC, LI.THUMB_MCP, LI.THUMB_IP, LI.THUMB_TIP],
            "IDX": [LI.INDEX_FINGER_MCP, LI.INDEX_FINGER_PIP, LI.INDEX_FINGER_DIP, LI.INDEX_FINGER_TIP],
            "MID": [LI.MIDDLE_FINGER_MCP, LI.MIDDLE_FINGER_PIP, LI.MIDDLE_FINGER_DIP, LI.MIDDLE_FINGER_TIP],
            "RNG": [LI.RING_FINGER_MCP, LI.RING_FINGER_PIP, LI.RING_FINGER_DIP, LI.RING_FINGER_TIP],
            "PNK": [LI.PINKY_MCP, LI.PINKY_PIP, LI.PINKY_DIP, LI.PINKY_TIP]
        }

        lengths = {}
        for name, ids in fingers.items():
            dist = 0
            for i in range(len(ids) - 1):
                p1 = np.array([lm_list[ids[i]][1], lm_list[ids[i]][2]])
                p2 = np.array([lm_list[ids[i+1]][1], lm_list[ids[i+1]][2]])
                dist += np.linalg.norm(p1 - p2)
            lengths[name] = dist / scale

        return lengths

    @staticmethod
    def get_spatial_state(lm_list):
        """Returns the 3D orientation and center point of the hand."""
        if not lm_list: return 0, (0, 0)
        
        wrist = np.array([lm_list[LI.WRIST][1], lm_list[LI.WRIST][2]])
        index_mcp = np.array([lm_list[LI.INDEX_FINGER_MCP][1], lm_list[LI.INDEX_FINGER_MCP][2]])
        
        # Rotation angle calculated from wrist to index base
        angle = np.degrees(np.arctan2(index_mcp[1] - wrist[1], index_mcp[0] - wrist[0])) + 90
        
        # Center of the hand
        center = (int((wrist[0] + index_mcp[0]) / 2), int((wrist[1] + index_mcp[1]) / 2))
        
        return angle % 360, center


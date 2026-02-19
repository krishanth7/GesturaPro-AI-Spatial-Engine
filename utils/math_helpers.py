import numpy as np

def calculate_distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_angle(p1, p2):
    """Calculate angle of a line between two points in degrees."""
    return np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))

def normalize_value(val, min_val, max_val):
    """Normalize value between 0 and 1."""
    return (val - min_val) / (max_val - min_val) if max_val != min_val else 0

def clamp(val, min_val, max_val):
    """Clamp value between min and max."""
    return max(min(val, max_val), min_val)

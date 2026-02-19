# GESTURA PRO: Industrial AI Spatial Interaction Engine

**Gestura Pro** is an enterprise-grade spatial computing engine that transforms standard RGB camera feeds into high-precision 3D interaction environments. By utilizing advanced computer vision and recursive signal filtering, it enables fluid, zero-latency manipulation of digital assets and spatial CAD interaction.

---

## Technical Specifications

### Spatial CAD and Shape Synthesis
The system features a professional geometric interaction layer for real-time drafting:
- **AI Shape Recognition**: Hand-drawn paths are automatically synthesized into perfect geometric primitives (Circles, Rectangles, Lines) using contour analysis.
- **Interactive Drag and Drop**: Select and relocate spatial entities using high-precision pinch gestures.
- **Zero-Latency Manipulation**: Physics-based translation of shapes across the interaction plane.

### Clinical Biometric Analysis
The engine provides high-precision physiological tracking for hardware-level telemetry:
- **Normalized Finger Lengths**: Real-time statistical analysis of phalangeal segments.
- **Dynamic Flexion (Bentness)**: Calculation of interphalangeal joint angles (0.0 straight to 1.0 curled).
- **Temporal Stability**: Integrated MediaPipe Video Context for jitter-free skeletal tracking.

### Industrial HUD and Telemetry
A mission-critical interface designed for professional diagnostics:
- **Interaction Diagnostics**: Real-time status indicators for PINCH ENGINE, RESET SYSTEM, and SIGNAL STABILITY.
- **Biometric Dashboard**: Side-by-side bar telemetry for Finger Length and Flexion levels.
- **Digital Framing**: Cyber-industrial border with lock-on tracking indicators.

---

## Command Gesture Matrix

*The system uses a deterministic state-machine for fluid environment control.*

- **☝️ DRAW (Pointing)**: Active spatial sketching with the index finger.
- **👌 DRAG (Pinching)**: Entity selection and 3D translation.
- **✋ CLEAR (Open Palm)**: Global system reset and canvas erasure.

---

## Modular Architecture

| Module | Responsibility |
| :--- | :--- |
| `hand_tracking` | High-LOD landmark extraction via Tasks API. |
| `gesture_engine` | Neural-to-Mechanical gesture classification & Biometrics. |
| `canvas_manager` | AI Shape synthesis, recognition, and entity manipulation. |
| `ui` | 3D Projection, Industrial HUD & Real-time Telemetry. |

---

## Deployment

1. **Environmental Setup**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch Engine**:
   ```bash
   python main.py
   ```

---

## Configuration Specs (config.yaml)
Fine-tune system behavior for specific lighting and hardware:
- **CAMERA_ID**: I/O port for the capture device.
- **KALMAN_Q/R**: Tuning for the recursive noise-reduction algorithm.
- **MIN_DETECTION_CONFIDENCE**: AI detection floor (set to 0.5 for high sensitivity).

---
*Gestura Pro: The professional standard for AI-based human-machine interaction.*

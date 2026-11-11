# Exercise Tracker

Tracks your body through the webcam with [MediaPipe Pose](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker), draws your skeleton on the live video, and shows the angle of each major joint (elbows, shoulders, hips, knees, ankles) in degrees.

## Files

| File | What it does |
|------|--------------|
| `main.py` | Runs the program: reads the webcam, detects the pose, draws the skeleton and joint angles |
| `joint_calculations.py` | Vector math, including `jointAngle(a, b, c)`, which returns the angle at point `b` |
| `pose_landmarker_lite.task` | The MediaPipe pose model that `main.py` loads |

## Setup (once)

MediaPipe needs Python 3.12 or older. With Anaconda:

```bash
conda create -n tracker python=3.12 -y
conda activate tracker
pip install -r requirements.txt
```

## Run

From inside this folder:

```bash
conda activate tracker
python main.py
```

- Allow camera access if macOS asks (System Settings → Privacy & Security → Camera).
- Press the **spacebar** in the video window to quit.

To check the angle math without a camera: `python joint_calculations.py` (prints `ok`).

## How the angles work

Each joint is three landmarks, A–B–C, and the angle is measured at B. For example, the elbow angle uses shoulder–elbow–wrist: 180° means the arm is straight.

The angles use MediaPipe's **world landmarks** (real 3D positions in meters), not the on-screen points. That way the angle doesn't depend on the image shape or which way you're facing the camera.

The joints are listed in `JOINTS` at the top of `main.py`. To measure another joint, add a line there, and its angle shows up in the `angles` dict each frame (e.g. `angles["right knee"]`).

### Landmark numbers

The numbers in `JOINTS` are MediaPipe's landmark indices:

| Body part | Left (MediaPipe) | Right (MediaPipe) |
|-----------|-----:|------:|
| Shoulder  | 11 | 12 |
| Elbow     | 13 | 14 |
| Wrist     | 15 | 16 |
| Hip       | 23 | 24 |
| Knee      | 25 | 26 |
| Ankle     | 27 | 28 |
| Foot tip  | 31 | 32 |

0–10 are on the face (not drawn). The video is mirrored before detection, so MediaPipe's "left" landmarks are on **your right** side. That's why `JOINTS` calls 11–13–15 the "right elbow".

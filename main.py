"""
Exercise Tracker: live pose tracking from the webcam.

Draws the body skeleton on the camera feed and writes the angle (in degrees)
of each major joint next to it. Press the SPACEBAR to quit.
"""

import time

import cv2
import mediapipe as mp

from joint_calculations import jointAngle


# MediaPipe model file (must sit in the folder you run the program from)
MODEL_PATH = "pose_landmarker_lite.task"

# Landmarks 0-10 are on the face; we don't draw them
FACE_LANDMARKS = set(range(11))

# Joints to measure: name -> (point A, joint B, point C); the angle is measured at B.
# Numbers are MediaPipe pose landmark indices (see README).
# The frame is mirrored before detection, so MediaPipe's "left" (odd) indices are the user's right side.
JOINTS = {
    "right elbow":    (11, 13, 15),
    "left elbow":     (12, 14, 16),
    "right shoulder": (13, 11, 23),
    "left shoulder":  (14, 12, 24),
    "right hip":      (11, 23, 25),
    "left hip":       (12, 24, 26),
    "right knee":     (23, 25, 27),
    "left knee":      (24, 26, 28),
    "right ankle":    (25, 27, 31),
    "left ankle":     (26, 28, 32),
}

# Joints MediaPipe is less sure about than this aren't labelled (their angle would be noise)
MIN_VISIBILITY = 0.5

# Pairs of landmarks that form the skeleton lines
SKELETON = mp.tasks.vision.PoseLandmarksConnections.POSE_LANDMARKS


# Set up the pose detector for a video stream, tracking one person
options = mp.tasks.vision.PoseLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    num_poses=1,
)

camera = cv2.VideoCapture(0)

with mp.tasks.vision.PoseLandmarker.create_from_options(options) as landmarker:

    start_time = time.monotonic()

    while camera.isOpened():

        success, frame = camera.read()
        if not success:
            print("Could not access camera")
            break

        # Mirror the image so it behaves like a mirror for the user
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # MediaPipe expects RGB; OpenCV gives BGR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Video mode needs an increasing timestamp for each frame
        timestamp_ms = int((time.monotonic() - start_time) * 1000)
        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        if result.pose_landmarks:

            # Screen landmarks: x, y are 0-1 fractions of the image width/height (used for drawing)
            pose_landmarks = result.pose_landmarks[0]

            # World landmarks: real 3D positions in meters (used for angles, so they
            # don't depend on the image's aspect ratio or which way the person faces)
            world_landmarks = result.pose_world_landmarks[0]

            # Angle of every joint in JOINTS, e.g. angles["right knee"]
            angles = {
                name: jointAngle(world_landmarks[a], world_landmarks[b], world_landmarks[c])
                for name, (a, b, c) in JOINTS.items()
            }

            # Green skeleton lines
            for connection in SKELETON:
                if connection.start in FACE_LANDMARKS or connection.end in FACE_LANDMARKS:
                    continue
                start = pose_landmarks[connection.start]
                end = pose_landmarks[connection.end]
                cv2.line(frame,
                         (int(start.x * w), int(start.y * h)),
                         (int(end.x * w), int(end.y * h)),
                         (0, 255, 0), 2)

            # Red dot on each body landmark
            for i, landmark in enumerate(pose_landmarks):
                if i in FACE_LANDMARKS:
                    continue
                cv2.circle(frame, (int(landmark.x * w), int(landmark.y * h)), 5, (0, 0, 255), -1)

            # White angle label next to each joint
            for name, (a, b, c) in JOINTS.items():
                joint = pose_landmarks[b]
                if joint.visibility < MIN_VISIBILITY:
                    continue
                cv2.putText(frame, f"{angles[name]:.0f}",
                            (int(joint.x * w) + 10, int(joint.y * h)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Exercise Tracker - Pose Tracking", frame)

        # Press SPACEBAR to quit
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

camera.release()
cv2.destroyAllWindows()

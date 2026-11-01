import cv2
import mediapipe as mp
import time

#Load Mediapipe Landmarks

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options = BaseOptions(
        model_asset_path = "pose_landmarker_lite.task"
    ),
    running_mode = RunningMode.VIDEO,
    num_poses = 1
)

camera = cv2.VideoCapture(0)

with PoseLandmarker.create_from_options(options) as landmarker:

    while camera.isOpened():

        success, frame = camera.read()

        if not success:
            print("Could not access camera")
            break

        #Flips the camera to mirror view
        frame = cv2.flip(frame,1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        timestamp_ms = int(
            camera.get(cv2.CAP_PROP_POS_MSEC)
        )

        if 'start_time' not in globals():
            start_time = time.monotonic()

        timestamp_ms = int((time.monotonic() - start_time) * 1000)

        result = landmarker.detect_for_video(
            mp_image, timestamp_ms
        )

        if result.pose_landmarks:

            pose_landmarks = result.pose_landmarks[0]

            connections = mp.tasks.vision.PoseLandmarksConnections.POSE_LANDMARKS

            for connection in connections:

                start = pose_landmarks[connection.start]
                end = pose_landmarks[connection.end]

                h,w, _ = frame.shape

                x1, y1 = int(start.x * w), int(start.y * h)
                x2, y2 = int(end.x * w), int(end.y * h)

                cv2.line(
                    frame, (x1,y1), (x2, y2),
                    (0,255,0), 2
                )

            for landmark in pose_landmarks:

                h,w, _ = frame.shape

                x = int(landmark.x * w)
                y = int(landmark.y * h)

                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

        cv2.imshow("Rehab Monitor - Pose Tracking", frame)

        # Press Q to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

camera.release()
cv2.destroyAllWindows()


import cv2
import mediapipe as mp
import time

from joint_calculations import jointAngle


#Load Mediapipe Landmarks

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode


# Configure the pose detector:
options = PoseLandmarkerOptions(
    base_options = BaseOptions(
        model_asset_path = "pose_landmarker_lite.task"
    ),
    running_mode = RunningMode.VIDEO,
    num_poses = 1
)

#Initalize the computer's camera
camera = cv2.VideoCapture(0)

#numeric values of body landmarks on the face
face_landmarks = [0,1,2,3,4,5,6,7,8,9,10]

# joint name: (point A, joint B, point C) -> angle measured at B
# The frame is mirrored before detection, so MediaPipe's "left" indices (odd) are the user's right side
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


# Create the pose detector using the configuration above
with PoseLandmarker.create_from_options(options) as landmarker:


    start_time = time.monotonic()

    # Continuously capture and process camera frames
    while camera.isOpened():

        # Reads the next camera frame and stores whether it was successful and the image itself
        success, frame = camera.read()

        # Stop the program if the camera fails to provide a frame
        if not success:
            print("Could not access camera")
            break

        #Flips the camera to create a mirror view
        frame = cv2.flip(frame,1)

        # Convert the frame from OpenCV's BGR format to RGB so the MediaPipe can be able to understand it
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #Converts the RGB frame into a MediaPipe compatible image object
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Generate a timestamp for the current frame
        timestamp_ms = int((time.monotonic() - start_time) * 1000)

        # Pass the current image and its timestamp to MediaPipe for pose detection
        result = landmarker.detect_for_video(mp_image, timestamp_ms)


        # Check whether MediaPipe successfully detected any people
        if result.pose_landmarks:

            # Retrieve the body landmarks of the first detected person
            pose_landmarks = result.pose_landmarks[0]

            # World landmarks are real 3D coordinates in meters, so angles don't depend on camera aspect ratio or facing direction
            world_landmarks = result.pose_world_landmarks[0]

            # Angle (degrees) of every joint in JOINTS, e.g. angles["right knee"]
            angles = {
                name: jointAngle(world_landmarks[a], world_landmarks[b], world_landmarks[c])
                for name, (a, b, c) in JOINTS.items()
            }

            # Retrieve the connections that define the human body skeleton
            connections = mp.tasks.vision.PoseLandmarksConnections.POSE_LANDMARKS

            # Loop through all the connections that make up the human body skeleton

            for connection in connections:

                # Retrieve the two landmarks that form the current connection
                start = pose_landmarks[connection.start]
                end = pose_landmarks[connection.end]

                if ((connection.start in face_landmarks) or (connection.end in face_landmarks)):
                    continue

                else:

                    h,w, _ = frame.shape

                    # Convert normalized landmark coordinates into pixel coordinates
                    x1, y1 = int(start.x * w), int(start.y * h)
                    x2, y2 = int(end.x * w), int(end.y * h)

                    # Draw a green line between the two landmarks
                    cv2.line(
                        frame, (x1,y1), (x2, y2),
                        (0,255,0), 2
                    )

            #Loop through all detected body landmarks
            for i, landmark in enumerate(pose_landmarks):

                if (i in face_landmarks):
                    continue

                else:

                    h,w, _ = frame.shape

                    x = int(landmark.x * w)
                    y = int(landmark.y * h)

                    # Draw a red circle at the landmark's position
                    cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

            # Write each joint's angle next to the joint (skip joints MediaPipe can't see well)
            for name, (a, b, c) in JOINTS.items():
                joint = pose_landmarks[b]
                if joint.visibility < 0.5:
                    continue
                x, y = int(joint.x * w), int(joint.y * h)
                cv2.putText(frame, f"{angles[name]:.0f}", (x + 10, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        #Displays the camera frame with the drawn skeleton
        cv2.imshow("Exercise Tracker - Pose Tracking", frame)

        # Press Q to exit from the program
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

#closes window
camera.release()
cv2.destroyAllWindows()


from collections import deque

# Determines the direction of an arm curl by tracking changes in the elbow angle over time.
class CurlTracker:

    def __init__(
        self,
        smoothing=0.3,        # Controls how much each new angle affects the smoothed angle
        window_s=0.4,         # Time window used to measure angle changes
        start_speed=8.0,      # Minimum speed needed to detect a movement
        stop_speed=3.0,       # Speed at which an ongoing movement is considered stopped
        confirm_frames=3,     # Number of frames needed to confirm a state change
    ):
        self.smoothing = smoothing
        self.window_s = window_s
        self.start_speed = start_speed
        self.stop_speed = stop_speed
        self.confirm_frames = confirm_frames

        self.smoothed = None
        self.history = deque()  # (time_seconds, smoothed_angle)
        self.state = "Holding"
        self._candidate = "Holding"
        self._candidate_count = 0

    def update(self, angle, t):
        #Function that updates the movement state using the current elbow angle and time

        # Smooth out sudden changes in the elbow angle to prevent inaccurate results
        if self.smoothed is None:
            self.smoothed = angle
        else:
            self.smoothed += self.smoothing * (angle - self.smoothed)

        # Store the latest angle and remove old measurements
        self.history.append((t, self.smoothed))
        while len(self.history) > 2 and t - self.history[1][0] >= self.window_s:
            self.history.popleft()

        # Calculate how quickly the elbow angle is changing
        t0, a0 = self.history[0]
        dt = t - t0
        if dt < 0.1:  # not enough data yet
            return self.state

        # Positive speed = angle increasing = arm extending
        speed = (self.smoothed - a0) / dt

        # Determine whether the arm is raising, lowering or holding
        if speed < -self.start_speed:
            target = "Raising"
        elif speed > self.start_speed:
            target = "Lowering"
        elif self.state == "Raising" and speed < -self.stop_speed:
            target = "Raising"      # already raising, keep going at lower speed
        elif self.state == "Lowering" and speed > self.stop_speed:
            target = "Lowering"
        else:
            target = "Holding"

        # Confirm the new state before changing the current one
        if target == self.state:
            self._candidate = target
            self._candidate_count = 0
        elif target == self._candidate:
            self._candidate_count += 1
            if self._candidate_count >= self.confirm_frames:
                self.state = target
                self._candidate_count = 0
        else:
            self._candidate = target
            self._candidate_count = 1

        return self.state
    

# Counts completed dumbbell curl repetitions and monitors elbow angles
# to help assess whether the exercise is being performed correctly.

class RepCounter:

    def __init__(self):
        self.state = "Waiting"  # Current stage of the curl
        self.reps = 0           # Number of completed repetitions


    def countRep(self, movement, angle):

        # Ignore the update if angle or movement data is missing
        if movement is None or angle is None:
            return self.reps

        if self.state == "Waiting":

            # Wait until the arm is fully extended before tracking a curl
            if angle > 160:
                self.state = "Bottom"

        elif self.state == "Bottom":

            # Detect when the arm starts curling upward
            if movement == "Raising":
                self.state = "Raising"

        elif self.state == "Raising":

            # Confirm the arm has reached the top of the curl
            if angle < 50:
                self.state = "Top"

        elif self.state == "Top":

            # Detect when the arm starts lowering
            if movement == "Lowering":
                self.state = "Lowering"

        elif self.state == "Lowering":

            # Count the rep once the arm returns to the extended position
            if angle > 160:
                self.state = "Bottom"
                self.reps += 1

        return self.reps #Returns the reps
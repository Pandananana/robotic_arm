import cv2
import numpy as np
import mediapipe as mp
from main import INITIAL_POSITION, BASE_HEIGHT, goToCoordinates, goToStart
import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# Define the function to be called when the button is clicked
ready = False
def button_click():
    global ready 
    global params
    ready = True
    coordinates = find_coordinates(midpoints, INITIAL_POSITION, params['sensor_width_pixels'], params['sensor_height_pixels'], params['fov_x'], params['fov_y'])
    plot_coordinates(coordinates)
    goToCoordinates(coordinates)

def plot_coordinates(coordinates):
    x = [coord[0] for coord in coordinates]
    y = [coord[1] for coord in coordinates]
    plt.scatter(x, y)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Computed Coordinates')
    plt.show()

def find_coordinates(midpoints, camera_pos, w, h, fov_x, fov_y):
    # Calculate the distance from the camera to the image plane
    camera_height = camera_pos[2] + BASE_HEIGHT

    # Calculate the center of the image
    center_x = w / 2
    center_y = h / 2
    center_position = INITIAL_POSITION - np.array([0, 0, camera_height])

    # Calculate the FOV in radians
    fov_x_rad = np.deg2rad(fov_x)
    fov_y_rad = np.deg2rad(fov_y)

    # Calculate pixels per radian
    px_per_rad_x = w / fov_x_rad
    px_per_rad_y = h / fov_y_rad

    # Create empty list to store the calculated coordinates
    coordinates = []

    for point in midpoints:
        pixel_x = point[0] * w
        pixel_y = point[1] * h

        delta_x = pixel_x - center_x
        delta_y = pixel_y - center_y
        
        # Convert pixel differences to angles
        angle_h = delta_x / px_per_rad_x
        angle_v = delta_y / px_per_rad_y
        
        # Calculate distances on table using tangent
        # For small angles, tan(θ) ≈ θ, but we'll use tan for accuracy
        x_relative = camera_height * np.tan(angle_h)
        y_relative = camera_height * np.tan(angle_v)

        # Calculate the absolute coordinates
        # x and y are swapped because of the camera orientation
        x = center_position[0] - y_relative
        y = center_position[1] - x_relative
        z = 0

        print(f"X: {x}, Y: {y}")
        coordinates.append((x, y, z))

    return coordinates

midpoints = []
cap = None
def process_video():
    # Global variables
    global cap

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils

    # Stream video from DroidCam app
    droid_cam_url = "http://192.168.86.26:4747/video"
    cap = cv2.VideoCapture("/dev/video4")
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    print("Starting camera loop")

    # Define button properties
    button_position = (0, 0)
    button_size = (100, 50)
    button_color = (0, 0, 0)
    button_text = "Ready"

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if button_position[0] <= x <= button_position[0] + button_size[0] and button_position[1] <= y <= button_position[1] + button_size[1]:
                button_click()

    cv2.namedWindow('Hand Points')
    cv2.setMouseCallback('Hand Points', mouse_callback)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe Hands
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw all landmarks on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Find the midpoints between the finger dip joints
                finger_dip_joint = [hand_landmarks.landmark[i] for i in [2, 7, 11, 15, 19]]

                global midpoints
                midpoints = []
                for i in range(len(finger_dip_joint) - 1):
                    x1, y1 = finger_dip_joint[i].x, finger_dip_joint[i].y
                    x2, y2 = finger_dip_joint[i+1].x, finger_dip_joint[i+1].y
                    midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)
                    midpoints.append(midpoint)

                h, w, _ = frame.shape
                for point in midpoints:
                    cv2.circle(frame, (int(point[0] * w), int(point[1] * h)), 5, (255, 100, 0), -1)

        # Draw the button on the frame
        cv2.rectangle(frame, button_position, (button_position[0] + button_size[0], button_position[1] + button_size[1]), button_color, -1)
        cv2.putText(frame, button_text, (button_position[0] + 10, button_position[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Display the frame
        cv2.imshow('Hand Points', frame)

        # Break the loop when 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def load_camera_params(filepath='camera_params.txt'):
    params = {}
    with open(filepath, 'r') as f:
        for line in f:
            # Split each line at the equals sign
            key, value = line.strip().split('=')
            # Convert value to float (all our parameters are numeric)
            params[key] = float(value)
    return params

params = {}
def main():
    global params
    params = load_camera_params()

    goToStart()

    process_video()

if __name__ == "__main__":
    main()
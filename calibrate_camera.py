import numpy as np
import cv2
import os
import time
from datetime import datetime

def calibrate_camera(images_paths, checkerboard_size=(10,7), square_size_mm=25):
    """
    Calibrate camera using checkerboard images to find focal length.
    
    Args:
        images_paths (list): List of paths to checkerboard images
        checkerboard_size (tuple): Number of inner corners (width, height)
        square_size_mm (float): Size of each square in millimeters
    
    Returns:
        tuple: (fx_pixels, fy_pixels, fx_mm, fy_mm) focal lengths in pixels and millimeters
    """
    # Prepare object points
    objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
    
    if square_size_mm:
        # Use actual measurements (in mm)
        objp[:,:2] = np.mgrid[0:checkerboard_size[0], 0:checkerboard_size[1]].T.reshape(-1,2) * square_size_mm
    else:
        # Use unit measurements (1 unit = 1 square)
        objp[:,:2] = np.mgrid[0:checkerboard_size[0], 0:checkerboard_size[1]].T.reshape(-1,2)
    
    objpoints = []
    imgpoints = []
    
    for image_path in images_paths:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)
        
        if ret:
            objpoints.append(objp)
            imgpoints.append(corners)
            
            # Draw corners for visualization
            cv2.drawChessboardCorners(img, checkerboard_size, corners, ret)
            cv2.imshow('Checkerboard Corners', img)
            cv2.waitKey(500)
    
    cv2.destroyAllWindows()
    
    # Calibrate camera
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )
    
    # Extract focal lengths in pixels
    fx_pixels = mtx[0,0]
    fy_pixels = mtx[1,1]

    # Get sensor size in pixels
    sensor_width_pixels = gray.shape[1]
    sensor_height_pixels = gray.shape[0]

    # Find field of view
    fov_x = np.rad2deg(2 * np.arctan2(sensor_width_pixels, 2 * fx_pixels))
    fov_y = np.rad2deg(2 * np.arctan2(sensor_height_pixels, 2 * fy_pixels))
    
    # Calculate focal lengths in millimeters (if square size is provided)
    if square_size_mm:      
        # Convert focal length to millimeters
        fx_mm = (fx_pixels * square_size_mm) / (checkerboard_size[0] - 1)
        fy_mm = (fy_pixels * square_size_mm) / (checkerboard_size[1] - 1)
        
        return fov_x, fov_y, sensor_width_pixels, sensor_height_pixels, fx_pixels, fy_pixels, fx_mm, fy_mm
    
    return fov_x, fov_y, sensor_width_pixels, sensor_height_pixels, fx_pixels, fy_pixels, None, None

def capture_calibration_images(output_folder="calibration_images", checkerboard_size=(10,7), frame_rate=10):
    """
    Capture images from webcam for camera calibration.
    Space: Take picture
    ESC: Exit capture mode
    
    Args:
        output_folder (str): Folder to save calibration images
        checkerboard_size (tuple): Number of inner corners (width, height)
    
    Returns:
        list: Paths to captured images
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Initialize camera
    droid_cam_url = "http://192.168.86.26:4747/video"
    webcam_url = "/dev/video4"
    cap = cv2.VideoCapture(webcam_url)
    if not cap.isOpened():
        print("Camera not available. Using existing images from folder.")
        return [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith('.jpg')]
    
    image_paths = []
    image_count = 0
    
    print("Press SPACE to capture image")
    print("Press ESC to finish capturing")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        # Create copy for visualization
        display_frame = frame.copy()
        
        # Try to find checkerboard corners
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret_chess, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)
        
        # If found, draw corners
        if ret_chess:
            cv2.drawChessboardCorners(display_frame, checkerboard_size, corners, ret_chess)
            cv2.putText(display_frame, "Checkerboard Detected!", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(display_frame, "No Checkerboard Detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
        # Add instructions to display
        cv2.putText(display_frame, f"Images captured: {image_count}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Camera Calibration Capture', display_frame)
        
        key = cv2.waitKey(1)
        
        # ESC key
        if key == 27:
            break
            
        # Spacebar
        if key == 32:
            # Only save if checkerboard is detected
            if ret_chess:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = os.path.join(output_folder, f"calib_{timestamp}.jpg")
                cv2.imwrite(image_path, frame)
                image_paths.append(image_path)
                image_count += 1
                print(f"Saved image {image_count}")
            else:
                print("No checkerboard detected - image not saved")

        # Delay to reduce frame rate
        time.sleep(1 / frame_rate)
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    
    return image_paths

def save_camera_params(fov_x, fov_y, sensor_width_pixels, sensor_height_pixels, 
                      fx_pixels, fy_pixels, fx_mm=None, fy_mm=None, 
                      filepath='camera_params.txt'):
    """
    Save camera calibration parameters to a text file in an easily parseable format.
    
    Args:
        fov_x (float): Horizontal field of view in degrees
        fov_y (float): Vertical field of view in degrees
        sensor_width_pixels (int): Sensor width in pixels
        sensor_height_pixels (int): Sensor height in pixels
        fx_pixels (float): Horizontal focal length in pixels
        fy_pixels (float): Vertical focal length in pixels
        fx_mm (float, optional): Horizontal focal length in millimeters
        fy_mm (float, optional): Vertical focal length in millimeters
        filepath (str): Path to save the parameters file
    """
    with open(filepath, 'w') as f:
        # Write each parameter on a new line in key=value format
        f.write(f"fov_x={fov_x}\n")
        f.write(f"fov_y={fov_y}\n")
        f.write(f"sensor_width_pixels={sensor_width_pixels}\n")
        f.write(f"sensor_height_pixels={sensor_height_pixels}\n")
        f.write(f"fx_pixels={fx_pixels}\n")
        f.write(f"fy_pixels={fy_pixels}\n")
        
        # Only write mm values if they exist
        if fx_mm is not None:
            f.write(f"fx_mm={fx_mm}\n")
        if fy_mm is not None:
            f.write(f"fy_mm={fy_mm}\n")


def main():
    # Capture calibration images
    print("Starting camera capture for calibration...")
    
    image_paths = capture_calibration_images()
    
    if len(image_paths) < 10:
        print("Warning: Less than 10 images captured. More images recommended for accurate calibration.")
        if len(image_paths) == 0:
            print("No images captured. Exiting...")
            return
    
    # Perform calibration using previously defined function
    print("\nPerforming calibration...")
    fov_x, fov_y, w, h, fx, fy, fx_mm, fy_mm = calibrate_camera(image_paths)  # Using the calibration function from previous example

    # Save camera params
    save_camera_params(fov_x, fov_y, w, h, fx, fy, fx_mm, fy_mm)

    print(f"\nCalibration Results:")
    print(f"Focal Length (fx): {fx:.2f} pixels")
    print(f"Focal Length (fy): {fy:.2f} pixels")

    print("Field of View (degrees):")
    print(f"  {w = } pixels")
    print(f"  {h = } pixels")
    print(f"  {fov_x = :.1f}\N{DEGREE SIGN}")
    print(f"  {fov_y = :.1f}\N{DEGREE SIGN}")

    
if __name__ == "__main__":
    main()
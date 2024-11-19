import cv2
import numpy as np
import serial
from picamera2 import Picamera2, Preview
import time
#from utils.serial import send_command
from utils.raspberry import front_off,front_on
# Initialize the camera
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start()

# Allow the camera to warmup
time.sleep(0.1)

def process_frame(frame):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Threshold the image to get only black colors
    _, black_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    
    # Apply Gaussian blur to the mask
    blur = cv2.GaussianBlur(black_mask, (5, 5), 0)
    
    # Perform edge detection
    edges = cv2.Canny(blur, 50, 150)
    
    # Define a region of interest (ROI)
    height, width = edges.shape
    mask = np.zeros_like(edges)
    polygon = np.array([[
        (0, height),
        (width, height),
        (width, height // 2),
        (0, height // 2),
    ]], np.int32)
    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    
    # Detect lines using Hough transform
    lines = cv2.HoughLinesP(cropped_edges, 1, np.pi / 180, 50, maxLineGap=50)
    
    return lines

def compute_direction(lines, frame):
    height, width, _ = frame.shape
    if lines is None:
        return "forward", (width // 2, height // 2), (width // 2, height // 2 - 50)
    
    left_lines = []
    right_lines = []
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        slope = (y2 - y1) / (x2 - x1)
        if slope < 0:
            left_lines.append(line)
        else:
            right_lines.append(line)
    
    if len(left_lines) == 0 or len(right_lines) == 0:
        return "forward", (width // 2, height // 2), (width // 2, height // 2 - 50)
    
    left_x = np.mean([line[0][0] for line in left_lines])
    right_x = np.mean([line[0][0] for line in right_lines])
    
    center_x = int((left_x + right_x) / 2)
    center_y = height // 2
    
    if center_x < width // 2 - 10:
        return "left", (center_x, center_y), (center_x, center_y - 50)
    elif center_x > width // 2 + 10:
        return "right", (center_x, center_y), (center_x, center_y - 50)
    else:
        return "forward", (center_x, center_y), (center_x, center_y - 50)

def capture_and_process_frame():
    # Capture frame-by-frame
    frame = picam2.capture_array()
    
    # Check for low light conditions
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_intensity = np.mean(gray)
    if mean_intensity < 70:  # Threshold for low light condition
        print("Low light condition detected")
        front_on()
    else:
        print("Normal light condition")
        front_off()
    
    # Process the frame to detect lines
    lines = process_frame(frame)
    
    # Compute the direction based on the detected lines
    direction, start_point, end_point = compute_direction(lines, frame)
    
    # Send the direction command via the send_command function
    #send_command(direction)
    
    # Display the frame with detected lines and direction arrow
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    # Draw the direction arrow
    cv2.arrowedLine(frame, start_point, end_point, (0, 0, 255), 5)
    
    return frame
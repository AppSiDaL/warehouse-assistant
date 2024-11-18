import cv2
import numpy as np
import serial
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

# Initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# Allow the camera to warmup
time.sleep(0.1)

# Initialize serial communication
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.flush()

def process_frame(frame):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to the image
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
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

def compute_direction(lines):
    if lines is None:
        return "forward"
    
    left_lines = []
    right_lines = []
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        slope = (y2 - y1) / (x2 - x1)
        if slope < 0:
            left_lines.append(line)
        else:
            right_lines.append(line)
    
    if len(left_lines) > len(right_lines):
        return "left"
    elif len(right_lines) > len(left_lines):
        return "right"
    else:
        return "forward"

# Capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    
    # Process the frame to detect lines
    lines = process_frame(image)
    
    # Compute the direction based on the detected lines
    direction = compute_direction(lines)
    
    # Send the direction command via serial communication
    ser.write(direction.encode('utf-8'))
    
    # Display the frame with detected lines
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    cv2.imshow("Frame", image)
    
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    
    if key == ord("q"):
        break

cv2.destroyAllWindows()
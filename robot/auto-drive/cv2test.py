import cv2
import numpy as np
import serial
from picamera2 import Picamera2, Preview
import time

# Initialize the camera
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start()

# Allow the camera to warmup
time.sleep(0.1)

# Initialize serial communication
try:
    ser = serial.Serial('/dev/ttyACM0', 9600)  # Ajusta el puerto y la velocidad según sea necesario
except:
    print("No se pudo conectar al puerto")

def send_command(command):
    print(command)
    if command in ['forward', 'backward', 'left', 'right', 'stop']:
        ser.write(command.encode())
        return {"status": "success", "command": command}
    return {"status": "error", "message": "Invalid command"}

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

while True:
    # Capture frame-by-frame
    frame = picam2.capture_array()
    
    # Process the frame to detect lines
    lines = process_frame(frame)
    
    # Compute the direction based on the detected lines
    direction = compute_direction(lines)
    
    # Send the direction command via the send_command function
    send_command(direction)
    
    # Wait for 5 seconds
    time.sleep(5)
    
    # Display the frame with detected lines
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    cv2.imshow("Frame", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.serial import send_command
from fastapi.responses import StreamingResponse
import io
import cv2
import numpy as np
from picamera2 import Picamera2, Preview
import time
import threading

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir cualquier método
    allow_headers=["*"],  # Permitir cualquier encabezado
)

# Initialize the camera
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start()

# Allow the camera to warmup
time.sleep(0.1)

# Global variable to store the processed frame
processed_frame = None

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
    global processed_frame
    while True:
        # Capture frame-by-frame
        frame = picam2.capture_array()
        
        # Check for low light conditions
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_intensity = np.mean(gray)
        if mean_intensity < 50:  # Threshold for low light condition
            send_command("light_front")
        else:
            send_command("shut_front")
        
        # Process the frame to detect lines
        lines = process_frame(frame)
        
        # Compute the direction based on the detected lines
        direction, start_point, end_point = compute_direction(lines, frame)
        time.sleep(2)
        # Send the direction command via the send_command function
        send_command(direction)
        
        # Display the frame with detected lines and direction arrow
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw the direction arrow
        cv2.arrowedLine(frame, start_point, end_point, (0, 0, 255), 5)
        
        # Update the global variable with the processed frame
        processed_frame = frame

# Start the frame capture and processing in a separate thread
thread = threading.Thread(target=capture_and_process_frame)
thread.daemon = True
thread.start()

def generate_frames():
    global processed_frame
    while True:
        if processed_frame is not None:
            _, jpeg = cv2.imencode('.jpg', processed_frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.1)  # Adjust the sleep time as needed

@app.get("/drive")
def get_frame():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
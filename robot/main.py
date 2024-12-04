
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import time
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import hailo
from hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
import serial
from detection_pipeline import GStreamerDetectionApp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Open the two cameras
camera1 = cv2.VideoCapture(0)
camera2 = cv2.VideoCapture(10)

# Allow the cameras to warmup
time.sleep(0.1)

try:
    ser = serial.Serial('/dev/ttyACM0', 9600)  # Ajusta el puerto y la velocidad según sea necesario
except:
    print("No se pudo conectar al puerto")

class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.new_variable = 42  # New variable example

    def new_function(self):  # New function example
        return "The meaning of life is: "

class AutonomousControl:
    def __init__(self):
        self.last_command_time = time.time()
        self.command_interval = 1  # Cada 1 segundo aprox (10 cm)
        self.last_command = None

    def calculate_steering_command(self, left_line, right_line):
        if left_line and right_line:
            return "forward"
        elif left_line:
            return "right"
        elif right_line:
            return "left"
        else:
            return "stop"

    def send_command(self, command):
        current_time = time.time()
        if command != self.last_command or (current_time - self.last_command_time) > self.command_interval:
            print(f"Sending command: {command}")
            ser.write(command.encode())
            self.last_command_time = current_time
            self.last_command = command

# Global variable to store the current frame
current_frame = None
def generate_frames(camera):
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        _, jpeg = cv2.imencode(".jpg", frame)
        frame = jpeg.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        time.sleep(0.1)
def app_callback(pad, info, user_data):
    global current_frame
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    frame = get_numpy_from_buffer(buffer, *get_caps_from_pad(pad))
    current_frame = frame  # Store the current frame
    detections = hailo.get_roi_from_buffer(buffer).get_objects_typed(hailo.HAILO_DETECTION)

    left_line = right_line = False
    for detection in detections:
        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()

        if label == "limiter-line" and confidence > 0.75:
            x_center = (bbox.xmin() + bbox.xmax()) / 2
            if x_center < frame.shape[1] * 0.4:
                left_line = True
            elif x_center > frame.shape[1] * 0.6:
                right_line = True

    control = user_data
    command = control.calculate_steering_command(left_line, right_line)
    control.send_command(command)

    return Gst.PadProbeReturn.OK

control = AutonomousControl()

def generate_frames_from_callback():
    global current_frame
    while True:
        if current_frame is not None:
            _, jpeg = cv2.imencode(".jpg", current_frame)
            frame = jpeg.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        time.sleep(0.1)

@app.get("/camera1")
def get_frame_camera1():
    return StreamingResponse(
        generate_frames(camera1), media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/camera2")
def get_frame_camera2():
    return StreamingResponse(
        generate_frames(camera2), media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/current_command")
def get_current_command():
    return {"current_command": control.last_command}

@app.get("/drive")
def drive():
    return StreamingResponse(
        generate_frames_from_callback(), media_type="multipart/x-mixed-replace; boundary=frame"
    )

if __name__ == "__main__":
    import uvicorn
    app_detection = GStreamerDetectionApp(app_callback, control)
    app_detection.run()
    uvicorn.run(app, host="0.0.0.0", port=8000)
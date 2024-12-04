import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
from hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
import time
from detection_pipeline import GStreamerDetectionApp
import serial
import tempfile

    
# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.new_variable = 42  # New variable example

    def new_function(self):  # New function example
        return "The meaning of life is: "

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
import time

class AutonomousControl:
    def __init__(self):
        self.last_command_time = time.time()
        self.command_interval = 1  # Cada 1 segundo aprox (10 cm)
        self.last_command = None
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

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
        print(f"Sending command: {command}")
        with open("command.txt", 'w') as f:
            f.write(command)

def app_callback(pad, info, user_data):
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    frame = get_numpy_from_buffer(buffer, *get_caps_from_pad(pad))
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

    control = user_data  # Usar la clase para enviar comandos controlados
    command = control.calculate_steering_command(left_line, right_line)
    control.send_command(command)

    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    control = AutonomousControl()  # Instancia para gestionar comandos
    app = GStreamerDetectionApp(app_callback, control)
    app.run()
    
#python autodrive/main.py --labels-json resources/path-labels.json --hef resources/path2.hef --input rpi
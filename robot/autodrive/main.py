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
from serialcom import send_command
import tempfile
import threading
from raspberry import front_on, front_off

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
class AutonomousControl:
    def __init__(self):
        self.last_command_time = time.time()
        self.command_interval = 1  # Cada 1 segundo aprox (10 cm)
        self.last_command = None
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.command_queue = []
        self.lock = threading.Lock()

    def calculate_steering_command(self, left_line, right_line):
        if left_line and right_line:
            return "stop"
        elif left_line:
            return "right"
        elif right_line:
            return "left"
        else:
            return "stop"

    def add_command(self, command):
        with self.lock:
            self.command_queue.append(command)

    def send_commands(self):
        while True:
            if self.command_queue:
                with self.lock:
                    command = self.command_queue.pop(0)
                print(f"Sending command: {command}")
                send_command(command)
            time.sleep(0.1)  # Adjust the sleep time as needed

def app_callback(pad, info, user_data):
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    frame = get_numpy_from_buffer(buffer, *get_caps_from_pad(pad))

    # Calculate the average brightness of the frame
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray_frame)
    print(f"Average brightness: {avg_brightness}")

    if avg_brightness < 80:  # Adjust the threshold as needed
        front_on()
    else:
        front_off()

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
    control.add_command(command)

    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    control = AutonomousControl()  # Instancia para gestionar comandos
    command_thread = threading.Thread(target=control.send_commands)
    command_thread.daemon = True
    command_thread.start()

    app = GStreamerDetectionApp(app_callback, control)
    app.run()
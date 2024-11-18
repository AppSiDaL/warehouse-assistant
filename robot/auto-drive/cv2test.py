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
 
send_command("forward")
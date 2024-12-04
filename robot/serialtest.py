import serial
import time
try:
    ser = serial.Serial('/dev/ttyACM0', 9600)  # Ajusta el puerto y la velocidad según sea necesario
except:
    print("No se pudo conectar al puerto")

def send_command(command):
    print("moving",command)
    if command in ['forward', 'backward', 'left', 'right', 'stop']:
        ser.write(command.encode())
        return {"status": "success", "command": command}
    return {"status": "error", "message": "Invalid command"}

while True:
    send_command("forward")
    time.sleep(2)
    send_command("backward")
    time.sleep(2)
    send_command("stop ")
    time.sleep(2)
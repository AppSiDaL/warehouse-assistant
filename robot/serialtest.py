import serial

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

for i in range(10):
    send_command("forward")
    send_command("backward")
    send_command("left")
    send_command("right")
    send_command("stop ")
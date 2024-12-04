import serial

try:
    ser = serial.Serial('/dev/ttyACM0', 9600)  # Ajusta el puerto y la velocidad según sea necesario
except:
    print("No se pudo conectar al puerto")

def send_command(command):
    ser.write(command.encode())
    return {"status": "success", "command": command}
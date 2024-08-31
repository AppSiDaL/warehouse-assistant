import serial

ser = serial.Serial('/dev/ttyUSB0', 9600)  # Ajusta el puerto y la velocidad según sea necesario

def send_command(command):
    if command in ['forward', 'backward', 'left', 'right', 'stop']:
        ser.write(command.encode())
        return {"status": "success", "command": command}
    return {"status": "error", "message": "Invalid command"}
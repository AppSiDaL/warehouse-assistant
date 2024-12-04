import serial
import subprocess

def get_serial_port():
    try:
        result = subprocess.run(['ls', '-l', '/dev/ttyACM*'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            port = result.stdout.decode('utf-8').split('\n')[0].split()[-1]
            return port
        else:
            print("No se encontraron dispositivos /dev/ttyACM*")
            return None
    except Exception as e:
        print(f"Error al ejecutar el comando: {e}")
        return None

port = get_serial_port()
if port:
    try:
        ser = serial.Serial(port, 9600)
        print(f"Conectado al puerto {port}")
    except:
        print("No se pudo conectar al puerto")
else:
    ser = None

def send_command(command):
    ser.write(command.encode())
    return {"status": "success", "command": command}
import serial
import subprocess

def get_serial_port():
    try:
        result = subprocess.run(['ls', '-l', '/dev/'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            devices = result.stdout.decode('utf-8').split('\n')
            for device in devices:
                if 'ttyACM' in device or 'ttyUSB' in device:
                    port = '/dev/' + device.split()[-1]
                    return port
            print("No se encontraron dispositivos ttyACM o ttyUSB")
            return None
        else:
            print("Error al listar dispositivos en /dev/")
            return None
    except Exception as e:
        print(f"Error al ejecutar el comando: {e}")
        return None

port = get_serial_port()
if port:
    try:
        ser = serial.Serial(port, 9600)
        print(f"Conectado al puerto {port}")
    except Exception as e:
        print(f"No se pudo conectar al puerto: {e}")
else:
    ser = None

def send_command(command):
    if ser:
        ser.write(command.encode())
        return {"status": "success", "command": command}
    else:
        return {"status": "error", "message": "No se pudo conectar al puerto serie"}
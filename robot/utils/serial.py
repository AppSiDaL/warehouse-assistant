import serial
import subprocess
import time

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
        ser = serial.Serial(port, 9600, timeout=1)  # Ajusta la velocidad y el timeout según sea necesario
        ser.flushInput()
        ser.flushOutput()
    except Exception as e:
        print(f"No se pudo conectar al puerto: {e}")
        ser = None
else:
    ser = None

def send_command(command):
    print("moving", command)
    if ser and command in ['forward', 'backward', 'left', 'right', 'stop', 'light_front', 'shut_front']:
        try:
            ser.flushInput()
            ser.flushOutput()
            ser.write(command.encode())
            ser.flush()  # Asegúrate de que los datos se envíen inmediatamente
            return {"status": "success", "command": command}
        except Exception as e:
            print(f"Error al enviar el comando: {e}")
            return {"status": "error", "message": str(e)}
    return {"status": "error", "message": "Invalid command or serial port not available"}
import serial
import subprocess


def get_serial_port():
    try:
        result = subprocess.run(
            ["ls", "-l", "/dev/ttyACM*"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            port = result.stdout.decode("utf-8").split("\n")[0].split()[-1]
            return port
        else:
            print("No se encontraron dispositivos /dev/ttyACM*")
            return None
    except Exception as e:
        print(f"Error al ejecutar el comando: {e}")
        return None


try:
    port = get_serial_port()
    print(f"Conectando al puerto {port}")
    ser = serial.Serial(
        port, 9600
    )  # Ajusta el puerto y la velocidad según sea necesario
except:
    print("No se pudo conectar al puerto")


def send_command(command):
    print("moving", command)
    if command in ["forward", "backward", "left", "right", "stop"]:
        ser.write(command.encode())
        return {"status": "success", "command": command}
    return {"status": "error", "message": "Invalid command"}

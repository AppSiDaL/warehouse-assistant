import cv2

def print_camera_info():
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    print(f"Cámaras disponibles: {arr}")

def open_camera(camera_index, window_name):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: No se puede abrir la cámara {camera_index}")
        return cap

    return cap

def open_two_cameras():
    cap1 = open_camera(0, 'Camera 1')
    cap2 = open_camera(1, 'Camera 2')

    while cap1.isOpened() and cap2.isOpened():
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1:
            print("Error: No se puede leer el cuadro de la cámara 1")
            break
        if not ret2:
            print("Error: No se puede leer el cuadro de la cámara 2")
            break

        cv2.imshow('Camera 1', frame1)
        cv2.imshow('Camera 2', frame2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()

# Imprime información sobre las cámaras disponibles
print_camera_info()

# Abre las dos cámaras
open_two_cameras()
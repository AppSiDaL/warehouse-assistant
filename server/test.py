import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
from pyzbar import pyzbar
import json

# Load a pretrained YOLOv8n model
model = YOLO("/Users/gilbertodavalosnava/Documents/AppSiDaL/warehouse-assistant/server/best.pt")

# Define path to video file
source = "/Users/gilbertodavalosnava/Documents/AppSiDaL/warehouse-assistant/server/wa1.mp4"

# Open the video file
cap = cv2.VideoCapture(source)
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Known parameters
KNOWN_WIDTH = 0.5  # Example: known width of the object in meters
FOCAL_LENGTH = 800  # Example: focal length of the camera in pixels

def estimate_distance(known_width, focal_length, pixel_width):
    return (known_width * focal_length) / pixel_width

# Initialize ByteTrack
tracker = sv.ByteTrack()
plataform_data = {}

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference on the frame
    results = model(frame)

    # Extract boxes and classes
    boxes = results[0].boxes.xyxy.cpu().numpy()  # Bounding boxes
    classes = results[0].boxes.cls.cpu().numpy()  # Class IDs

    # Initialize variables to count boxes within the polygon
    platform_box = None
    max_box_y1 = float("inf")  # Initialize to a large value

    # Identify platform and find the highest box
    for i, cls in enumerate(classes):
        if cls == 1:  # Assuming class 1 is platform
            platform_box = boxes[i]
        elif cls == 0:  # Assuming class 0 is box
            box_x1, box_y1, box_x2, box_y2 = boxes[i]
            if box_y1 < max_box_y1:
                max_box_y1 = box_y1

    if platform_box is not None and max_box_y1 < float("inf"):
        platform_x1, platform_y1, platform_x2, platform_y2 = platform_box
        # Define the polygon as an extension upwards from the platform to the highest box
        polygon = np.array(
            [
                [platform_x1, platform_y1],
                [platform_x2, platform_y1],
                [platform_x2, max_box_y1],
                [platform_x1, max_box_y1],
            ]
        ).astype(int)
        polygon_zone = sv.PolygonZone(polygon=polygon)

        detections = sv.Detections(
            xyxy=results[0].boxes.xyxy.cpu().numpy(),
            confidence=results[0].boxes.conf.cpu().numpy(),
            class_id=results[0].boxes.cls.cpu().numpy(),
            tracker_id=np.arange(1, len(results[0].boxes.xyxy.cpu().numpy()) + 1)  # Assuming tracker IDs are sequential
        )
        detections = tracker.update_with_detections(detections)
        print(detections)
        is_detections_in_zone = polygon_zone.trigger(detections)

        # Draw the polygon on the frame
        cv2.polylines(frame, [polygon], isClosed=True, color=(0, 255, 0), thickness=2)

        # Display box count within the polygon on the frame
        cv2.putText(
            frame,
            f"Boxes in polygon: {polygon_zone.current_count}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        for i in range(len(detections.xyxy)):
            box_x1, box_y1, box_x2, box_y2 = detections.xyxy[i]
            box_width = box_x2 - box_x1
            distance = estimate_distance(KNOWN_WIDTH, FOCAL_LENGTH, box_width)

            # Draw a filled rectangle as background for the text
            text = f"Dist: {distance:.2f}m"
            (text_width, text_height), baseline = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
            )
            cv2.rectangle(
                frame,
                (int(box_x1), int(box_y1) - text_height - 10),
                (int(box_x1) + text_width, int(box_y1)),
                (0, 0, 0),
                -1,
            )

            # Put the distance text on the frame
            cv2.putText(
                frame,
                text,
                (int(box_x1), int(box_y1) - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
            )

            # Draw the tracker ID on the frame only for class 1 (platform)
            if detections.class_id[i] == 1 and i < len(detections.tracker_id):
                print(
                    f"La plataforma tiene el ID: {detections.tracker_id[i]} y contiene {polygon_zone.current_count} cajas"
                )
                platform_id = str(detections.tracker_id[i])
                current_count = polygon_zone.current_count

                # Check if the platform ID is already in the dictionary
                if platform_id in plataform_data:
                    # Update the count only if the new count is greater
                    if current_count > plataform_data[platform_id]:
                        plataform_data[platform_id] = current_count
                else:
                    # Add the platform ID with the current count
                    plataform_data[platform_id] = current_count
                tracker_id = detections.tracker_id[i]
                id_text = f"ID: {tracker_id}"
                (id_text_width, id_text_height), id_baseline = cv2.getTextSize(
                    id_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
                )
                cv2.rectangle(
                    frame,
                    (int(box_x1), int(box_y1) - text_height - id_text_height - 20),
                    (int(box_x1) + id_text_width, int(box_y1) - text_height - 10),
                    (0, 0, 0),
                    -1,
                )
                cv2.putText(
                    frame,
                    id_text,
                    (int(box_x1), int(box_y1) - text_height - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2,
                )

    # Draw the results on the frame
    annotated_frame = results[0].plot()

    # Scan for QR codes
    qrcodes = pyzbar.decode(frame)
    cv2.putText(
        annotated_frame,
        f"QR codes found: {len(qrcodes)}",
        (10, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )
    for qrcode in qrcodes:
        (x, y, w, h) = qrcode.rect
        cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        qrcode_data = qrcode.data.decode("utf-8")
        qrcode_type = qrcode.type
        text = f"{qrcode_data} ({qrcode_type})"
        cv2.putText(
            annotated_frame,
            text,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2,
        )

    # Display the frame
    cv2.imshow("YOLOv8 Inference", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Save the data to a JSON file
with open("/Users/gilbertodavalosnava/Documents/AppSiDaL/warehouse-assistant/server/plataform_data.json", "w") as f:
    json.dump(plataform_data, f)

# Release everything if job is finished
cap.release()
cv2.destroyAllWindows()
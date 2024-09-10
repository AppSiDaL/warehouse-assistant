import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
from .utils import (
    estimate_distance,
    draw_polygon,
    draw_text,
    process_detections,
    scan_qr_codes,
    save_data_to_json,
)
from .config import VIDEO_SOURCE, MODEL_PATH, OUTPUT_JSON


def run_inference(
    video_source=VIDEO_SOURCE,
    model_path=MODEL_PATH,
    output_json=OUTPUT_JSON,
    display=False,
):
    # Load a pretrained YOLOv8n model
    model = YOLO(model_path)

    # Open the video file
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Initialize ByteTrack
    tracker = sv.ByteTrack()
    plataform_data = {}
    qr = None
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
                tracker_id=np.arange(
                    1, len(results[0].boxes.xyxy.cpu().numpy()) + 1
                ),  # Assuming tracker IDs are sequential
            )
            detections = tracker.update_with_detections(detections)
            is_detections_in_zone = polygon_zone.trigger(detections)

            # Draw the polygon on the frame
            draw_polygon(frame, polygon)

            # Display box count within the polygon on the frame
            draw_text(
                frame,
                f"Boxes in polygon: {polygon_zone.current_count}",
                (10, 60),
                font_scale=1,
                color=(0, 255, 0),
            )
            # Scan for QR codes
            qr = scan_qr_codes(frame)
            # Process detections
            process_detections(frame, detections, polygon_zone, plataform_data, qr)

        # Draw the results on the frame
        annotated_frame = results[0].plot()
        if qr:
            draw_text(
                annotated_frame,
                f"QR codes found: {len(qr)}",
                (10, 90),
                font_scale=1,
                color=(0, 255, 0),
            )

        if display:
            # Display the frame
            cv2.imshow("YOLOv8 Inference", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # Encode the frame in JPEG format
        ret, jpeg = cv2.imencode(".jpg", annotated_frame)
        if ret:
            yield jpeg.tobytes()

    if output_json:
        save_data_to_json(plataform_data, output_json)

    cap.release()
    if display:
        cv2.destroyAllWindows()
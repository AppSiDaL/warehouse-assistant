import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import pytesseract
from pyzbar import pyzbar
from .utils import (
    estimate_distance,
    draw_polygon,
    draw_text,
    process_detections,
    save_data_to_json,
    create_or_update_item,
)
from .config import VIDEO_SOURCE, MODEL_PATH, OUTPUT_JSON


def run_inference(
    video_source=VIDEO_SOURCE,
    model_path=MODEL_PATH,
    output_json=OUTPUT_JSON,
    display=False,
    use_ocr=True,  # Argument to choose between OCR and QR
):
    # Load a pretrained YOLOv8n model
    model = YOLO(model_path)

    # Open the video file
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Initialize ByteTrack with custom parameters
    tracker = sv.ByteTrack(
        track_activation_threshold=0.5,  # Detection confidence threshold for track activation
        lost_track_buffer=15,  # Number of frames to buffer when a track is lost
        minimum_matching_threshold=0.5,  # Threshold for matching tracks with detections
        frame_rate=30,  # Frame rate of the video
        minimum_consecutive_frames=5,  # Number of consecutive frames for a valid track
    )
    plataform_data = {}
    detected_text = None
    last_platform_id = None
    processed_platforms = set()

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

        # Identify the largest platform and find the highest box
        largest_area = 0
        for i, cls in enumerate(classes):
            if cls == 1:  # Assuming class 1 is platform
                x1, y1, x2, y2 = boxes[i]
                area = (x2 - x1) * (y2 - y1)
                if area > largest_area:
                    largest_area = area
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
                    [platform_x1, platform_y2],
                    [platform_x2, platform_y2],
                    [platform_x2, max_box_y1],
                    [platform_x1, max_box_y1],
                ]
            ).astype(int)
            polygon_zone = sv.PolygonZone(polygon=polygon)

            detections = sv.Detections(
                xyxy=results[0].boxes.xyxy.cpu().numpy(),
                confidence=results[0].boxes.conf.cpu().numpy(),
                class_id=results[0].boxes.cls.cpu().numpy(),
            )
            detections = tracker.update_with_detections(detections)
            is_detections_in_zone = polygon_zone.trigger(detections)

            # Draw the polygon on the frame
            draw_polygon(frame, polygon)

            # Filter detections to only include boxes within the polygon
            box_detections = detections[
                (detections.class_id == 0) & is_detections_in_zone
            ]

            # Display box count within the polygon on the frame
            draw_text(
                frame,
                f"Boxes in polygon: {len(box_detections)}",
                (10, 60),
                font_scale=1,
                color=(0, 255, 0),
            )

            # Perform OCR or QR scanning on the platform bounding box
            platform_roi = frame[
                int(platform_y1) : int(platform_y2), int(platform_x1) : int(platform_x2)
            ]
            if use_ocr:
                detected_text = pytesseract.image_to_string(platform_roi)
            else:
                qr_codes = pyzbar.decode(frame)
                detected_text = qr_codes[0].data.decode("utf-8") if qr_codes else None
                draw_text(
                    frame,
                    f"Detected QR: {detected_text}",
                    (10, 90),
                    font_scale=1,
                    color=(0, 255, 0),
                )

            # Process detections
            last_platform_id, processed_platforms = process_detections(
                frame,
                detections,
                box_detections,
                plataform_data,
                detected_text,
                last_platform_id,
                processed_platforms,
                output_json,
            )

        # Draw the results on the frame
        annotated_frame = results[0].plot()
        if detected_text:
            draw_text(
                annotated_frame,
                f"Detected Text: {detected_text}",
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

    # Save the last platform data if it exists
    if last_platform_id:
        save_data_to_json(plataform_data, output_json)
        create_or_update_item(
            plataform_data[last_platform_id]["type"],
            plataform_data[last_platform_id]["total_boxes"],
        )

    cap.release()
    if display:
        cv2.destroyAllWindows()

import cv2
import json
from services.items import create_or_update_item
from services.platforms import update_platform
# Known parameters
KNOWN_WIDTH = 0.5  # Example: known width of the object in meters
FOCAL_LENGTH = 800  # Example: focal length of the camera in pixels
AVERAGE_BOX_DEPTH = 0.5  # Example: average depth of a box in meters
PALLET_DEPTH = 2.0  # Example: depth of the pallet in meters

# URL of the endpoint to get item description


def estimate_distance(known_width, focal_length, pixel_width):
    return (known_width * focal_length) / pixel_width


def draw_polygon(frame, polygon):
    cv2.polylines(frame, [polygon], isClosed=True, color=(0, 255, 0), thickness=2)


def draw_text(
    frame, text, position, font_scale=0.5, color=(255, 255, 255), thickness=2
):
    (text_width, text_height), baseline = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
    )
    cv2.rectangle(
        frame,
        (position[0], position[1] - text_height - 10),
        (position[0] + text_width, position[1]),
        (0, 0, 0),
        -1,
    )
    cv2.putText(
        frame,
        text,
        (position[0], position[1] - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness,
    )


def estimate_box_count(distances, average_box_depth, pallet_depth, current_count):
    if not distances:
        return 0
    closest_distance = min(distances)
    num_boxes_in_depth = int(pallet_depth / average_box_depth)
    return num_boxes_in_depth * current_count


def save_data_to_json(plataform_data, output_json):
    with open(output_json, "w") as f:
        json.dump(plataform_data, f, indent=4)


def process_detections(
    frame,
    detections,
    box_detections,
    plataform_data,
    detected_text,
    last_platform_id=None,
    processed_platforms=None,
    output_json="plataform_data.json",
):
    if processed_platforms is None:
        processed_platforms = set()

    distances = []
    current_platform_ids = set()

    for i in range(len(detections.xyxy)):
        box_x1, box_y1, box_x2, box_y2 = detections.xyxy[i]
        box_width = box_x2 - box_x1
        distance = estimate_distance(KNOWN_WIDTH, FOCAL_LENGTH, box_width)
        distances.append(distance)

        # Draw a filled rectangle as background for the text
        text = f"Dist: {distance:.2f}m"
        (text_width, text_height), baseline = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
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
            0.7,
            (255, 255, 255),
            2,
        )

        # Draw tracker ID for class 1 (platform)
        if detections.class_id[i] == 1 and i < len(detections.tracker_id):
            platform_id = str(detections.tracker_id[i])
            current_platform_ids.add(platform_id)
            current_count = len(box_detections)
            type = (
                plataform_data[platform_id]["type"]
                if platform_id in plataform_data
                else ""
            )
            if detected_text:
                # Extract platform ID and box code from detected text
                if "_" in detected_text:
                    platform_id_text, box_code = detected_text.split("_")
                else:
                    platform_id_text, box_code = detected_text, ""

                type = box_code
            else:
                platform_id_text = ""

            # Update platform data and save type
            if platform_id in plataform_data:
                plataform_data[platform_id]["type"] = type
                if current_count > plataform_data[platform_id]["visible_boxes"]:
                    plataform_data[platform_id]["visible_boxes"] = current_count
            else:
                plataform_data[platform_id] = {
                    "visible_boxes": current_count,
                    "total_boxes": 0,
                    "type": type,
                    "platform_id": platform_id_text,
                }

            # Estimate the number of boxes on the platform
            if distances:
                if isinstance(plataform_data[platform_id], dict):
                    box_count = estimate_box_count(
                        distances,
                        AVERAGE_BOX_DEPTH,
                        PALLET_DEPTH,
                        plataform_data[platform_id]["visible_boxes"],
                    )
                    plataform_data[platform_id]["total_boxes"] = box_count
                    draw_text(
                        frame,
                        f"Estimated boxes: {box_count}",
                        (10, 120),
                        font_scale=1,
                        color=(0, 255, 0),
                    )

            # Get item description based on type only if platform_id has changed
            if (
                last_platform_id != platform_id
                and platform_id not in processed_platforms
            ):
                update_platform(
                    platform_id_text,
                    plataform_data[platform_id]["total_boxes"],
                    plataform_data[platform_id]["type"],
                )
                last_platform_id = platform_id
                processed_platforms.add(platform_id)

            draw_text(
                frame,
                f"ID: {detections.tracker_id[i]}",
                (int(box_x1), int(box_y1) - text_height - 30),
                font_scale=0.7,
            )

    # Save JSON when a platform goes out of the screen
    if last_platform_id and last_platform_id not in current_platform_ids:
        save_data_to_json(plataform_data, output_json)
        update_platform(
            plataform_data[last_platform_id]["platform_id"],
            plataform_data[last_platform_id]["total_boxes"],
            plataform_data[last_platform_id]["type"],
        )
        last_platform_id = (
            None  # Reset last_platform_id to indicate the platform has left the screen
        )

    return last_platform_id, processed_platforms

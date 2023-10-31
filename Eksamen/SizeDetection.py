import cv2
import numpy as np
from RobotMovement import move_to_position

colors = [(95, 50, 50, 130, 255, 255),   # Blue
          (0, 50, 50, 7, 255, 255),       # Red
          (20, 50, 50, 35, 255, 255),     # Yellow
          (80, 101, 0, 98, 255, 255)]     # Green

#Target positioner til aflevering af objekter baseret på størrelsen
target_position_small = [0.485, -1.431, -2.259, -1.0293, 1.581, -3.156]  # Small object movement
target_position_medium = [0.220, -1.373, -2.215, -1.135, 1.578, -3.421]  # Medium object movement
target_position_large = [-0.0607, -1.420, -2.148, -1.156, 1.575, -3.702]  # Large object movement
object_final_location = None
small_object_target = [0.485, -1.515, -2.329, -0.875, 1.581, -3.157]
medium_object_target = [0.220, -1.485, -2.329, -0.907, 1.578, -3.422]
large_object_target = [-0.0606, -1.518, -2.258, -0.948, 1.575, -3.703]

# Størrelseforhold mellem objecterne til sortering
small_size_threshold = 1
medium_size_threshold = 2


def detect_objects_by_size(frame, colors):
    largest_area = 0
    largest_contour = None

    for color_range in colors:
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_bound = np.array([color_range[0], color_range[1], color_range[2]])
        upper_bound = np.array([color_range[3], color_range[4], color_range[5]])
        color_mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)

        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > largest_area:
                largest_area = area
                largest_contour = contour

    size_detected = False
    if largest_contour is not None:
        size_detected = True
        moments = cv2.moments(largest_contour)
        if moments["m00"] != 0:
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            cv2.putText(frame, f"Center: ({cx}, {cy})", (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 3)

    return frame, size_detected, largest_contour


def pick_and_place_based_on_size(largest_contour, robot_socket):
    # Determine object size based on contour area
    object_size = cv2.contourArea(largest_contour)  # Assuming 'largest_contour' is detected

    # Perform pick and place operation based on object size
    if object_size < small_size_threshold:
        target_position = target_position_small  # Small object movement
        object_final_location = small_object_target
    elif object_size < medium_size_threshold:
        target_position = target_position_medium  # Medium object movement
        object_final_location = medium_object_target
    else:
        target_position = target_position_large  # Large object movement
        object_final_location = large_object_target

    # Perform pick and place operation
    move_to_position(robot_socket, target_position, object_final_location)

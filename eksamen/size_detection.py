import cv2
import numpy as np
from RobotMovement import *

colors = [(95, 50, 50, 130, 255, 255),   # Blue
          (0, 50, 50, 7, 255, 255),       # Red
          (20, 50, 50, 35, 255, 255),     # Yellow
          (80, 101, 0, 98, 255, 255)]     # Green



picture_position = [0.743, -1.041, -1.962, -1.695, 1.553, -0.846]
pick_up_position = []

#Target positioner til aflevering af objekter baseret på størrelsen
target_position_small = [1.366, -1.876, -1.656, -1.177, 1.547, -0.225]  # Small object movement
target_position_medium = [1.149, -2.019, -1.401, -1.286, 1.548, -0.441]  # Medium object movement
target_position_large = [1.832, -1.732, -1.782, -1.205, 1.548, 0.242]  # Large object movement
object_final_location = None
small_object_target = [1.366, -1.95, -1.747, -1.013, 1.547, -0.225]
medium_object_target = [1.149, -2.093, -1.52, -1.092, 1.548, -0.441]
large_object_target = [1.832, -1.833, -1.909, -0.978, 1.548, 0.241]

# Størrelseforhold mellem objekterne til sortering
small_size_threshold = 5000
medium_size_threshold = 7000
large_size_threshold = 9000

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
            global pick_up_position
            pick_up_position = calculate_position_size(cx, cy, largest_area)
        cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 3)


    return frame, size_detected, largest_contour


def pick_and_place_based_on_size(largest_contour, robot_socket, robot_moved_to_default):
    # Determine object size based on contour area
    object_size = cv2.contourArea(largest_contour)  # Assuming 'largest_contour' is detected

    if object_size > 2000 and robot_moved_to_default:
        # Perform pick and place operation based on object size
        if object_size < small_size_threshold:
            target_position = target_position_small  # Small object movement
            object_final_location = small_object_target
        elif object_size < medium_size_threshold and object_size > small_size_threshold:
            target_position = target_position_medium  # Medium object movement
            object_final_location = medium_object_target
        else:
            target_position = target_position_large  # Large object movement
            object_final_location = large_object_target

        robot_moved_to_default = False
        move_position_linear(robot_socket, pick_up_position)
        print(pick_up_position)
        Read_Script("ON", robot_socket)
        time.sleep(1)
        move_up_in_z(robot_socket,0.09)
        move_to_position(robot_socket, target_position)
        move_to_position(robot_socket, object_final_location)
        Read_Script("OFF", robot_socket)
        time.sleep(1)
        move_to_position(robot_socket, picture_position)
        robot_moved_to_default = True
        # definer object farve og pick up location
        robot_moved_to_default = False  # Reset the flag since an object is detected
        # indsæt robot False, hvis det giver problemer igen.

    elif robot_moved_to_default == True:
        pass

    else:
        move_to_position(robot_socket, picture_position)
        print("moving to defautl")
        robot_moved_to_default = True

    return robot_moved_to_default
import cv2
import numpy as np
from RobotMovement import *

# Opretter en liste til de udvalgte farver. Upper og Lower bound til hver farve.
colors = [(104, 58, 3, 117, 255, 255),   # Blue
          (0, 170, 79, 10, 255, 136, 175, 52, 101, 179, 255, 123),       # Red
          (22, 45, 0, 35, 255, 255),     # Yellow
          (78, 72, 0, 103, 255, 217)]     # Green

size_counts = {"Small": 0, "Medium": 0, "Large": 0}



picture_position = [0.641, -1.118, -2.001, -1.575, 1.554, -0.948]
pick_up_position = []
moveto = ""

#Target positioner til aflevering af objekter baseret på størrelsen
target_position_small = [1.585, -1.776, -1.757, -1.182, 1.547, -0.005]  # Small object movement
target_position_medium = [1.366, -1.876, -1.656, -1.177, 1.547, -0.225]  # Medium object movement
target_position_large = [1.149, -2.019, -1.401, -1.286, 1.548, -0.441]  # Large object movement
object_final_location = None


# Størrelseforhold mellem objekterne til sortering
small_size_threshold = 6700
medium_size_threshold = 9900
large_size_threshold = 9999

def detect_objects_by_size(frame, colors):
    blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)
    largest_area = 0
    largest_contour = None
    focused_mask = np.zeros_like(frame[:, :, 0])

    all_colors_mask = np.zeros_like(frame[:, :, 0])
    for color in colors:
        if color == colors[1]:
            lower_boundL = np.array([color[0], color[1], color[2]])
            upper_boundL = np.array([color[3], color[4], color[5]])
            lower_boundH = np.array([color[6], color[7], color[8]])
            upper_boundH = np.array([color[9], color[10], color[11]])
            hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
            maskL = cv2.inRange(hsv, lower_boundL, upper_boundL)
            maskH = cv2.inRange(hsv, lower_boundH, upper_boundH)
            maskRed = cv2.add(maskL, maskH)

            color_mask = cv2.bitwise_or(all_colors_mask, maskRed)
        else:
            lower_bound = np.array([color[0], color[1], color[2]])
            upper_bound = np.array([color[3], color[4], color[5]])
            hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            color_mask = cv2.bitwise_or(all_colors_mask, mask)

        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > largest_area:
                print(area)
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


def size_sorting(largest_contour, robot_socket, robot_moved_to_default):
    # Bestem objektstørrelse baseret på konturareal
    object_size = cv2.contourArea(largest_contour)  # Assuming 'largest_contour' is detected

    # Kontroller om objektstørrelsen er tilstrækkelig stor, og at robotten ikke allerede har bevæget sig til standardpositionen
    if object_size > 3200 and robot_moved_to_default:
        # Udfør pick and place-operation baseret på objektstørrelse
        if object_size < small_size_threshold:
            moveto = "Small"
            target_position = target_position_small  # Small object movement
        elif object_size < medium_size_threshold and object_size > small_size_threshold:
            moveto = "Medium"
            target_position = target_position_medium  # Medium object movement
        else:
            moveto = "Large"
            target_position = target_position_large  # Large object movement

        # Robotten har bevæget sig væk fra standardpositionen
        robot_moved_to_default = False

        # Robotten bevæger sig til positionen for at samle objektet op
        move_position_linear(robot_socket, pick_up_position,moveto)
        Vacuum("ON", robot_socket)
        time.sleep(1)
        move_up_in_z(robot_socket,0.09)

        # Robotten bevæger sig til afleveringspositionen
        move_position_joints(robot_socket, target_position, moveto)
        Vacuum("OFF", robot_socket)
        time.sleep(1)
        size_counts[moveto] += 1
        move_position_joints(robot_socket, picture_position, moveto)

    # Hvis robotten allerede har bevæget sig til standardpositionen
    elif robot_moved_to_default:
        pass

    # Hvis ingen betingelser er opfyldt, sættes robotten til standardpositionen
    else:
        moveto = "Default"
        move_position_joints(robot_socket, picture_position, moveto)
        robot_moved_to_default = True

    return robot_moved_to_default
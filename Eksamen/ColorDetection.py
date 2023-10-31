import cv2
import numpy as np

from RobotMovement import connect_to_robot, vacuum_on, vacuum_off, move_to_position
robot_moved_to_default = False

default_position = [0.326, -1.262, -1.980, -1.478, 1.580, -3.314]

#Target and Final positions for color deliveries.
target_position_blue = [-0.06, -1.4259, -2.1561, -1.144, 1.57, -3.97]
final_position_blue = [-0.0631, -1.5189, -2.2586, -0.9487, 1.5751, -3.7056]
target_position_green = [0.205, -1.367, -2.238, -1.118, 1.578, -3.436]
final_position_green = [0.205, -1.447, -2.323, -0.952, 1.578, -3.436]
target_position_yellow = [0.700, -1.413, -2.166, -1.137, 1.582, -2.941]
final_position_yellow = [0.700, -1.510, -2.272, -0.934, 1.582, -2.941]
target_position_red = [0.471, -1.350, -2.217, -1.151, 1.581, -3.170]
final_position_red = [0.471, -1.446, -2.324, -0.950, 1.580, -3.170]

# position for taking a picture of the objects to be sorted.
picture_position = []

# Opretter en liste til de udvalgte farver. Upper og Lower bound til hver farve.
colors = [(95, 50, 50, 130, 255, 255),   # Blue
          (0, 50, 50, 7, 255, 255),       # Red
          (20, 50, 50, 35, 255, 255),     # Yellow
          (80, 101, 0, 98, 255, 255)]     # Green


def detect_objects_by_color(frame, focus_color_index):
    #benytter os af gaussianblur for at minimere støj på billedet.
    blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)

    focused_mask = np.zeros_like(frame[:, :, 0])

    all_colors_mask = np.zeros_like(frame[:, :, 0])
    for color in colors:
        lower_bound = np.array([color[0], color[1], color[2]])
        upper_bound = np.array([color[3], color[4], color[5]])
        hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        all_colors_mask = cv2.bitwise_or(all_colors_mask, mask)

        if colors.index(color) == focus_color_index:
            focused_mask = mask

    contours, _ = cv2.findContours(focused_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    color_detected = False

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:
            color_detected = True

            moments = cv2.moments(contour)
            if moments["m00"] != 0:
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])

                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                cv2.putText(frame, f"Center: ({cx}, {cy})", (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 2)

            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 3)

    masked_frame = cv2.bitwise_and(frame, frame, mask=all_colors_mask)

    return frame, masked_frame, color_detected

def color_sorting(focus_method, focus_color_index, frame,robot_socket,robot_moved_to_default ):

        if focus_method == "color":
            cv2.putText(frame, f"Sorting by: Color", (1, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)
            processed_frame, masked_frame, color_detected = detect_objects_by_color(frame, focus_color_index)
            if color_detected:
                # Determine object color based on focus_color_index
                if focus_color_index == 0:  # Blue
                    target_position = target_position_blue
                    final_position = final_position_blue

                elif focus_color_index == 1:  # Red
                    target_position = target_position_red
                    final_position = final_position_red
                elif focus_color_index == 2:  # Yellow
                    target_position = target_position_yellow
                    final_position = final_position_yellow
                elif focus_color_index == 3:  # Green
                    target_position = target_position_green
                    final_position = final_position_green

                # Perform pick and place operation
                move_to_position(robot_socket, target_position, final_position)
                # definer object farve og pick up location
                robot_moved_to_default = False  # Reset the flag since an object is detected

            elif not robot_moved_to_default:
                # Move UR to default location only if it has not moved there before
                move_to_position(robot_socket, default_position)
                robot_moved_to_default = True  # Set the flag to indicate that the robot has moved

        return processed_frame, color_detected, robot_moved_to_default
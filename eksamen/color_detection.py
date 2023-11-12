import cv2
import numpy as np

from RobotMovement import connect_to_robot, Read_Script, vacuum_off, move_to_position, calculate_position, move_position_linear
from eksamen import ur

robot_moved_to_default = False

default_position = [0.326, -1.262, -1.980, -1.478, 1.580, -3.314]

target_position_blue = [1.366, -1.876, -1.656, -1.177, 1.547, -0.225]
final_position_blue = [1.366, -1.95, -1.747, -1.013, 1.547, -0.225]
target_position_green = [1.149, -2.019, -1.401, -1.286, 1.548, -0.441]
final_position_green = [1.149, -2.093, -1.52, -1.092, 1.548, -0.441]
target_position_yellow = [1.832, -1.732, -1.782, -1.205, 1.548, 0.242]
final_position_yellow = [1.832, -1.833, -1.909, -0.978, 1.548, 0.241]
target_position_red = [1.585, -1.776, -1.757, -1.182, 1.547, -0.005]
final_position_red = [1.585, -1.863, -1.865, -0.987, 1.546, -0.005]

# position for taking a picture of the objects to be sorted.
picture_position = [0.741, -1.044, -1.953, -1.702, 1.553, -0.847]
pick_up_position = []



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
                global pick_up_position
                pick_up_position = calculate_position(cx, cy)
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                cv2.putText(frame, f"Center: ({cx}, {cy})", (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 2)


            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 3)

    masked_frame = cv2.bitwise_and(frame, frame, mask=all_colors_mask)

    return frame, masked_frame, color_detected

def color_sorting(focus_method, focus_color_index, frame,robot_socket,robot_moved_to_default ):
    #print(pick_up_position)
    #print(robot_moved_to_default)


    if focus_method == "color":
        cv2.putText(frame, f"Sorting by: Color", (1, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)
        processed_frame, masked_frame, color_detected = detect_objects_by_color(frame, focus_color_index)

        joint_position = ur.UR_RobotState(robot_socket)
        joint_position.start()
        current_position = joint_position.get_actual_joint_positions()
        #print(current_position)
        joint_position.stop()
        print(current_position)

        if current_position == picture_position and color_detected and robot_moved_to_default:

            # Determine object color based on focus_color_index
            if focus_color_index == 0:  # Blue
                move_position_linear(robot_socket, pick_up_position)
                Read_Script("ON")
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
            robot_moved_to_default = False
            move_to_position(robot_socket, target_position, final_position)
            move_to_position(robot_socket, picture_position)
            robot_moved_to_default = True
            # definer object farve og pick up location
            #robot_moved_to_default = False  # Reset the flag since an object is detected

        #else:
        #    move_to_position(robot_socket, picture_position)
        #    robot_moved_to_default = True

    return processed_frame, color_detected, robot_moved_to_default
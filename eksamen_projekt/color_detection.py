import time
import cv2
import numpy as np
from RobotMovement import Vacuum, move_position_joints, calculate_position_color, move_position_linear, move_up_in_z

#Denne variable bruges til at bestemme om robotten er i sin udgangsposition til at behandle billeder.
robot_moved_to_default = False

#positioner til aflevering af objekter, baseret på deres farve.
target_position_blue = [1.366, -1.876, -1.656, -1.177, 1.547, -0.225]
target_position_green = [1.149, -2.019, -1.401, -1.286, 1.548, -0.441]
target_position_yellow = [1.832, -1.732, -1.782, -1.205, 1.548, 0.242]
target_position_red = [1.585, -1.776, -1.757, -1.182, 1.547, -0.005]


# position for taking a picture of the objects to be sorted.
picture_position = [0.641, -1.118, -2.001, -1.575, 1.554, -0.948]

#picture position kalkuleres via def calculate_position i RobotMovement.py
#value bliver assigned inde i def detect_objects_by_color.
pick_up_position = []
moveto = ""

# Opretter en liste til de udvalgte farver. Upper og Lower bound til hver farve.
colors = [(104, 58, 3, 117, 255, 255),   # Blue
          (0, 170, 79, 10, 255, 136, 175, 52, 101, 179, 255, 123),       # Red
          (22, 45, 0, 35, 255, 255),     # Yellow
          (78, 72, 0, 103, 255, 217)]     # Green

# Define a dictionary to store the count for each color
color_counts = {"Blue": 0, "Red": 0, "Yellow": 0, "Green": 0}


def detect_objects_by_color(frame, focus_color_index):
    #benytter os af gaussianblur for at minimere støj på billedet.
    blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)
    global pick_up_position

    focused_mask = np.zeros_like(frame[:, :, 0])

    all_colors_mask = np.zeros_like(frame[:, :, 0])
    for color in colors:
        if color == colors[1]:
            # Hvis farven er rød, skal der opdeles i lavere og højere grænser på grund af farvens rækkevidde på HSV hue circlen.
            lower_boundL = np.array([color[0], color[1], color[2]])
            upper_boundL = np.array([color[3], color[4], color[5]])
            lower_boundH = np.array([color[6], color[7], color[8]])
            upper_boundH = np.array([color[9], color[10], color[11]])
            hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
            maskL = cv2.inRange(hsv, lower_boundL, upper_boundL)
            maskH = cv2.inRange(hsv, lower_boundH, upper_boundH)
            maskRed = cv2.add(maskL, maskH)
            mask = cv2.add(maskL, maskH)
            all_colors_mask = cv2.bitwise_or(all_colors_mask, maskRed)
        else:
            # Hvis farven ikke er rød, opret maske for det normale farveområde
            lower_bound = np.array([color[0], color[1], color[2]])
            upper_bound = np.array([color[3], color[4], color[5]])
            hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            all_colors_mask = cv2.bitwise_or(all_colors_mask, mask)

        # Hvis den aktuelle farve svarer til fokusfarven, opdater fokuseret maske
        if colors.index(color) == focus_color_index:
            focused_mask = mask

    # Find konturer baseret på focused_mask
    contours, _ = cv2.findContours(focused_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    color_detected = False
    print(len(contours))
    for contour in contours:
        # Beregn området af konturen
        area = cv2.contourArea(contour)
        if area > 5000:
            color_detected = True

            # Beregn centrum af konturen
            moments = cv2.moments(contour)
            if moments["m00"] != 0:
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])
                # Beregn positionen for objektet baseret på konturens centrum
                pick_up_position = calculate_position_color(cx, cy)
                print("Calculated pick up position",pick_up_position)
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                cv2.putText(frame, f"Center: ({cx}, {cy})", (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 2)

            # Tegn konturen på billedet
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 3)
            break
        else:
            color_detected = False

    # Opret et maskebillede baseret på alle farverne
    masked_frame = cv2.bitwise_and(frame, frame, mask=all_colors_mask)


    return frame, masked_frame, color_detected

def color_sorting(focus_method, focus_color_index, frame,robot_socket,robot_moved_to_default ):
    # Tjekker om fokus metoden er color.
    if focus_method == "color":
        # Indsætter teksten for at vise, at objekterne sorteres efter farve
        cv2.putText(frame, f"Sorting by: Color", (1, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)

        # Viser optælling af farver på skærmen
        for color, count in color_counts.items():
            cv2.putText(frame, f"{color} Count: {count}", (10, 30 + 20 * list(color_counts.keys()).index(color)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Detekterer farver i det givne billede
        processed_frame, masked_frame, color_detected = detect_objects_by_color(frame, focus_color_index)

        # Gemmer det behandlede billede og viser det
        cv2.imwrite("billeder/picture_color.png", processed_frame)
        picture_color = cv2.imread("billeder/picture_color.png")
        cv2.imshow("Test", picture_color)
        cv2.waitKey(1)
        #print(color_detected, robot_moved_to_default,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Hvis farve detekteres, og robotten er i standardpositionen
        if color_detected and robot_moved_to_default:
            # Bestemmer objektfarven baseret på fokusfarveindekset
            if focus_color_index == 0:  # Blue
                target_position = target_position_blue
                moveto = "Blue"
            elif focus_color_index == 1:  # Red
                target_position = target_position_red
                moveto = "Red"
            elif focus_color_index == 2:  # Yellow
                target_position = target_position_yellow
                moveto = "Yellow"
            elif focus_color_index == 3:  # Green
                target_position = target_position_green
                moveto = "Green"


            # Robotten har bevæget sig væk fra standardpositionen
            robot_moved_to_default = False

            # Robotten bevæger sig til positionen for at samle objektet op
            move_position_linear(robot_socket, pick_up_position, focus_color_index)
            Vacuum("ON", robot_socket)
            time.sleep(1)
            move_up_in_z(robot_socket,0.09)

            # Robotten bevæger sig til afleveringspositionen
            move_position_joints(robot_socket, target_position, moveto)
            Vacuum("OFF", robot_socket)
            time.sleep(1)
            color_counts[moveto] += 1
            move_position_joints(robot_socket, picture_position, moveto)

        # Hvis robotten allerede har bevæget sig til standardpositionen
        elif robot_moved_to_default:
            pass

        # Hvis ingen betingelser er opfyldt, sæt robotten til standardpositionen
        else:
            moveto = "Default"
            move_position_joints(robot_socket, picture_position, moveto)
            robot_moved_to_default = True
            print(robot_moved_to_default)

    return processed_frame, color_detected, robot_moved_to_default
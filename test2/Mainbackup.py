import cv2
import numpy as np
from RobotMovement import connect_to_robot, vacuum_on, vacuum_off, move_to_position

focus_color_index = 0 # variable til at holde styr på hvilken farve er i fokus
focus_method = "color" # variable til at holde styr på hvilket sorterings mode programmet kører i Color/Size
objects_sorted = 0 # skal bruges senere til at tælle antal objekter der er sorteret
robot_busy = False
robot_moved_to_default = False

#initialisere robot forbindelse
robot_ip = "192.168.0.10"
robot_port = 30002
robot_socket = connect_to_robot(robot_ip,robot_port)

# Størrelseforhold mellem objecterne til sortering
small_size_threshold = 1
medium_size_threshold = 2

#Target positioner til aflevering af objekter baseret på størrelsen
small_object_target = [0.48546773195266724, -1.515461591338255, -2.32981538772583, -0.8750452560237427, 1.5810723304748535, -3.1572044531451624]
medium_object_target = [0.2202010154724121, -1.4858639550260087, -2.3299739360809326, -0.9077205818942566, 1.5786256790161133, -3.4224165121661585]
large_object_target = [-0.06068021455873662, -1.5185403277030964, -2.25874662399292, -0.9489020866206666, 1.5751457214355469, -3.703146282826559]

# Kasse lokation
container_pickup_location = [-0.7903359572040003, -2.206264158288473, -1.646661639213562, -1.8003956280150355, 0.9046512246131897, -0.440160099660055]
container_home_location = [-0.7903078238116663, -1.9489785633482875, -1.1922039985656738, -2.512567182580465, 0.9065796732902527, -0.4395869413958948]
# Opretter en liste til de udvalgte farver. Upper og Lower bound til hver farve.
colors = [(95, 50, 50, 130, 255, 255),   # Blue
          (0, 50, 50, 7, 255, 255),       # Red
          (20, 50, 50, 35, 255, 255),     # Yellow
          (80, 101, 0, 98, 255, 255)]     # Green

#Funktion til at sortere efter farve
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

#Funktion til at sortere efter størrelse
def detect_objects_by_size(frame):
    global colors
    global focus_color_index

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
            cv2.putText(frame, f"Center: ({cx}, {cy})", (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 2)

        cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 3)

    return frame, size_detected, largest_contour


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()

    if not robot_busy:

        if focus_method == "color":
            cv2.putText(frame, f"Sorting by: Color", (1, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)
            processed_frame, masked_frame, color_detected = detect_objects_by_color(frame, focus_color_index)
            if color_detected:
                # Determine object color based on focus_color_index
                if focus_color_index == 0:  # Blue
                    target_position = [-0.06, -1.4259, -2.1561, -1.144, 1.57, -3.97]
                    final_position = [-0.0631, -1.5189, -2.2586, -0.9487, 1.5751, -3.7056]

                elif focus_color_index == 1:  # Red
                    target_position = [0.4716886281967163, -1.3508786422065278, -2.217750310897827, -1.1519264739802857, 1.5812199115753174, -3.1701539198504847]
                    final_position = [0.47178056836128235, -1.4461347845247765, -2.3243308067321777, -0.9500878018191834, 1.5809961557388306, -3.170647923146383]
                elif focus_color_index == 2:  # Yellow
                    target_position = [0.7006034255027771, -1.4135532987168808, -2.166627883911133, -1.1371448200992127, 1.5825966596603394, -2.9412949720965784]
                    final_position = [0.7007275819778442, -1.5104431745461007, -2.2727348804473877, -0.934100942020752, 1.5824851989746094, -2.941820208226339]
                elif focus_color_index == 3:  # Green
                    target_position = [0.20538535714149475, -1.3670546871474762, -2.2383196353912354, -1.1183951956084748, 1.578601360321045, -3.4366043249713343]
                    final_position = [0.2054448425769806, -1.4477618870190163, -2.3234686851501465, -0.9526143235019227, 1.5784783363342285, -3.436953369771139]


                # Perform pick and place operation
                robot_busy = True
                move_to_position(robot_socket, target_position, final_position)
                # definer object farve og pick up location
                robot_busy = False
                robot_moved_to_default = False  # Reset the flag since an object is detected

            elif not robot_moved_to_default:
                # Move UR to default location only if it has not moved there before
                default_position = [0.3264823257923126, -1.26273466766391, -1.9809584617614746, -1.4787000578692933, 1.5803697109222412, -3.314575258885519]
                move_to_position(robot_socket, default_position)
                robot_moved_to_default = True  # Set the flag to indicate that the robot has moved


        elif focus_method == "size":
            cv2.putText(frame, f"Sorting by: Size", (1, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)
            processed_frame, size_detected, largest_contour = detect_objects_by_size(frame)

            if size_detected:
                # Determine object size based on contour area
                object_size = cv2.contourArea(largest_contour)  # Assuming 'largest_contour' is detected

                # Perform pick and place operation based on object size
                if object_size < small_size_threshold:
                    target_position = [0.4853595495223999, -1.4315304321101685, -2.2594118118286133, -1.0293823641589661, 1.5811961889266968, -3.1568432489978235]  # Small object movement

                elif object_size < medium_size_threshold:
                    target_position = [0.22004520893096924, -1.3731062573245545, -2.215040922164917, -1.1353859168342133, 1.5787533521652222, -3.42188269296755]  # Medium object movement
                else:
                    target_position = [-0.060787502919332326, -1.4208181512406846, -2.1486549377441406, -1.1567146939090271, 1.5753016471862793, -3.7026103178607386]  # Large object movement

                # Perform pick and place operation
                robot_busy = True
                move_to_position(robot_socket, target_position, small_object_target)

            else:
                pass
            #Move the kasse destination

        else:
            color_detected = False
            size_detected = False

    cv2.imshow('Detected Objects', processed_frame)
    if focus_method == "size" and size_detected:
        pass
    elif focus_method == "color" and not color_detected:
        focus_color_index = (focus_color_index + 1) % len(colors)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('c'):
        focus_method = "color"
    elif key == ord('s'):
        focus_method = "size"
    elif key == ord('p'):
        # Move the robot to the specific target position when 'p' is pressed
        robot_busy = True
        move_to_position(robot_socket, container_home_location,container_pickup_location)
        robot_busy = False

cap.release()
cv2.destroyAllWindows()
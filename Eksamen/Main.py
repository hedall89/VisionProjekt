import cv2
import numpy as np
from RobotMovement import connect_to_robot, vacuum_on, vacuum_off, move_to_position
from ColorDetection import color_sorting
from SizeDetection import detect_objects_by_size
from SizeDetection import pick_and_place_based_on_size, colors


focus_color_index = 0 # variable til at holde styr på hvilken farve er i fokus
focus_method = "color" # variable til at holde styr på hvilket sorterings mode programmet kører i Color/Size
objects_sorted = 0 # skal bruges senere til at tælle antal objekter der er sorteret
robot_moved_to_default = False

#initialisere robot forbindelse
robot_ip = "192.168.0.10"
robot_port = 30002
robot_socket = connect_to_robot(robot_ip,robot_port)


# Kasse lokation
container_pickup_location = [-0.790, -2.206, -1.646, -1.800, 0.904, -0.440]
container_home_location = [-0.790, -1.948, -1.192, -2.512, 0.906, -0.439]
# Opretter en liste til de udvalgte farver. Upper og Lower bound til hver farve.



cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()

    if focus_method == "color":
        processed_frame, color_detected, robot_moved_to_default = color_sorting(focus_method, focus_color_index, frame,robot_socket, robot_moved_to_default)

    if focus_method == "size":
        cv2.putText(frame, f"Sorting by: Size", (1, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)
        processed_frame, size_detected, largest_contour = detect_objects_by_size(frame, colors)

        if size_detected:
            pick_and_place_based_on_size(largest_contour, robot_socket)


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
        move_to_position(robot_socket, container_home_location,container_pickup_location)


cap.release()
cv2.destroyAllWindows()
import cv2
import numpy as np
from threading import Thread
from queue import Queue
from RobotMovement import connect_to_robot, vacuum_off, move_to_position
from color_detection import color_sorting, picture_position
from size_detection import detect_objects_by_size
from size_detection import pick_and_place_based_on_size, colors


focus_color_index = 0 # variable til at holde styr på hvilken farve er i fokus
focus_method = "color" # variable til at holde styr på hvilket sorterings mode programmet kører i Color/Size
objects_sorted = 0 # skal bruges senere til at tælle antal objekter der er sorteret
robot_moved_to_default = True

#initialisere robot forbindelse
robot_ip = "192.168.0.10"
robot_port = 30002
robot_socket = connect_to_robot(robot_ip,robot_port)


# Kasse lokation
container_pickup_location = [-0.790, -2.206, -1.646, -1.800, 0.904, -0.440]
container_home_location = [-0.790, -1.948, -1.192, -2.512, 0.906, -0.439]
# Opretter en liste til de udvalgte farver. Upper og Lower bound til hver farve.

# Create a flag for stopping the thread
stop_thread = False

# Create a queue for passing frames between threads
frame_queue = Queue()
frame = np.zeros((480, 640, 3), dtype=np.uint8)
def video_capture_thread():
    global stop_thread

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while not stop_thread:
        ret, frame = cap.read()

        # Put the frame into the queue
        frame_queue.put(frame)

        # Process the frame or perform other tasks
        # ...

        cv2.imshow('Detected Objects', frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            stop_thread = True

    cap.release()
    cv2.destroyAllWindows()

# Start the video capture thread
video_thread = Thread(target=video_capture_thread)
video_thread.start()


while True:


    if robot_moved_to_default:
        if not frame_queue.empty():
            # Get the frame from the queue
            frame = frame_queue.get()
            cv2.imshow("picture",frame)
            cv2.waitKey(3)


        if focus_method == "color":
            processed_frame, color_detected, robot_moved_to_default = color_sorting(focus_method, focus_color_index, frame,robot_socket, robot_moved_to_default)


        if focus_method == "size":
            cv2.putText(frame, f"Sorting by: Size", (1, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)
            processed_frame, size_detected, largest_contour = detect_objects_by_size(frame, colors)

            if size_detected:
                pick_and_place_based_on_size(largest_contour, robot_socket)


        cv2.imshow('Detected Objects', frame)
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



cv2.destroyAllWindows()
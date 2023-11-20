import cv2
from RobotMovement import connect_to_robot, pickup_crate
from color_detection import color_sorting
from size_detection import detect_objects_by_size
from size_detection import size_sorting, colors, size_counts

# Initialiser variabler
focus_color_index = 0 # variable til at holde styr på hvilken farve er i fokus
focus_method = "" # variable til at holde styr på hvilket sorterings mode programmet kører i Color/Size
robot_moved_to_default = False # bruges til at Fortælle om robotten er i Default position, hvor den også tager billede af arbejdsområdet.

#initialisere robot forbindelse
robot_ip = "192.168.0.10"
robot_port = 30002
robot_socket = connect_to_robot(robot_ip,robot_port)

# Initialiser videooptagelse
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    # Læs et billede fra videooptagelsen
    ret, frame = cap.read()

    # Håndter fokusmetoden "Color"
    if focus_method == "color":
        processed_frame, color_detected, robot_moved_to_default = color_sorting(focus_method, focus_color_index, frame,robot_socket, robot_moved_to_default)

    # Håndter fokusmetoden "Size"
    if focus_method == "size":

        # Udfør size_sorting-funktionen, og opdater variablen 'robot_moved_to_default'
        robot_moved_to_default = size_sorting(*detect_objects_by_size(frame, colors), robot_socket,
                                              robot_moved_to_default)
        #text på videofeed til sorterings metode
        cv2.putText(frame, f"Sorting by: Size", (1, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)
        #Text på videofeed til counter
        for color, count in size_counts.items():
            cv2.putText(frame, f"{color} Count: {count}", (10, 30 + 20 * list(size_counts.keys()).index(color)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        processed_frame_size, size_detected, largest_contour = detect_objects_by_size(frame, colors)

        # Gem det behandlede billede og vis det
        cv2.imwrite("billeder/picture_size.png", processed_frame_size)
        picture_size = cv2.imread("billeder/picture_size.png")
        cv2.imshow("Test", picture_size)
        cv2.waitKey(1)

        # Hvis size er detekteret, udfør size_sorting-funktionen
        if size_detected:
            robot_moved_to_default = size_sorting(largest_contour, robot_socket, robot_moved_to_default)

    #viser live feed vindue
    cv2.imshow('Detected Objects', frame)

    # Opdater fokusmetoden og farveindekset baseret på brugerinput
    if focus_method == "size" and size_detected:
        pass
    elif focus_method == "color" and not color_detected:
        focus_color_index = (focus_color_index + 1) % len(colors)

    # Vent på brugerinput
    key = cv2.waitKeyEx(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        focus_method = "color"
    elif key == ord('s'):
        focus_method = "size"
    elif key == ord('p'):
        focus_method = ""
        pickup_crate()

# lukker video optagelse og lukker alle vinduer.
cap.release()
cv2.destroyAllWindows()
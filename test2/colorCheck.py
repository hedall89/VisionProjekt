import cv2
import numpy as np

focus_color_index = 0 # variable til at holde styr på hvilken farve er i fokus
focus_method = "color" # variable til at holde styr på hvilket sorterings mode programmet kører i Color/Size
objects_sorted = 0 # skal bruges senere til at tælle antal objekter der er sorteret

#Variables for drawing rectangle used for camera calibration.
start_point = (50, 50)
end_point = (590, 430)
color = (255, 255, 255)
thickness = 2

# Opretter en liste til de udvalgte farver. Upper og Lower bound til hver farve.
colors = [(104, 58, 3, 117, 255, 255),   # Blue
          (0, 170, 79, 10, 255, 136, 175, 52, 101, 179, 255, 123),       # Red
          (22, 45, 0, 35, 255, 255),     # Yellow
          (78, 72, 0, 103, 255, 217)]     # Green

#Funktion til at sortere efter farve
def detect_objects_by_color(frame, focus_color_index):
    #benytter os af gaussianblur for at minimere støj på billedet.
    blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)

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
            kernel = np.ones((5, 5), np.uint8)

            # Perform dilation with 3 iterations
            dilated_image = cv2.dilate(maskRed, kernel, iterations=5)
            mask= cv2.add(maskL, maskH)
            all_colors_mask = cv2.bitwise_or(all_colors_mask, maskRed)
        else:
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
            print(area)
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

    return frame, masked_frame, color_detected, dilated_image

#Funktion til at sortere efter størrelse
def detect_objects_by_size(frame):
    global colors
    global focus_color_index

    # benytter os af gaussianblur for at minimere støj på billedet.
    blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)

    largest_area = 0
    largest_contour = None

    for color_range in colors:

        hsv_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

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

    return frame, size_detected


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
#cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
#cap.set(cv2.CAP_PROP_EXPOSURE,-6)



while True:

    ret, frame = cap.read()

    image = cv2.rectangle(frame, start_point, end_point, color, thickness)




    if focus_method == "color":
        cv2.putText(frame, f"Sorting by: Color", (1, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)
        processed_frame, masked_frame, color_detected, maskTest = detect_objects_by_color(frame, focus_color_index)
    elif focus_method == "size":
        cv2.putText(frame, f"Sorting by: Size", (1, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)
        processed_frame, size_detected = detect_objects_by_size(frame)
    else:
        color_detected = False
        size_detected = False


    cv2.imshow('Detected Objects', processed_frame)
    cv2.imshow("red", maskTest)
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

cap.release()
cv2.destroyAllWindows()
import cv2
import numpy as np

def detect_objects(frame):
    # Convert the frame from BGR to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for each color
    lower_yellow = np.array([20, 50, 50])
    upper_yellow = np.array([35, 255, 255])

    lower_green = np.array([80, 101, 0])
    upper_green = np.array([98, 255, 255])

    lower_blue = np.array([95, 50, 50])
    upper_blue = np.array([130, 255, 255])

    lower_red = np.array([0, 50, 50])
    upper_red = np.array([7, 255, 255])
    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    # Threshold the HSV image to get only specific colors
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_red1 = cv2.inRange(hsv, lower_red, upper_red)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.add(mask_red1, mask_red2)

    # Bitwise-AND masks to get specific color regions
    yellow_result = cv2.bitwise_and(frame, frame, mask=mask_yellow)
    green_result = cv2.bitwise_and(frame, frame, mask=mask_green)
    blue_result = cv2.bitwise_and(frame, frame, mask=mask_blue)
    red_result = cv2.bitwise_and(frame, frame, mask=mask_red)

    # Combine all Masks.
    combined_mask = cv2.add(red_result, blue_result)
    combined_mask = cv2.add(combined_mask, green_result)
    combined_mask = cv2.add(combined_mask, yellow_result)

    # Convert the combined mask to grayscale
    gray = cv2.cvtColor(combined_mask, cv2.COLOR_BGR2GRAY)

    # Detect corners using Harris Corner detection
    corners = cv2.cornerHarris(gray, 2, 3, 0.04)

    # Dilate corners to mark them
    corners = cv2.dilate(corners, None, iterations=20)

    # Threshold to get only strong corners
    threshold = 0.1 * corners.max()
    frame_with_corners = frame.copy()

    # Mark detected corners on the frame
    frame_with_corners[corners > threshold] = [0, 0, 255]  # Mark corners in red

    return frame_with_corners

# Open a connection to the webcam
cap = cv2.VideoCapture(1)

while True:
    # Read frames from the webcam
    ret, frame = cap.read()

    # Call the detect_objects function to get the processed frame with corners marked
    processed_frame = detect_objects(frame)

    # Display the processed frame
    cv2.imshow('Color Detection with Corners', processed_frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
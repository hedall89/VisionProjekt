import socket
import threading
import time
import ur

HOST = '192.168.0.10'  # The remote host (ip of the ur-robot)
PORT1 = 30002  # Port number (30001 or 30002)
robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect_to_robot(robot_ip, robot_port):
    robot_socket.connect((robot_ip, robot_port))
    return robot_socket

def pickup_crate():
    f = open("scripts/pickup_crate.script", "rb")
    l = f.read(1024)
    while l:
        robot_socket.send(l)
        l = f.read(1024)


def Vacuum(Width, robot_socket):
    if Width == 'ON':
        print("Turning vacuum ON")
        f = open("scripts/VG10_ON.script", "rb")
        l = f.read(1024)
        while l:
            robot_socket.send(l)
            l = f.read(1024)
        print("Vacuum ON script sent")
    elif Width == 'OFF':
        print("Turning vacuum OFF")
        f = open("scripts/VG10_OFF.script", "rb")
        l = f.read(1024)
        while l:
            robot_socket.send(l)
            l = f.read(1024)
    else:
        print("Invalid command")
    return

def move_joints(q):
    Movement = 'movej' + "(" + str(q) + ")" + "\n"
    Movement_encoded = Movement.encode()
    return Movement_encoded

def move_linear(q):
    Movement = 'movel' + "(p" + str(q) + ")" + "\n"
    Movement_encoded = Movement.encode()
    return Movement_encoded


def move_position_linear(robotsocket, position, color):

    print(f"Moving to pick up {color} at position: {position}")
    time.sleep(1)
    ur_state = ur.UR_RobotState(robotsocket)
    ur_state.start()

    def check_program_running():
        time.sleep(0.2)
        while ur_state.is_program_running():
            time.sleep(0.1)

        print("Move completed")

    # Start a thread to check if the robot is still moving
    thread = threading.Thread(target=check_program_running)
    thread.start()

    # Perform the movement
    position = move_linear(position)
    robotsocket.send(position)

    # Wait for the thread to finish
    thread.join()

    ur_state.stop()

def move_to_position(robotsocket, position, moveto):
    print(f"Moving to {moveto} position")
    ur_state = ur.UR_RobotState(robotsocket)
    ur_state.start()

    def check_program_running():
        time.sleep(0.2)
        while ur_state.is_program_running():
            time.sleep(0.1)

        print("Move completed")

    # Start a thread to check if the robot is still moving
    thread = threading.Thread(target=check_program_running)
    thread.start()

    # Perform the movement
    position = move_joints(position)
    robotsocket.send(position)

    # Wait for the thread to finish
    thread.join()

    ur_state.stop()

def calculate_position_color(x_pix,y_pix):
    # robot
    robot_max_x = 485
    robot_min_x = 175
    robot_max_y = -135
    robot_min_y = 100

    #pixel
    pixel_max_x = 640
    pixel_min_x = 0
    pixel_max_y = 480
    pixel_min_y = 0


    range_x = robot_max_x - robot_min_x
    range_y = robot_max_y - robot_min_y

    y_scale = range_y / pixel_max_y
    x_scale = range_x / pixel_max_x

    point_X = (robot_max_x - x_pix * x_scale) / 1000
    point_y = (robot_max_y - y_pix * y_scale) / 1000
    point_z = 138 / 1000
    RX = 3.140
    RY = 0.031
    RZ = 0.036


    return [point_X, point_y, point_z, RX, RY, RZ]


def calculate_position_size(x_pix, y_pix, area):
    # robot mm
    robot_max_x = 485
    robot_min_x = 175
    robot_max_y = -135
    robot_min_y = 100

    #pixel
    pixel_max_x = 640
    pixel_min_x = 0
    pixel_max_y = 480
    pixel_min_y = 0

    range_x = robot_max_x - robot_min_x
    range_y = robot_max_y - robot_min_y

    y_scale = range_y / pixel_max_y
    x_scale = range_x / pixel_max_x

    point_x = (robot_max_x - x_pix * x_scale) / 1000
    point_y = (robot_max_y - y_pix * y_scale) / 1000
    RX = 3.140
    RY = 0.031
    RZ = 0.036

    if area >= 9999:
        point_z = 138 / 1000
    elif area > 5600 and area < 9900:
        point_z = 128 / 1000
    else:
        point_z = 119 / 1000

    return [point_x, point_y, point_z, RX, RY, RZ]


def move_up_in_z(robotsocket, delta_z):
    print("Moving up in Z")
    ur_state = ur.UR_RobotState(robotsocket)
    ur_state.start()
    def check_program_running():
        time.sleep(1)
        while ur_state.is_program_running():
            time.sleep(0.1)
        print("Move completed")

    # Start a thread to check if the robot is still moving
    thread = threading.Thread(target=check_program_running)
    thread.start()

    # Get the current joint positions
    current_positions = ur_state.get_tcp_pose()
    # Updater Z-axis position
    current_positions[2] += delta_z  # Assuming Z-axis is the third joint (0-indexed)

    # Send the URScript command to the robot
    position = move_linear(current_positions)
    #print(position)
    robotsocket.send(position)

    # Wait for the thread to finish
    thread.join()

    ur_state.stop()








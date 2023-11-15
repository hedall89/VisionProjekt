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


def Read_Script(Width, robot_socket):
    if Width == 'ON':
        print("Turning vacuum ON")
        f = open("VG10_ON.script", "rb")
        l = f.read(1024)
        while l:
            robot_socket.send(l)
            l = f.read(1024)
        print("Vacuum ON script sent")
    elif Width == 'OFF':
        print("Turning vacuum OFF")
        f = open("VG10_OFF.script", "rb")
        l = f.read(1024)
        while l:
            robot_socket.send(l)
            l = f.read(1024)
        #print("Vacuum OFF script sent")
    else:
        print("Invalid command")
    return

def move_joints(q):
    Movement = 'movej' + "(" + str(q) + ")" + "\n"
    Movement_encoded = Movement.encode()
    return Movement_encoded

def move_linear(q):
    Movement = 'movel' + "(p" + str(q) + ")" + "\n"
    #print(Movement)
    Movement_encoded = Movement.encode()
    return Movement_encoded


def move_linear_point(q, a, v):
    Movement = 'movej' + "(p" + str(q) + ", a=" + str(a) + ", v=" + str(v) + ")" + "\n"
    # print(Movement)
    Movement_encoded = Movement.encode()
    return Movement_encoded

def move_position_linear(robotsocket, position):
    print("Moving to pick up position", position)
    time.sleep(1)
    ur_state = ur.UR_RobotState(robotsocket)
    ur_state.start()

    def check_program_running():
        time.sleep(0.1)
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

def move_to_position(robotsocket, position):
    print("Moving to position: General move J")
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
    robot_max_x = 447
    robot_min_x = 211
    robot_max_y = -128
    robot_min_y = 114

    #pixel
    pixel_max_x = 470
    pixel_min_x = 0
    pixel_max_y = 480
    pixel_min_y = 0


    range_x = robot_max_x - robot_min_x
    range_y = robot_max_y - robot_min_y

    y_scale = range_y / pixel_max_y
    x_scale = range_x / pixel_max_x

    point_X = (robot_max_x - x_pix * x_scale) / 1000
    point_y = (robot_max_y - y_pix * y_scale) / 1000
    point_z = 113 / 1000
    RX = 3.140
    RY = 0.031
    RZ = 0.036
    print(point_X,point_y,point_z,RX,RY,RZ)

    return [point_X, point_y, point_z, RX, RY, RZ]


def calculate_position_size(x_pix, y_pix, area):
    # robot
    robot_max_x = 447
    robot_min_x = 211
    robot_max_y = -128
    robot_min_y = 114

    #pixel
    pixel_max_x = 470
    pixel_min_x = 0
    pixel_max_y = 480
    pixel_min_y = 0


    range_x = robot_max_x - robot_min_x
    range_y = robot_max_y - robot_min_y

    y_scale = range_y / pixel_max_y
    x_scale = range_x / pixel_max_x

    point_X = (robot_max_x - x_pix * x_scale) / 1000
    point_y = (robot_max_y - y_pix * y_scale) / 1000
    RX = 3.140
    RY = 0.031
    RZ = 0.036

    if area >= 9000:
        point_z = 113 / 1000
    elif area > 5000 and area < 9000:
        point_z = 102 / 1000
    else:
        point_z = 90 / 1000


    print(point_X, point_y, point_z, RX, RY, RZ)

    return [point_X, point_y, point_z, RX, RY, RZ]


def move_up_in_z(robotsocket, delta_z):
    print("Moving up in Z")
    ur_state = ur.UR_RobotState(robotsocket)
    ur_state.start()
    def check_program_running():
        while ur_state.is_program_running():
            time.sleep(0.1)
        print("Move completed")

    # Start a thread to check if the robot is still moving
    thread = threading.Thread(target=check_program_running)
    thread.start()

    # Get the current joint positions
    current_positions = ur_state.get_tcp_pose()
    print(current_positions)
    # Update the Z-axis position
    current_positions[2] += delta_z  # Assuming Z-axis is the third joint (0-indexed)
    print(current_positions[2])



    # Send the URScript command to the robot
    position = move_linear(current_positions)
    print(position)
    robotsocket.send(position)

    # Wait for the thread to finish
    thread.join()

    ur_state.stop()








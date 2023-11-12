import asyncio
import socket
import time
import ur

HOST = '192.168.0.10'  # The remote host (ip of the ur-robot)
PORT1 = 30002  # Port number (30001 or 30002)
robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect_to_robot(robot_ip, robot_port):
    robot_socket.connect((robot_ip, robot_port))
    return robot_socket


def Read_Script(Width):
    if(Width == 'ON'):
        print("ON")
        f = open("VG10_ON.script", "rb")
        l = f.read(1024)
        while (l):
            robot_socket.send(l)
            l = f.read(1024)
    elif(Width == 'OFF'):
        print("OFF")
        f = open("VG10_OFF.script", "rb")
        l = f.read(1024)
        while (l):
            robot_socket.send(l)
            l = f.read(1024)
    else:
        pass
    return


def vacuum_off():
    command = "set_digital_out(0, False)\n"
    robot_socket.sendall(command.encode())
    time.sleep(1)


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

def move_position_linear(robotsocket,position):
    print("using linear movement")
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:  # Create socket for TCP/IP
    # s1.connect((HOST, PORT1))  # Connect socket to remote host
    print("Connected")  # if "Connected" is printed in the console, then connection has been established
    ur_state = ur.UR_RobotState(robotsocket)
    ur_state.start()
    time.sleep(1)
    position = move_linear(position)
    robotsocket.send(position)  # Base = 0, shoulder =90, elbow=-90 wrist1=180, wrist2=-90, wrist3= 90
    time.sleep(5)
    print("Is Robot moving to pos_1 ", ur_state.is_program_running())
    time.sleep(1)
    while ur_state.is_program_running():  # Check if robot is performing a move
        time.sleep(0.1)  # wait 5 seconds to complete move
    print("Move to pos_1 completed")

def move_to_position(robotsocket, position, position2=None):
    print("using 2 positions")
    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:  # Create socket for TCP/IP
    #s1.connect((HOST, PORT1))  # Connect socket to remote host
    print("Connected")  # if "Connected" is printed in the console, then connection has been established
    ur_state = ur.UR_RobotState(robotsocket)
    ur_state.start()
    time.sleep(1)
    position = move_joints(position)
    # Robot Feature: BASE
    robotsocket.send(position)  # Base = 0, shoulder =90, elbow=-90 wrist1=180, wrist2=-90, wrist3= 90
    time.sleep(5)
    print("Is Robot moving to pos_1 ", ur_state.is_program_running())
    time.sleep(1)
    while ur_state.is_program_running():  # Check if robot is performing a move
        time.sleep(0.1)  # wait 5 seconds to complete move
    print("Move to pos_1 completed")

    if position2 is not None:

        position2 = move_linear_point(position2, 0.5, 0.5)
        robotsocket.send(position2)
        time.sleep(1)
        print("Is Robot moving to pos_2 ", ur_state.is_program_running())
        while ur_state.is_program_running():  # Check if robot is performing a move
            time.sleep(0.1)  # wait 5 seconds to complete move
        print("Move to pos_2 completed")


def calculate_position(x_pix,y_pix,):
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
    point_z = 135 / 1000
    RX = 3.140
    RY = 0.031
    RZ = 0.036


    return [point_X, point_y, point_z, RX, RY, RZ ]









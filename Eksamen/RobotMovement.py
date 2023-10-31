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


def vacuum_on():
    command = "set_digital_out(0, True)\n"
    robot_socket.sendall(command.encode())
    time.sleep(1)


def vacuum_off():
    command = "set_digital_out(0, False)\n"
    robot_socket.sendall(command.encode())
    time.sleep(1)


def move_joints(q):
    Movement = 'movej' + "(" + str(q) + ")" + "\n"
    Movement_encoded = Movement.encode()
    return Movement_encoded

def move_linear(q, a, v):
    Movement = 'movel' + "(p" + str(q) + ", a=" + str(a) + ", v=" + str(v) + ")" + "\n"
    #print(Movement)
    Movement_encoded = Movement.encode()
    return Movement_encoded

def move_linear_point(q, a, v):
    Movement = 'movel' + "(" + str(q) + ", a=" + str(a) + ", v=" + str(v) + ")" + "\n"
    #print(Movement)
    Movement_encoded = Movement.encode()
    return Movement_encoded


def move_to_position(robotsocket, position, position2=None):
    print("using 2 positions")
    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:  # Create socket for TCP/IP
    #s1.connect((HOST, PORT1))  # Connect socket to remote host
    print("Connected")  # if "Connected" is printed in the console, then connection has been established
    ur_state = ur.UR_RobotState(robotsocket)
    ur_state.start()
    #time.sleep(1)
    position = move_joints(position)
    # Robot Feature: BASE
    robotsocket.send(position)  # Base = 0, shoulder =90, elbow=-90 wrist1=180, wrist2=-90, wrist3= 90
    #time.sleep(1)
    print("Is Robot moving to pos_1 ", ur_state.is_program_running())
    time.sleep(0.1)
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






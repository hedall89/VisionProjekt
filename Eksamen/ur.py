# UR_RobotState v1.1
# Collects data from Universal Robot's RobotState packet
# Written for educational purposes - University College Lillebælt, Erhvervsakademi og Professionshøjskole

import threading
import struct
import math
import warnings


class UR_RobotState(threading.Thread):
    _ur_socket = None
    _data = None
    _running = False

    def __init__(self, ur_socket):
        super(UR_RobotState, self).__init__()
        self._ur_socket = ur_socket

    def run(self):
        self._running = True
        while True and self._running:
            data_tmp = self._ur_socket.recv(4096)
            if struct.unpack('!b', data_tmp[4:5])[0] == 16:
                self._data = data_tmp

    def stop(self):
        self._running = False

    def _get_sub_package(self, value):
        while not self._data:
            pass
        package_length = struct.unpack('!i', self._data[0:4])[0]
        i = 5
        while i + 5 < package_length:
            sub_package_length = struct.unpack('!i', self._data[i:i + 4])[0]
            sub_package_type = struct.unpack('!b', self._data[i + 4:i + 5])[0]
            if sub_package_type == value:
                return self._data[i:i + sub_package_length], sub_package_length
            i += sub_package_length
        warnings.warn("ERROR: Sub-package " + str(value) + " not found!")
        return None, None

    def _int_to_bin(self, value, digits=8):
        binary = [0] * digits
        for i in range(digits):
            bin_value = int(math.pow(2, i))
            if value & bin_value:
                binary[i] = 1
                value -= bin_value
        return binary

    def is_physical_robot_connected(self):
        # Returns True if physical robot is connected, otherwise returns False
        sub_package, sub_package_length = self._get_sub_package(0)
        return struct.unpack('!?', sub_package[13:14])[0]

    def is_real_robot_enabled(self):
        # Returns True if Real Robot is enabled, otherwise returns False
        sub_package, sub_package_length = self._get_sub_package(0)
        return struct.unpack('!?', sub_package[14:15])[0]

    def is_robot_power_on(self):
        # Returns True if the Robot Power is on, otherwise returns False
        sub_package, sub_package_length = self._get_sub_package(0)
        return struct.unpack('!?', sub_package[15:16])[0]

    def is_emergency_stop_on(self):
        # Returns True if Emergency Stop is pushed, otherwise returns False
        sub_package, sub_package_length = self._get_sub_package(0)
        return struct.unpack('!?', sub_package[16:17])[0]

    def is_protective_stop_on(self):
        # Returns True if Protective Stop is on, otherwise returns False
        sub_package, sub_package_length = self._get_sub_package(0)
        return struct.unpack('!?', sub_package[17:18])[0]

    def is_program_running(self):
        # Returns True if Robot Program is running, otherwise returns False
        sub_package, sub_package_length = self._get_sub_package(0)
        return struct.unpack('!?', sub_package[18:19])[0]

    def is_program_paused(self):
        # Returns True if Robot Program is paused, otherwise returns False
        sub_package, sub_package_length = self._get_sub_package(0)
        return struct.unpack('!?', sub_package[19:20])[0]

    def get_actual_joint_positions(self):
        # Returns 6D vector containing actual joint angles in Radians
        sub_package, sub_package_length = self._get_sub_package(1)
        joint_positions = []
        for i in range(6):
            packet_index = 5 + i * 41
            joint_positions.append(struct.unpack('!d', sub_package[packet_index:packet_index + 8])[0])
        return joint_positions

    def get_target_joint_positions(self):
        # Returns 6D vector containing target joint angles in Radians
        sub_package, sub_package_length = self._get_sub_package(1)
        target_joint_positions = []
        for i in range(6):
            packet_index = 13 + i * 41
            target_joint_positions.append(struct.unpack('!d', sub_package[packet_index:packet_index + 8])[0])
        return target_joint_positions

    def get_actual_joint_speed(self):
        # Returns 6D vector containing actual joint speeds
        sub_package, sub_package_length = self._get_sub_package(1)
        joint_speed = []
        for i in range(6):
            packet_index = 21 + i * 41
            joint_speed.append(struct.unpack('!d', sub_package[packet_index:packet_index + 8])[0])
        return joint_speed

    def get_joint_motor_temperature(self):
        # Returns 6D vector containing the temperature of each joint
        sub_package, sub_package_length = self._get_sub_package(1)
        joint_speed = []
        for i in range(6):
            packet_index = 37 + i * 41
            joint_speed.append(struct.unpack('!d', sub_package[packet_index:packet_index + 4])[0])
        return joint_speed

    def get_digital_input(self):
        # Returns 2x 8D vectors and 1x 2D vector representing Digital Input, Configurable Input, and Tool Input
        sub_package, sub_package_length = self._get_sub_package(3)
        digital_input_bits = struct.unpack('!i', sub_package[5:9])[0]
        digital_input = self._int_to_bin(digital_input_bits & 255)
        configurable_input = self._int_to_bin((digital_input_bits & (255 << 8)) >> 8)
        tool_input = self._int_to_bin((digital_input_bits & (3 << 16)) >> 16, 2)
        return digital_input, configurable_input, tool_input

    def get_digital_output(self):
        # Returns 2x 8D vectors and 1x 2D vector representing Digital Output, Configurable Output, and Tool Output
        sub_package, sub_package_length = self._get_sub_package(3)
        digital_output_bits = struct.unpack('!i', sub_package[9:13])[0]
        digital_output = self._int_to_bin(digital_output_bits & 255)
        configurable_output = self._int_to_bin((digital_output_bits & (255 << 8)) >> 8)
        tool_output = self._int_to_bin((digital_output_bits & (3 << 16)) >> 16, 2)
        return digital_output, configurable_output, tool_output

    def get_tcp_pose(self):
        # Returns 6D Vector containing actual TCP Pose in Cartesian Space
        sub_package, sub_package_length = self._get_sub_package(4)
        tcp_pose = []
        for i in range(6):
            packet_index = 5 + i * 8
            tcp_pose.append(struct.unpack('!d', sub_package[packet_index:packet_index + 8])[0])
        return tcp_pose

"""!
@file control.py
This file contains the P controller used to drive the motor
to a position
"""
import pyb
import utime


class Control:
    """!
    The class used for the controller of the motor. This class sets up
    initial conditions of the motor, calculates the error between
    current position and desired position, and returns the motor effort.
    """
    def __init__(self, Kp, setpoint, initial_output):
        """!
        The initial state of the controller. Sets up the initial conditions of the
        passed through motor
        :param Kp: The proportional controller gain for the motor, used to determine
        the motor effort.
        :param setpoint: The desired position of the encoder that was set.
        :param initial_output: The initial position of the passed through device
        """
        self.t_start = utime.ticks_ms()
        self.Kp = Kp
        self.setpoint = setpoint
        self.output = initial_output
        self.times = []
        self.positions = []

    def run(self, setpoint, measured_output):
        """!
        Calculates the error between the current encoder position and the desired
        encoder position and returns the motor effort.
        :param setpoint: The desired position of the encoder that was set.
        :param measured_output: The measured position of the encoder
        :return: The motor effort
        """
        error = setpoint - measured_output
        motor_actuation = self.Kp * error
        return motor_actuation

    def set_setpoint(self, setpoint):
        """!
        Sets the value of setpoint to be part of self.
        """
        self.setpoint = setpoint

    def set_Kp(self, Kp):
        """!
        Sets the value of Kp to be part of self.
        """
        self.Kp = Kp

    def print_time(self):
        """!
        Prints the encoder's position along with the current time.
        """
        for i in range(len(self.times)):
            print("{}, {}".format(self.times[i], self.positions[i]))

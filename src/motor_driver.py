"""!
@file motor_driver.py
This file contains the code used to drive the motor at a
specified percent power in a specified direction.
"""
import pyb


class MotorDriver:
    """!
    This class implements a motor driver for an ME405 kit.
    """

    def __init__(self, en_pin, in1pin, in2pin, timer):
        """!
        Creates a motor driver by initializing GPIO
        pins and turning off the motor for safety.
        @param en_pin GPIO pin that enables the motor to run
        @param in1pin GPIO pin number for the first motor output pin
        @param in2pin GPIO pin number for the second motor output pin
        @param in1pin GPIO pin number for the first motor output pin
        @param timer GPIO pin for the time that is used in running the motor
        """
        # initialize GPIO
        self.enable_motor = pyb.Pin(en_pin, pyb.Pin.OUT_PP)
        self.pin_1 = pyb.Pin(in1pin, pyb.Pin.OUT_PP)
        self.pin_2 = pyb.Pin(in2pin, pyb.Pin.OUT_PP)
        self.timer = pyb.Timer(timer, freq=20000)
        self.ch_1 = self.timer.channel(1, pyb.Timer.PWM, pin=self.pin_1)
        self.ch_2 = self.timer.channel(2, pyb.Timer.PWM, pin=self.pin_2)
        # initialize the motors to have 0 speed
        self.enable_motor.value(True)
        self.ch_1.pulse_width_percent(0)
        self.ch_2.pulse_width_percent(0)

    def set_duty_cycle(self, level):
        """!
        This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
                cycle of the voltage sent to the motor
        """
        #
        if level < 0:
            level = level * -1
            self.ch_1.pulse_width_percent(0)
            self.ch_2.pulse_width_percent(level)
        elif level > 0:
            self.ch_1.pulse_width_percent(level)
            self.ch_2.pulse_width_percent(0)
        else:
            self.ch_1.pulse_width_percent(0)
            self.ch_2.pulse_width_percent(0)
            self.ch_2.pulse_width_percent(0)

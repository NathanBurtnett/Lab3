"""!
@file basic_tasks.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

@author JR Ridgely
@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

import gc
import pyb
import sys

import utime

import cotask
import task_share
from encoder_reader import EncoderReader
from control import Control
import boot
from motor_driver import MotorDriver


def get_inumeric_input(prompt):
    """!
    Takes the input "prompt" and tries to return as an integer value.
    If the try fails, an error will be printed.
    :param prompt: The input to be changed into an integer value.
    :return: An integer value.
    """
    while True:
        try:
            print(prompt)
            i = input()
            return int(i)

        except ValueError:
            print("Invalid number")

        except KeyboardInterrupt:
            sys.exit(0)
        except EOFError:
            sys.exit(0)


def get_fnumeric_input(prompt):
    """!
    Takes the input "prompt" and tries to return as a float value.
    If the try fails, an error will be printed.
    :param prompt: The input to be changed into a float value.
    :return: A float value.
    """
    while True:
        try:
            print(prompt)
            i = input()
            return float(i)

        except ValueError:
            print("Invalid number")

        except KeyboardInterrupt:
            sys.exit(0)
        except EOFError:
            sys.exit(0)


# Share function created by JR Ridgely
def task1_fun(shares):
    kp, setpoint, data, reset = shares

    # Create the motor and motor encoder objects
    m0 = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    enc0 = EncoderReader(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4)

    while True:
        con = Control(kp.get(), setpoint.get(), initial_output=0)

        while reset.get() == 0:
            con.set_setpoint(setpoint.get())
            con.set_Kp(kp.get())

            measured_output = -enc0.read()
            motor_actuation = con.run(setpoint.get(), measured_output)
            m0.set_duty_cycle(motor_actuation)

            data.put(measured_output)
            yield 0

        # Reset
        enc0.zero()
        m0.set_duty_cycle(0)
        yield 0


# Share function created by JR Ridgely
def task2_fun(shares):
    kp, setpoint, data, reset = shares

    # Create the motor and motor encoder objects
    enc1 = EncoderReader(pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8)
    m1 = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)

    while True:
        con = Control(kp.get(), setpoint.get(), initial_output=0)

        while reset.get() == 0:
            con.set_setpoint(setpoint.get())
            con.set_Kp(kp.get())

            measured_output = -enc1.read()
            motor_actuation = con.run(setpoint.get(), measured_output)
            m1.set_duty_cycle(motor_actuation)

            data.put(measured_output)
            yield 0

        # Reset
        enc1.zero()
        m1.set_duty_cycle(0)
        yield 0


# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")

    # Create a share and a queue to test function and diagnostic printouts
    m0Kp = task_share.Share('f', thread_protect=False, name="m0 kp")
    m1Kp = task_share.Share('f', thread_protect=False, name="m1 kp")

    reset = task_share.Share('b', thread_protect=False, name="reset")

    m0setpoint = task_share.Share('l', thread_protect=False,
                                  name="m0 setpoint")
    m1setpoint = task_share.Share('l', thread_protect=False,
                                  name="m1 setpoint")

    m0Data = task_share.Queue('L', 1000, thread_protect=False,
                              overwrite=True,
                              name="M0 data")
    m1Data = task_share.Queue('L', 1000, thread_protect=False,
                              overwrite=True,
                              name="M1 data")
    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed

    task_list = cotask.TaskList()
    m0Task = cotask.Task(task1_fun, name="Motor 0 Driver", priority=1,
                         period=10,
                         profile=True, trace=False,
                         shares=(m0Kp, m0setpoint, m0Data, reset))

    m1Task = cotask.Task(task2_fun, name="Motor 1 Driver", priority=1,
                         period=10,
                         profile=True, trace=False,
                         shares=(m1Kp, m1setpoint, m1Data, reset))

    task_list.append(m0Task)
    task_list.append(m1Task)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    print("Starting tasks!")
    while True:
        print("?????")
        m0Kp.put(get_fnumeric_input("$a Set Motor 0 kp: "))
        m1Kp.put(get_fnumeric_input("$b Set Motor 1 kp: "))
        print("?????")

        m0setpoint.put(get_inumeric_input("$c Set Motor 0 setpoint: "))
        m1setpoint.put(get_inumeric_input("$d Set Motor 1 setpoint: "))

        per = get_inumeric_input("$e Enter Task Period: ")

        m0Task.set_period(per)
        m1Task.set_period(per)

        m0Data.clear()
        m1Data.clear()
        m0Task.reset_profile()
        m1Task.reset_profile()

        s = utime.ticks_ms()
        while utime.ticks_ms() - s < 1000:
            task_list.pri_sched()

        # Print data
        print("$f M0 data")
        for _ in range(m0Data.num_in()):
            print(m0Data.get())
        print("$g End Data")

        print("$h M1 data")
        for _ in range(m1Data.num_in()):
            print(m1Data.get())
        print("$i End Data")

        reset.put(1)
        s = utime.ticks_ms()
        while utime.ticks_ms() - s < 1000:
            task_list.pri_sched()

        reset.put(0)

    # Print a table of task data and a table of shared information data
    print('\n' + str(cotask.task_list))
    print(task_share.show_all())
    print(m0Task.get_trace())
    print(m1Task.get_trace())
    print('')

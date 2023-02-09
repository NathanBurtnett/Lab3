"""!
@file plot.py
Commands main.py on the nucleo to run multiple step responses
and plots the results.
"""
import serial
import matplotlib.pyplot as plt
import time


def wait_for_tok(ser, tok):
    """!
    Reads the serial output from the microcontroller and waits
    for the token that is located at various lines in order to
    keep track of when specific lines are produced
    :param ser: The serial of the connection between microcontroller
    and the computer.
    :param tok: The specified token as seen in run_step_response
    """
    r = ""
    while not r.startswith(tok):
        r = ser.readline().decode("ascii")
        print(f"SER: {r}", end="")


def init_board(ser):
    """!
    Initialises the board for serial output
    :param ser: The serial value to be passed into the function
    """
    print("initializing board...")

    s.write(b'\x03')
    time.sleep(1)

    s.reset_input_buffer()

    s.write(b'\x04')


def proc_lines(csv_lines):
    """!
    Takes the lines from the passed csv file and readies it for plotting
    :param csv_lines: The passed through file to be plotted.
    :return: The x and y values to be plotted
    """
    x = [float(l.split(",")[0].strip()) for l in csv_lines]
    y = [float(l.split(",")[1].strip()) for l in csv_lines]

    return x, y


def run_step_response(s, kP, setpoint, num_pts=250):
    """!
    Runs the step response of the motor.
    :param s: The serial value of the connecting wire
    :param kP: The proportional controller gain for the motor
    :param setpoint: The desired encoder position
    :param num_pts: The maximum number of points wanted for the plot
    :return: The csv file to be plotted
    """
    # Kp token
    wait_for_tok(s, "$A")
    s.write(bytes(f"{kP}\r\n", 'ascii'))

    # setpoint token
    wait_for_tok(s, "$B")
    s.write(bytes(f"{setpoint}\r\n", 'ascii'))

    wait_for_tok(s, "$E")
    s.write(bytes(f"{num_pts}\r\n", 'ascii'))

    wait_for_tok(s, "$C")
    print("Getting CSV")

    r = ""
    csv = []
    while True:
        r = s.readline().decode("ascii").strip()
        if r.startswith("$D"):
            break
        csv.append(r)

    return csv


# Sets the serial channel and baud rate of the connection
with serial.Serial('COM3', baudrate=115200) as s:
    init_board(s)

    plt.plot(*proc_lines(run_step_response(s, .0025, 16000)), label="Kp=0.0025")
    plt.plot(*proc_lines(run_step_response(s, .005, 16000)), label="Kp=0.005")
    plt.plot(*proc_lines(run_step_response(s, .02, 16000)), label="Kp=0.02")

    plt.legend(loc='lower right')
    plt.xlabel("Time (ms)")
    plt.ylabel("Position (enc count)")
    plt.title("Step Response")
    plt.savefig("plot.png")
    plt.show()

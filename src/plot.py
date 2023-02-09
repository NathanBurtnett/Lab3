"""!
@file plot.py
Commands main.py on the nucleo to run multiple step responses
and plots the results.
"""
import serial
import matplotlib.pyplot as plt
import time
import utime


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

def write_ctrl_c(s):
    s.write(b'\x03')

def write_ctrl_d(s):
    s.write(b'\x04')

def init_board(ser):
    """!
    Initialises the board for serial output
    :param ser: The serial value to be passed into the function
    """
    print("initializing board...")

    # Make sure program is dead...
    for _ in range(5):
        write_ctrl_c(s)

    time.sleep(.5)

    s.reset_input_buffer()

    # Reset board
    write_ctrl_d(s)


def proc_lines(csv_lines):
    """!
    Takes the lines from the passed csv file and readies it for plotting
    :param csv_lines: The passed through file to be plotted.
    :return: The x and y values to be plotted
    """
    x = [float(l.split(",")[0].strip()) for l in csv_lines]
    y = [float(l.split(",")[1].strip()) for l in csv_lines]

    return x, y

def write(ser, val):
    ser.write(bytes(f"{val}\r\n", 'ascii'))

def write_to_tok(s, tok, v):
    wait_for_tok(s, tok)
    write(s, v)

def read_csv(end_tok):
    r = ""
    csv = []
    while True:
        r = s.readline().decode("ascii").strip()
        if r.startswith(end_tok):
            break
        csv.append(r)
    return csv
def run_step_response(s, kPs, setpoints, period):
    """!
    Runs the step response of the motor.
    :param s: The serial value of the connecting wire
    :param kP: The proportional controller gain for the motor
    :param setpoint: The desired encoder position
    :param num_pts: The maximum number of points wanted for the plot
    :return: The csv file to be plotted
    """
    # Kp token
    m0, m1 = kPs
    write_to_tok(s, "$a", m0)
    write_to_tok(s, "$b", m1)

    # setpoint token
    m0, m1 = setpoints
    write_to_tok(s, "$c", m0)
    write_to_tok(s, "$d", m1)

    # Period
    write_to_tok(s, "$e", period)

    # TODO: Fix this?
    time.sleep(5)

    # Exit response loop
    write_ctrl_c(s)
    print("Getting CSV")

    wait_for_tok(s, "$f")
    m0_csv = read_csv("$g")

    wait_for_tok(s, "$h")
    m1_csv = read_csv("$i")

    return m0_csv, m1_csv


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

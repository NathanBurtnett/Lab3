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

    # Make sure program is dead...
    s.write(b'\x03\x03\x03\x03\x03\x03')

    ser.read_all()

    time.sleep(2)

    s.reset_input_buffer()

    # Reset board
    # Reset boardd
    s.write(b'\x04')
    print("INIT FINISHED")


def write(ser, val):
    """!
    Writes the byte value of the input for
    serial communication
    :param ser: The serial object
    :param val: The value to be written
    """
    ser.write(bytes(f"{val}\r\n", 'ascii'))


def write_to_tok(s, tok, v):
    """!
    Waits for and writes the token that
    will tell the code what is being
    written in the terminal
    :param s: The serial object
    :param tok: The token to be checked
    :param v:
    :return:
    """
    wait_for_tok(s, tok)
    write(s, v)


def read_csv(end_tok):
    """!
    Creates a csv array for encoder values if
    the end token is passed through.
    :param end_tok: The token pertaining to the
    end of the encoder data.
    :return: The csv array
    """
    r = ""
    csv = []
    while True:
        r = s.readline().decode("ascii").strip()
        if r.startswith(end_tok):
            break
        csv.append(r)
    return csv


def run_step_response(s, kPs, setpoints, period, t_tot=1):
    """!
    Runs the step response of the motor.
    :param s: The serial value of the connecting wire
    :param kP: The proportional controller gain for the motor
    :param setpoint: The desired encoder position
    :param num_pts: The maximum number of points wanted for the plot
    :return: The csv file to be plotted
    """
    # Kp tokenz
    print("Doing step response")
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
    time.sleep(t_tot)

    wait_for_tok(s, "$f")
    m0_csv = read_csv("$g")

    wait_for_tok(s, "$h")
    m1_csv = read_csv("$i")

    return m0_csv, m1_csv


def plot_period_tests(s, periods):
    """!
    Takes the data from the serial object and
    plots the graph for the step response.
    :param s: The serial object
    :param periods: The period of the task
    :return: A plot of the step response.
    """
    sp = 16000
    for p in periods:
        m0, m1 = run_step_response(s, (.05, 0), (sp, 0), p)
        m0 = [int(m) if -4294967 < int(m) < 4294967 else 0 for m in m0]
        print(m0)

        t = list(range(0, len(m0) * p, p))

        plt.plot(t, m0, label=f"period={p}")
        # time.sleep(1)

    plt.legend(loc='lower right')
    plt.xlabel("Time (ms)")
    plt.ylabel("Position (enc count)")
    plt.title("Step Response")
    plt.savefig("periods.png")
    plt.show()


def position_tests(s, m0_poss, m1_poss, per):
    """!
    The test that runs both motors simultaneously
    to the specified encoder counts.
    :param s: The serial object
    :param m0_poss: The first motor's current encoder count
    :param m1_poss: The second motor's current encoder count
    :param per: The passed period of the task
    :return: Appended lists of the encoder positions
    """
    m0_tot = []
    m1_tot = []
    for p in zip(m0_poss, m1_poss):
        m0, m1 = run_step_response(s, (.05, .05), p, per)
        m0, m1 = [int(m) for m in m0], [int(m) for m in m1]

        m0_tot.append(m0)
        m1_tot.append(m1)


# Sets the serial channel and baud rate of the connection
with serial.Serial('COM5', baudrate=115200) as s:
    init_board(s)

    plot_period_tests(s, [10, 25, 40, 60, 100])

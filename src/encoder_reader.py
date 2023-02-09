"""!
@file control.py
Contains the EncoderReader class which is used to track the position of an
encoder.
"""
import pyb

ENC_MAX = 0xFFFF


class EncoderReader:
    count = 0
    last_raw_cnt = 0

    def __init__(self, pin_a, pin_b, timer):
        """!
        Creates an encoder reader on the passed pin names and
        timer number.
        @param pin_a The first input pin to be assigned by the encoder.
        @param pin_b The second input pin to be assigned by the encoder.
        @param timer The passed timer channel.
        """
        # https://github.com/dhylands/upy-examples/blob/master/encoder2.py
        pa = pyb.Pin(pin_a, mode=pyb.Pin.IN)
        pb = pyb.Pin(pin_b, mode=pyb.Pin.IN)

        self.tim = pyb.Timer(timer, prescaler=0, period=ENC_MAX)
        self.ch_1 = self.tim.channel(1, pyb.Timer.ENC_AB, pin=pa)
        self.ch_2 = self.tim.channel(2, pyb.Timer.ENC_AB, pin=pb)

    def read(self):
        """!
        Reads the encoder count on the passed encoder and allows
        for under and overflow correction.
        """
        # Previous count received from the encoder on the last read
        cnt = self.tim.counter()
        # Difference between the last read count (cnt) and the raw count
        delta = cnt - self.last_raw_cnt

        # Overflow max -> min

        if delta > ENC_MAX // 2:
            delta = ENC_MAX - delta

        # Overflow min -> max
        elif delta < -ENC_MAX // 2:
            delta = -ENC_MAX - delta

        self.count += delta
        self.last_raw_cnt = cnt

        return self.count

    def zero(self):
        """!
        Resets the count from the passed encoder to zero.
        """
        self.count = 0


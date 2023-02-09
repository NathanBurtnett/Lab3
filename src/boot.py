"""!
@file boot.py
Contains code used to boostrap the main project
"""
import pyb
pyb.repl_uart(None)
pyb.main("main.py")
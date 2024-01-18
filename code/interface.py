#!/usr/bin/env python3

import os
import sys
import time
import readline
import random
import signal
import datetime as dt
from pathlib import Path

try:
	import serial 
except ImportError:
	print("To run the Solar Tap CLI, please install the `pyserial` library.")
	print("\tPyPi: https://pypi.org/project/pyserial/")
	print("\tDebian/Ubuntu: (sudo) apt install python3-serial")
	sys.exit(1)

####################
# - Constants
####################
PATH_ROOT = Path(__file__).resolve().parent
PATH_EXP = PATH_ROOT / "exp" / dt.date.today().isoformat()

PATH_EXP_TEMP = lambda experiment_number: (
	PATH_EXP / str(experiment_number) / "temp.txt"
)
PATH_EXP_ROT = lambda experiment_number: (
	PATH_EXP / str(experiment_number) / "rot.txt"
)

PORT = "/dev/ttyACM0"
BAUD_RATE = 9600


####################
# - Global State
####################
FIRST_CLI_RUN = True
CLI_ACTIVE = False

EXPERIMENT_ACTIVE = False
EXPERIMENT_NUMBER = None

TEMP_SAMPLE = 0
ROT_SAMPLE = 0


####################
# - Mode Enable/Disable
####################
def enable_experiment(experiment_number: int):
	global CLI_ACTIVE
	global EXPERIMENT_ACTIVE
	global EXPERIMENT_NUMBER
	global TEMP_SAMPLE
	global ROT_SAMPLE
	
	print(f"[Enable] Experiment {experiment_number}...")
	EXPERIMENT_ACTIVE = True
	EXPERIMENT_NUMBER = experiment_number
	TEMP_SAMPLE = 0
	ROT_SAMPLE = 0
	disable_cli()
	
def disable_experiment():
	global EXPERIMENT_ACTIVE
	global EXPERIMENT_NUMBER
	
	print(f"[Disable] Experiment {EXPERIMENT_NUMBER}...")
	EXPERIMENT_ACTIVE = False
	EXPERIMENT_NUMBER = None


def enable_cli():
	global CLI_ACTIVE
	
	print("[Enable] CLI...")
	CLI_ACTIVE = True

def disable_cli():
	global CLI_ACTIVE
	
	print("[Disable] CLI...")
	CLI_ACTIVE = False

def quit_program():
	print("[Exiting]")
	sys.exit(0)

def cli_help():
	return """
Welcome to the Solar Tap CLI ("Command Line Interface")!
The following is a reference to available commands (type without ``, followed by "ENTER"):


`q`, `quit`: Quit the program.

CTRL+C: From monitoring mode, enable the CLI. From the CLI, quit the program.
	-> CTRL+C from monitoring mode will always disable any active experiment.

`monitor`: Disable the CLI mode, and return to monitoring mode.
	-> Messages received while in the CLI were buffered, and are replayed.


`enable experiment <number>`: Enable monitoring of an experiment, which will write data to dedicated files.
	-> Experiment recordings can be found at './exp/<today>/<number>/' (relative to this script) as 'temp.txt' and 'rot.txt'
	-> Recording format is '<sample_count>|<sample_datetime_iso8601>|<sample_value>".
	-> One line per sample


`motor inc <steps>`: Increment the step motor by a number of steps (steps are specific to motor model).
	-> Use negative steps to rotate the other way.

`motor rot <degrees>`: Increment the step motor by a number of degrees (degrees to steps are hard-coded on the microcontroller).
	-> Use negative degrees to rotate the other way.


`shader open`: Open the solar tap shaders, by rotating the motor a hard-coded number of degrees.
	-> When the shaders are already open, nothing happens.
	-> Whenever powering on the solar tap, it is presumed that the shaders are closed.

`shader close`: Close the solar tap shaders, by rotating the motor a hard-coded number of degrees.
	-> When the shaders are already closed, nothing happens.
	-> Whenever powering on the solar tap, it is presumed that the shaders are closed.


`compile`: Flash new firmware for the Solar Tap, by running 'make'.
	-> The command 'make' must work without this script.
	-> You must run this script from the directory that you run 'make' in.

`flash`: Flash new firmware to the Arduino, by running 'make upload'.
	-> See `compile`.
"""


####################
# - Device Actions
####################
def motor_inc(steps_str: str):
	"""Increment the motor by a given number of steps."""
	steps = int(steps_str)
	device.write(f"motor inc {steps}".encode())

def motor_rot(steps_str: str):
	"""Increment the motor by a given number of degrees."""
	degrees = float(steps_str)
	device.write(f"motor rot {degrees}".encode())


def shader_open():
	"""Open the shader by rotating a hard-coded amount."""
	device.write("shader open".encode())

def shader_close():
	"""Close the shaders by rotating a hard-coded amount."""
	device.write("shader close".encode())


####################
# - Signal Handling
####################
def on_sigint(sig, frame):
	"""Run when receiving SIGINT.
	"""
	global CLI_ACTIVE
	global TEMP_SAMPLE
	global ROT_SAMPLE
	
	# Newline to Jump Past ^C
	print()
	
	if EXPERIMENT_ACTIVE:
		disable_experiment()
	
	# Disable Experiment
	if CLI_ACTIVE:
		quit_program()
	else:
		enable_cli()



####################
# - Testing Serial Device
####################
class TestingSerialDevice:
	def __init__(self, port=None, baudrate=None, timeout=None):
		print("[DEBUG] Initializing Fake (Test) Serial Device:")
		print(f"\tport = {port}")
		print(f"\tbaudrate = {baudrate}")
		print(f"\ttimeout = {timeout}")
		print()
	
	def readline(self):
		time.sleep(0.5)
		if random.random() > 0.1:
			return "C: 1000.0".encode()
		else:
			return "R: 10".encode()
	
	def write(self, msg: bytes):
		print("Wrote to Device:", repr(msg))


####################
# - main()
####################
if __name__ == "__main__":
	# Attach Signal Handlers
	signal.signal(signal.SIGINT, on_sigint)
	
	print(f"""Welcome to the Solar Tap Interface!

The program will now attempt to connect to a Solar Tap device with the following settings:

  PORT: {PORT}
  BAUD_RATE: {BAUD_RATE}

If you're getting an error message, please adjust these constants in the source code of this program ('interface.py').
You should make use of the 'pyserial' documentation: <https://pyserial.readthedocs.io/en/latest/shortintro.html>.
""")
	
	# Connect to Device
	if len(sys.argv) > 1 and sys.argv[1] == "test":
		device = TestingSerialDevice(
			port=PORT,
			baudrate=BAUD_RATE,
			timeout=0.1,
		)
	else:
		device = serial.Serial(
			port=PORT,
			baudrate=BAUD_RATE,
			timeout=0.1,
		)
	
	print(f"[Connected] Device on port {PORT} with baudrate {BAUD_RATE}!")
	print()
	# Basic Usage
	print("""The program is now monitoring and printing events from the Solar Tap.
The data format is interpreted as follows:
- 'C: <number>': This denotes a measurement by the temperature sensor, in degrees celcius.
- 'R: <number>': This denotes a rotation requested of the step motor, in motor steps (steps -> degrees depends on the motor).

To interact with the device, please open the CLI ("Command Line Interface") using "CTRL+C".
This will also bring up a help text on how to use the CLI.
""")
	
	# Main Loop
	while True:
		raw_line = device.readline()
		sample_dt = dt.datetime.now()
		
		line = raw_line.decode("utf-8").strip()
		
		# (Potentially) Prompt for CLI Command
		if CLI_ACTIVE:
			if FIRST_CLI_RUN:
				print(cli_help())
				FIRST_CLI_RUN = False
			
			command = input(">>> ").split(" ")
			{
				"": lambda _: print("", end=""),
				"monitor": lambda _: disable_cli(),
				"q": lambda _: quit_program(),
				"quit": lambda _: quit_program(),
				
				"enable": lambda args: {
						"experiment": enable_experiment,
				}[args[0]](int(args[1])),
				
				"motor": lambda args: {
						"inc": motor_inc,
						"rot": motor_rot,
				}[args[0]](args[1]),
				
				"shader": lambda args: {
						"open": shader_open,
						"close": shader_close,
				}[args[0]](),
				
				"compile": lambda args: os.system("make"),
				"flash": lambda args: os.system("make upload"),
			}[command[0]](command[1:])
		
		# Print Line
		else:
			if line:
				print(line)
		
		# (Potentially) Record Line in Active Experiment
		if EXPERIMENT_ACTIVE:
			if line.startswith("C: "):
				temp = float(line[3:].strip())
				
				PATH_EXP_TEMP(EXPERIMENT_NUMBER).parent.mkdir(parents=True, exist_ok=True)
				with PATH_EXP_TEMP(EXPERIMENT_NUMBER).open("a") as f:
					f.write(f"{TEMP_SAMPLE}|{sample_dt.isoformat()}|{temp}\n")
				
				TEMP_SAMPLE += 1
			
			if line.startswith("R: "):
				steps = int(line[3:].strip())

				PATH_EXP_ROT(EXPERIMENT_NUMBER).parent.mkdir(parents=True, exist_ok=True)
				with PATH_EXP_ROT(EXPERIMENT_NUMBER).open("a") as f:
					f.write(f"{ROT_SAMPLE}|{sample_dt.isoformat()}|{steps}\n")
				
				ROT_SAMPLE += 1

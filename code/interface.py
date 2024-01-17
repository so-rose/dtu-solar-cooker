# Importing Libraries 
import serial 

PORT = "/dev/ttyACM0"
BAUD_RATE = 9600

if __name__ == "__main__":
	device = serial.Serial(
		port=PORT,
		baudrate=BAUD_RATE,
		timeout=0.1,
	)
	
	cli_active = True
	while True:
		if cli_active:
			command = input(">> ")
		
			if command == "run":
				cli_active = False
			else:
				device.write(command.encode())
		
		line = device.readline()
		if line:
			print(line.decode("utf-8"))

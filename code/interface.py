# Importing Libraries 
import serial 

PORT = "/dev/ttyACM0"
BAUD_RATE = 9600

if __name__ == "__main__":
	temp_sensor = serial.Serial(
		port=PORT,
		baudrate=BAUD_RATE,
		timeout=0.1,
	)
	
	while True:
		line = temp_sensor.readline()
		if line:
			print(line.decode("utf-8"))

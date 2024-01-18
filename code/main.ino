#include <Stepper.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <NonBlockingDallas.h>

//####################
// - Hardware Configuration
//####################
#define BAUD_RATE 9600
// - Byte Transfer Rate for Serial Interface

#define PIN_ONEWIRE 4
// - Pin for the Temperature Sensor(s)

#define PIN_STEPPER_1 8
#define PIN_STEPPER_2 10
#define PIN_STEPPER_3 9
#define PIN_STEPPER_4 11
// - Pins for the Step Motor (**Presume + is CCW**)
// - ---------------------------
// - Stepper.h[4] -> 8 -> IN1 -> Blue -> Motor{4}
// - Stepper.h[2] -> 9 -> IN2 -> Pink -> Motor{2}
// - Stepper.h[3] -> 10 -> IN3 -> Yellow -> Motor{3}
// - Stepper.h[1] -> 11 -> IN4 -> Orange -> Motor{1}
// - _Simply invert Stepper.h Indices to make CW the + direction._
// - ---------------------------
// - See <https://components101.com/motors/28byj-48-stepper-motor>


//####################
// - Configuration - Temperature Sensor
//####################
#define LED_MOTOR_LIGHT_TEMP 30.0
// - Temperature Threshold for LED Activation
// - Degrees Celcius.

#define TEMP_RESOLUTION NonBlockingDallas::resolution_11
// - Temperature Data Resolution (# of precision bits) vs. Computation Time
// - ---------------------------
// - 9 bit       93 ms
// - 10 bit      187 ms
// - 11 bit      375 ms
// - 12 bit      750 ms
// - See <https://github.com/Gbertaz/NonBlockingDallas>

#define TEMP_SAMPLE_RATE 500
// - Temperature Data Sample Rate
// - **Must be > Conversion Time for Chosen Resolution**.
// - Milliseconds. 


//####################
// - Configuration - Step Motor
//####################
#define STEPS_PER_REV 2038
// - Motor Steps per Full Revolution (360 degrees)
// - Property of Motor

#define RPM 10
// - Speed of Motor (in Revolutions per Minute)

//#define DEG_FOR_SHADER_TOGGLE 81.8753
#define DEG_FOR_SHADER_TOGGLE 92
// - Degrees Rotation to Open/Close Shader (Computed empirically)


//####################
// - Utilities - Step Motor
//####################
#define DEG_TO_STEPS(deg) ( (long)(deg * (double)STEPS_PER_REV / 360.0) )
// - Degrees are given as doubles, steps must be given as a long


//####################
// - Initialization
//####################
Stepper stepper(STEPS_PER_REV, PIN_STEPPER_1, PIN_STEPPER_2, PIN_STEPPER_3, PIN_STEPPER_4);

OneWire oneWire(PIN_ONEWIRE);
DallasTemperature sensor(&oneWire);
NonBlockingDallas sensorNoBlock(&sensor);


//####################
// - Global State
//####################
bool led_on = false;
bool isShaderOpen = false;



//####################
// - Reporters
//####################
void report_temp(float temperature){
	Serial.print("C: ");
	Serial.print(temperature);
	Serial.print("\n");
}

void report_rot(long steps){
	Serial.print("R: ");
	Serial.print(steps);
	Serial.print("\n");
}



//####################
// - Shader Control
//####################
void openShaders() {
	if (!isShaderOpen) {
		report_rot(-DEG_TO_STEPS(DEG_FOR_SHADER_TOGGLE));
		stepper.step(-DEG_TO_STEPS(DEG_FOR_SHADER_TOGGLE));
		isShaderOpen = true;
	}
}
void closeShaders() {
	if (isShaderOpen) {
		report_rot(DEG_TO_STEPS(DEG_FOR_SHADER_TOGGLE));
		stepper.step(DEG_TO_STEPS(DEG_FOR_SHADER_TOGGLE));
		isShaderOpen = false;
	}
}



//####################
// - Temperature Readout
//####################
void handleIntervalElapsed(float temperature, bool valid, int deviceIndex){
	report_temp(temperature);
	// Set LED Temperature Indicator
	if (temperature >= LED_MOTOR_LIGHT_TEMP && !led_on) {
		led_on = true;
		digitalWrite(LED_BUILTIN, HIGH);
		openShaders();
	} else if (temperature < LED_MOTOR_LIGHT_TEMP && led_on) {
		led_on = false;
		digitalWrite(LED_BUILTIN, LOW);
		closeShaders();
	}
}


//####################
// - Startup and Main Loop
//####################
void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(LED_BUILTIN, OUTPUT);
  stepper.setSpeed(RPM);

  sensorNoBlock.begin(TEMP_RESOLUTION, NonBlockingDallas::unit_C, TEMP_SAMPLE_RATE);
  sensorNoBlock.onIntervalElapsed(handleIntervalElapsed);
}

void loop() {
	sensorNoBlock.update();  // Possibly Read Temperature
	
	if (Serial.available() > 0) {
		String command = Serial.readString();
		command.trim();  // Get Rid of Leading/Trailing Whitespace (\n, \r, other trash)
		
		if (command == "shader open") {
			openShaders();
		} else if (command == "shader close") {
			closeShaders();
		} else if (command.startsWith("motor inc ")) {
			long increment_steps = command.substring(10).toInt();
			report_rot(increment_steps);
			stepper.step(increment_steps);
		} else if (command.startsWith("motor rot ")) {
			double increment_degrees = command.substring(10).toDouble();
			report_rot(DEG_TO_STEPS(increment_degrees));
			stepper.step(DEG_TO_STEPS(increment_degrees));
		} else if (command.startsWith("motor test")) {
			stepper.step(1000);
			delay(500);
			stepper.step(-1000);
		}
	}
}

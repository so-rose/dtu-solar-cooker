#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 4
#define LED_LIGHT_TEMP 30.0

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
bool led_on = false;

void setup(void) {
	pinMode(LED_BUILTIN, OUTPUT);
	Serial.begin(9600);
	sensors.begin();
}

void loop(void) { 
	sensors.requestTemperatures(); 
	float latest_temp = sensors.getTempCByIndex(0);
	
	Serial.print("C: ");
	Serial.print(latest_temp); 
	
	// LED Temperature Indicator
	if (latest_temp >= LED_LIGHT_TEMP && !led_on) {
		led_on = true;
		digitalWrite(LED_BUILTIN, HIGH);
	} else if (latest_temp < LED_LIGHT_TEMP && led_on) {
		led_on = false;
		digitalWrite(LED_BUILTIN, LOW);
	}
}

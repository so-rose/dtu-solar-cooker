# See https://github.com/sudar/Arduino-Makefile

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

AVRDUDE      = /usr/bin/avrdude
AVRDUDE_CONF = /etc/avrdude.conf

BOARD_TAG = uno
ARDMK_DIR = /usr/share/arduino

ARDUINO_SKETCHBOOK = $(ROOT_DIR)
ARDUINO_LIBS = OneWire DallasTemperature NonBlockingDallas Stepper

include $(ARDMK_DIR)/Arduino.mk

#!/usr/bin/env python3
# Adapted application script for Ci40 to work with LoRa RF Click Microcontroller
# ===========================================================
# https://github.com/MarisaAlina/Click_LoRa_RF
# Marten Vijn BSD-license http://svn.martenvijn.nl/svn/LICENSE
#
# http://www.microchip.com/DevelopmentTools/ProductDetails.aspx?PartNO=dm164138
# https://www.thethingsnetwork.org/docs/devices/
# create an appiclation and add a device for ABP or OTAA
# https://console.thethingsnetwork.org/applications
#

import time
# import serial
import os
import re

# imported these Ci40 specific libraries from https://github.com/francois-berder/PyLetMeCreate/blob/master/examples/lora_example.py
# first two are for connecting the ci40 pins with LoRa pins, latter for UART (interface), and baude rate
from letmecreate.core.common import MIKROBUS_2
from letmecreate.core import gpio
from letmecreate.core import uart
from letmecreate.core.uart import UART_BD_57600


## Thermo
from letmecreate.core import i2c
from letmecreate.core.common import MIKROBUS_1
from letmecreate.click import thermo3

# write config and keys to rn2483 or not
# writeconfig=0
writeconfig=1 

# Find ports on Ci40 via ls -l /dev/tty* -> /dev/ttySC
# Serial 
# SerialDev="/dev/ttyACM0"
# SerialDev="/dev/ttyUSB0"
## =======================================
## asign activation APB or OTAA                                                                     
#Activation="ABP"                                                                                   
Activation="OTAA" 
## =======================================

## TTN
## ABP settings
#Nwkskey="..."                                                              
#Appskey="..."            
#Devaddr="..."                                    
                                                      
## OTAA settings                          
Appkey="..."
Appeui="..."                 
Deveui="..."                             
                                                      
### SECOND TEST
## TTN, Pat's account
## ABP settings
# Nwkskey="..."
# Appskey="..."
# Devaddr="..."

## OTAA settings
#Appkey="..."
#Appeui="..."
#Deveui="..."

## =======================================

#print("Test ABP TTN")
print("Test OTAA TTN")
print("Test Air Data Transmission")
## =======================================

def readline():
	have_cr = False
	line = bytearray()
	while True:
		char = uart.receive(1)[0]
		line.append(char)
		if char == 13:
			have_cr = True
		elif char == 10 and have_cr == True:
			return line
		else:
			have_cr = False

def send(data):
	# p = serial.Serial(SerialDev, 9600 )
	# p.write(data+"\x0d\x0a")
	buf = data+"\x0d\x0a"
	uart.send(buf.encode())
	data.rstrip()
	print(data)
	time.sleep(2)
	rdata=readline()
	rdata=rdata[:-1]
    # deletes last char because it's \r or \n (c relic)
	print(rdata.decode())

# https://github.com/CreatorDev/PyLetMeCreate/blob/master/examples/lora_example.py
uart.init()
uart.select_bus(MIKROBUS_2)
uart.set_baudrate(UART_BD_57600)

# https://github.com/CreatorDev/LetMeCreate/blob/master/src/click/lora.c
# https://github.com/CreatorDev/PyLetMeCreate/blob/master/letmecreate/core/gpio.py

# gpio_init(rst_pin) < 0
#     ||  gpio_set_direction(rst_pin, GPIO_OUTPUT) < 0
# || gpio_set_value(rst_pin, 1) < 0) {}
pin = gpio.get_pin(MIKROBUS_2, gpio.TYPE_RST)
# print("pin="+pin)
gpio.init(pin)
gpio.set_direction(pin, gpio.GPIO_OUTPUT)
gpio.set_value(pin, 1)

send("sys reset")
time.sleep(1)

if writeconfig is 1:
  time.sleep(1)
  if ( Activation == "OTAA" ):
    send("mac set appkey {0}" .format(Appkey))
    send("mac set appeui {0}" .format(Appeui))
    send("mac set deveui {0}" .format(Deveui))
  elif ( Activation == "ABP"):
    send("mac set nwkskey {0}" .format(Nwkskey))
    send("mac set appskey {0}" .format(Appskey))
    send("mac set devaddr {0}" .format(Devaddr))
  send("mac set adr on")
  send("mac save")
  time.sleep(3)

if ( Activation == "OTAA" ):
  send("mac join otaa")
elif ( Activation == "ABP"):
  send("mac join abp")

## Thermo click 
"""This example uses Thermo3 Click and the wrapper of the PyLetMeCreate
library.
It reads some values from the sensor and exits.
The Thermo sensor click was inserted in Mikrobus 1 before running this program.
"""

# Initialise I2C on Mikrobus 1
i2c.init()
i2c.select_bus(MIKROBUS_1)

# sending temp sensor data
# converting into byte object (hex) using struct
# every 30 secs
import struct
while True:
    thermo3.enable(0)
    f = thermo3.get_temperature()
    temp_hex = struct.pack('f',f)
# temp_hex is now a byte object
# hex() returns a string object with the hex digit as literals
    b = bytearray(temp_hex).hex()
    temp_wrapper = "0367" +b  
#    send("mac tx cnf 1 "+ str(temp_wrapper))
    send("mac tx uncnf 1 aa ")
    time.sleep(30)
    thermo3.disable()   


# try sending confirmed and unconfirmed messages
# every 60 sec..
#  send("mac tx uncnf 1 aa ")
#  time.sleep(60)
#  send("mac tx cnf 1 bb")
#  time.sleep(60)

# Release I2C
i2c.release()

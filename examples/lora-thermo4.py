#!/usr/bin/env python3
# ===========================================================
# Adapted application script for Ci40 to work with LoRa RF Click Microcontroller
# https://github.com/francois-berder/PyLetMeCreate
# Marten Vijn BSD-license http://svn.martenvijn.nl/svn/LICENSE
# http://www.microchip.com/DevelopmentTools/ProductDetails.aspx?PartNO=dm164138
# https://www.thethingsnetwork.org/docs/devices/
# create an application and add a device for ABP or OTAA: https://console.thethingsnetwork.org/applications
# ===========================================================

import time
# import serial
import os
import re
import struct

# imported these Ci40 specific libraries from https://github.com/francois-berder/PyLetMeCreate/blob/master/examples/lora_example.py
# first two are for connecting the ci40 pins with LoRa pins, latter for UART (interface), and baudrate (ie symbols per second)
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
#Nwkskey="1F01907B33D556E4665F6C4DC1361EB9"
#Appskey="83C7A31C0BCB9C7E9B53E9A15E574CDC"
#Devaddr="26011058"                                   
     
## my_ci40
## OTAA settings                          
Appkey="790A9D08C4516B42A8DFED90B267C225"
Appeui="70B3D57EF00064C0"                 
Deveui="70B3D57EF00064C0"   


## Kevin's Device    
## OTAA settings                          
#Appkey="3D59713A24CB77265A157B8B42CF58DF"
#Appeui="70B3D57EF00064C0"                 
#Deveui="70B3D57EF000691F"   

## =======================================

#print("Test ABP TTN")
print("Test OTAA TTN")
print("Test Thermo Data Transmission")
## =======================================

## Ci40 receiving lines from lora tx 
def readline():
	have_cr = False
# preparing a "line": empty byte array onto which chars from lora tx are appended if \r\n was encountered
	line = bytearray()
	while True:
		buff = uart.receive(1)
		char = buff [0]
		line.append(char)
# State Machine to recognise a newline concept: https://github.com/francois-berder/LetMeCreate/blob/master/src/click/lora.c
		if char == 13:
			have_cr = True
		elif char == 10 and have_cr == True:
			return line
		else:
			have_cr = False


## sending encoded bytes via uart to lora tx (Ci40 -> lora tx)
def send(data):
# relic original script where serial instead of uart was used
	# p = serial.Serial(SerialDev, 9600 )
	# p.write(data+"\x0d\x0a")
# for lora tx to recognise command line end \r\n
	buf = data +"\x0d\x0a"
	uart.send(buf.encode())
# strip command clean from newline "garbage" at end	
	# data.rstrip()
# print command sent to lora tx	
	print(data)
# read what lora rx sends (back)	
	rdata = readline()
# deletes last char to cleanup bytearray from \r\n 	
	rdata = rdata[:-1]
	print(rdata.decode())

## Thermo click 
"""This example uses Thermo3 Click and the wrapper of the PyLetMeCreate
library.
It reads some values from the sensor and exits.
The Thermo sensor click was inserted in Mikrobus 1 before running this program.
https://github.com/francois-berder/PyLetMeCreate/blob/master/examples/thermo3_example.py
"""
def read_thermo():
    # Initialise I2C on Mikrobus 1
    i2c.init()
    i2c.select_bus(MIKROBUS_1)

    # sending temp sensor data
    # converting into byte object (hex) using struct

    while True:
        thermo3.enable(0)
        temp = (thermo3.get_temperature())/0.1
        temp_hex = struct.pack('>h',round(temp))
    # temp_hex is now a byte object, formatted to MSB short, rounded to last int
    # hex() returns a string object with the hex digit as literals
        b = bytearray(temp_hex).hex()
        temp_wrapper = "0967" +b  
    # channel 09, thermo object id '67'
        send("mac tx cnf 1 "+ str(temp_wrapper))
        time.sleep(3)
        thermo3.disable()   
    # Release I2C
    i2c.release()    

## setting the pins from lora tx on output high to switch it on
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

## UART = serial protocol for pins of Ci40 and lora tx to communicate                                                                                              
# https://github.com/CreatorDev/PyLetMeCreate/blob/master/examples/lora_example.py                                                                                 
uart.init()                                                                                                                                                        
uart.select_bus(MIKROBUS_2)                                                                                                                                        
uart.set_baudrate(UART_BD_57600)  


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
  time.sleep(1)

if ( Activation == "OTAA" ):
  send("mac join otaa")
elif ( Activation == "ABP"):
  send("mac join abp")

while True:
# sending air data in different intervals
#  time.sleep(1)
  read_thermo()


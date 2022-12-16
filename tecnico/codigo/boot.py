
try:
  import usocket as socket
except:
  import socket
  
from time import sleep
from machine import Pin
import onewire, ds18x20

import network

import esp
esp.osdebug(None)

import gc
gc.collect()

ds_pin = Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

import machine

touchA = machine.Pin(21, machine.Pin.IN)
touchB = machine.Pin(19, machine.Pin.IN)
touchC = machine.Pin(23, machine.Pin.IN)
touchD = machine.Pin(22, machine.Pin.IN)

ssid = 'Giane'
password = 'geanee71'

station = network.WLAN(network.STA_IF)
print("REDE")
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())
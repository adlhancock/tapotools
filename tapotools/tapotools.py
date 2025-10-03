#! /usr/bin/python3

from .config import login
from .config import devices
from PyP100.PyP110 import P110
from PyP100.PyL530 import L530
import sys
import os
import json
from datetime import datetime as dt
from colorsys import rgb_to_hsv
from matplotlib import colors
from PyP100.PyP100 import getDeviceList

class DeviceList:
    def __init__(self,login=login):
        self.devices = getDeviceList(login['email'],login['password'])

class Plug(P110):
    def __init__(self,name,login=login):
        P110.__init__(self,devices[name],login['email'],login['password'])
        self.handshake()
        self.login()
        

    def control(self,command=""):
        if command == 1:
            self.turnOn()
        elif command == 0:
            self.turnOff()
        elif command == '':
            pass
        return int(self.getDeviceInfo()['result']['device_on'])

class Bulb(L530):
    def __init__(self,name,login=login):
        L530.__init__(self,devices[name],login['email'],login['password'])
        self.handshake()
        self.login()
    def __str__(self):
        info = self.getDeviceInfo()['result']
        return f'{info}'
    def rgb(self,rgb):
        #assert len(rgb)==6
        r = int(str(rgb[0:2]),16)
        g = int(str(rgb[2:4]),16)
        b = int(str(rgb[4:6]),16)
        #print(r,g,b)
        
        h,s,l = rgb_to_hsv(r,g,b)
        #print(h,s,l)
        hue = int(h*360)
        sat = int(s*100)
        lum = int(l/255*100)
        #print(hue,sat,lum)
        self.setColor(hue,sat)
        self.setBrightness(lum)
        self.setColorTemp(0)
    def namedcolour(self,colour):
        rgb = colors.to_hex(colour)[1:]
        self.rgb(rgb)
    def daylight(self):
        self.setColor(0,0)
        self.setColorTemp(5500)
    def white(self):
        self.setColor(0,0)
        self.setColorTemp(4400)
    def warm(self):
        self.setColor(0,0)
        self.setColorTemp(2700)
    def full(self):
        self.setBrightness(100)
        self.warm()

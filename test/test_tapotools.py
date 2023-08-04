import os
import sys

sys.path.insert(0,os.path.abspath('..'))

from tapotools.tapotools import Plug, Bulb, DeviceList
from time import sleep

devices = ['fan','lamp']

light = Plug(devices[0])
light.turnOn()
sleep(3)
light.turnOff()

lamp = Bulb(devices[1])
lamp.rgb('ff0000')
sleep(1)
lamp.rgb('00ff00')
sleep(1)
lamp.rgb('0000ff')
sleep(1)
lamp.warm()
sleep(1)
lamp.turnOff()

#! /usr/bin/python3
""" studyheating/bin/tapo.py """


from config import USER_EMAIL, USER_PASSWORD, DEVICE_LIST, DEVICE_GROUPS
from PyP100 import PyP110, PyL530
import sys
import os
import json
from datetime import datetime as dt
from time import sleep
from pprint import pprint


def get_plug(ipaddress, email, password):
    plug = PyP110.P110(ipaddress, email, password)
    plug.handshake()
    plug.login()
    return plug


def get_tapodevice(ipaddress, email=USER_EMAIL, password=USER_PASSWORD, device_type='P110'):
    if device_type == 'P110':
        tapodevice = PyP110.P110(ipaddress, email, password)
    elif device_type == 'L530':
        try:
            tapodevice = PyL530.L530(ipaddress, email, password)
        except:
            print(f'{device_type} currently broken')
            exit()
    else:
        print(f'device type {device_type} not supported')
        exit()
    # tapodevice.handshake()
    # tapodevice.login()
    return tapodevice


def control(command, tapodevice):
    if command == "on":
        tapodevice.turnOn()
    elif command == "off":
        tapodevice.turnOff()
    elif command in ["",None]:
        pass
    else:
        print("Incorrect command issued to {}".format(tapodevice.getDeviceName()))
    deviceinfo = tapodevice.getDeviceInfo()
    ison = deviceinfo.get('device_on')
    return ison

def get_status(device_name):
    tapodevice = get_tapodevice(DEVICE_LIST.get(device_name).get('ip'),USER_EMAIL,USER_PASSWORD)
    ison = control("",tapodevice)
    return ison

def get_powernow(plug):
    plugenergy = plug.getEnergyUsage()
    # print(plugenergy)
    # power = plugenergy.get('result').get('current_power',float('nan'))
    power = plugenergy.get('current_power',float('nan'))
    if power != float('nan'):
        power = float(power)/1000
    return power

def write_logline(plug,logfile=None):
    pluginfo = plug.getDeviceInfo()
    if pluginfo['model'] == 'P110':
        try:
            if '-v' in sys.argv: print('-----pausing to get power value')
            sleep(2) # need to pause before getting power value
            devicepower = float(get_powernow(plug))/1000
        except:
            devicepower = None
    else:
        devicepower = 'N/A'
    logdata = {
            "timestamp":dt.now().isoformat(),
            "device": str(plug.getDeviceName()),
            "status": str(pluginfo['device_on']),
            "power": str(devicepower),
            }
    logline = json.dumps(logdata)+"\n"
    if logfile is not None:
        with open(logfile,'a') as f:
            f.write(logline)
    return logline

def tapo(device_name=None, command=None):
    if device_name in DEVICE_GROUPS:
        device_names = DEVICE_GROUPS.get(device_name)
    elif device_name in DEVICE_LIST:
        device_names = [device_name]
    else:
        print('Device list:')
        [print('\t',x) for x in DEVICE_LIST]
        print('Group list:')
        [print('\t',x) for x in DEVICE_GROUPS]
        print('Commands:')
        [print('\t',x) for x in ('on','off','info', '(or leave blank for status)')]
        exit()
    loglines = []
    for device in device_names:
        ip_address = DEVICE_LIST.get(device).get('ip')
        device_type = DEVICE_LIST.get(device).get('device_type')
        if ip_address is None:
            print('Device list:')
            [print('\t',x) for x in DEVICE_LIST]
            exit()
        tapodevice = get_tapodevice(ip_address,USER_EMAIL,USER_PASSWORD, device_type)
        if command == "info":
            pprint(tapodevice.getDeviceInfo())
            if device_type == 'P110':
                pprint(tapodevice.getEnergyUsage())
            exit()
        control(command,tapodevice)
        loglines.append(write_logline(tapodevice))
    return loglines

if __name__ == "__main__":
    args = sys.argv
    options, devices, commands = [], [], []
    for i, arg in enumerate(args):
        if '-' in arg:
            options.append(arg)
        if arg in DEVICE_LIST.keys():
            devices.append(arg)
            if i == len(args)-1:
                commands.append('')
            else:
                if args[i+1] in ('on','off','info'):
                    commands.append(args[i+1])
                else:
                    commands.append('')
    if len(devices) == 0:
        tapo()
    else:
        for device, command in zip(devices,commands):
            logline = tapo(device, command)
            if '-v' in args: print(f'{device} {command}\n\t {logline}')

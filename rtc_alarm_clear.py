#!/usr/bin/python3
# Reference: https://datasheets.maximintegrated.com/en/ds/DS3231.pdf

import smbus
import argparse

BUS=0

DEV_ADDR=0x68
REG_ALARM_INT=0x0F

parser = argparse.ArgumentParser(description='Clear any pending alarms on the DS3231.')
parser.add_argument('which_alarm', nargs='?', type=int, default=3, help='Which alarm (1 or 2) to clear; default BOTH.')
args = parser.parse_args()
if(args.which_alarm < 1 or args.which_alarm > 3):
  parser.error('Only valid alarm options are 1 or 2.')

if(args.which_alarm == 3):
  print('Clearing both alarms.')
else:
  print('Clearing alarm {}.'.format(args.which_alarm))

bus = smbus.SMBus(BUS)
prev = bus.read_byte_data(DEV_ADDR, REG_ALARM_INT)
bus.write_byte_data(DEV_ADDR, REG_ALARM_INT, prev & ~args.which_alarm)

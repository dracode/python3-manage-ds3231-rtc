#!/usr/bin/python3
# Reference: https://datasheets.maximintegrated.com/en/ds/DS3231.pdf

import smbus
import argparse

BUS=0

DEV_ADDR=0x68
REG_ALARM_INT_ENABLE=0x0E

parser = argparse.ArgumentParser(description='Disable the alarms on the DS3231.')
parser.add_argument('which_alarm', nargs='?', type=int, default=3, help='Which alarm (1 or 2) to disable; default BOTH.')
args = parser.parse_args()
if(args.which_alarm < 1 or args.which_alarm > 3):
  parser.error('Only valid alarm options are 1 or 2.')

if(args.which_alarm == 3):
  print('Disabling both alarms.')
else:
  print('Disabling alarm {}.'.format(args.which_alarm))

bus = smbus.SMBus(BUS)
prev = bus.read_byte_data(DEV_ADDR, REG_ALARM_INT_ENABLE)
bus.write_byte_data(DEV_ADDR, REG_ALARM_INT_ENABLE, prev & ~args.which_alarm)

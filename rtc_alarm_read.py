#!/usr/bin/python3
# Reference: https://datasheets.maximintegrated.com/en/ds/DS3231.pdf

import smbus
import argparse
import re

BUS=0

DEV_ADDR=0x68

REG_HWCLOCK_TIME=0x00 # through 0x06
REG_ALARM1_TIME=0x07 # through 0x0A
REG_ALARM2_TIME=0x0B # through 0x0D
REG_ALARM_INT_ENABLE=0x0E
REG_ALARM_INT_STATUS=0x0F

modes = {'X1111':'Once per second',
         'X1110':'When seconds match',
         'X1100':'When minutes and seconds match',
         'X1000':'When hours, minutes, and seconds match',
         '00000':'When date, hours, minutes, and seconds match',
         '10000':'When day of week, hours, minutes, and seconds match',
         'X111':'Once per minute',
         'X110':'When minutes match',
         'X100':'When hours and minutes match',
         '0000':'When date, hours, and minutes match',
         '1000':'When day of week, hours, and minutes match'}

def mode_lookup(mode):
  if(mode in modes):
    return modes[mode]
  return 'Undefined mode ' + mode

def hexed(inp):
  return '0x  ' + ' '.join(['{:02x}'.format(x) for x in inp])

def format_time(data):
  if(len(data) == 3):
    data = [0] + data
  dow = None
  dd = None
  mm = None
  yy = None
  if(len(data) == 7):
    dow = data[3]
    mm = '{:02x}'.format(data[5] & 0x7f)
    yy = '{:02x}'.format(data[6])
    data = data[0:3] + [data[4], ]
 
  sec  = '{:02x}'.format(data[0] & 0x7f)
  min  = '{:02x}'.format(data[1] & 0x7f)
  hour = '{:02x}'.format(data[2] & 0x3f)
  dd   = '{:02x}'.format(data[3] & 0x3f)

  if(data[2] & 0x40): # 12-hour format
    hour = int('{:x}'.format(data[2] & 0x1f), 16)
    if(hour == 12):
      hour = 0
    if(data[2] & 0x20): # PM
      hour += 12
    hour = '{:02d}'.format(hour)

  if(data[3] & 0x40):
    dow = int(dd, 16)
    dd = None

  if(dow and dow <= len(days)):
    dow = days[dow-1]
  else:
    dow = '***'
  date = '****-**-**'
  if(dd and dd != '00'):
    if(mm):
      date = '20{}-{}-{}'.format(yy, mm, dd)
    else:
      date = '****-**-{}'.format(dd)

  time = '{}:{}:{}'.format(hour, min, sec)

  return(dow, date, time)

days=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

parser = argparse.ArgumentParser(description='Read the alarms on the DS3231.')

args = parser.parse_args()

bus = smbus.SMBus(BUS)
cur_time = bus.read_i2c_block_data(DEV_ADDR, REG_HWCLOCK_TIME, 7)
alm1 = bus.read_i2c_block_data(DEV_ADDR, REG_ALARM1_TIME, 4)
alm2 = bus.read_i2c_block_data(DEV_ADDR, REG_ALARM2_TIME, 3)
estatus = bus.read_byte_data(DEV_ADDR, REG_ALARM_INT_ENABLE)
pstatus = bus.read_byte_data(DEV_ADDR, REG_ALARM_INT_STATUS)

print('DOW  YYYY-MM-DD  HH:MM:SS  Enabled  Pending  Alarm Trigger')
print('---  ----------  --------  -------  -------  -------------')
dow, date, time = format_time(cur_time)
print('{}  {}  {}  (current RTC time)'.format(dow, date, time))

dow, date, time = format_time(alm1)
mode = [(alm1[3] & 0x80) >> 7, (alm1[2] & 0x80) >> 7, (alm1[1] & 0x80) >> 7, (alm1[0] & 0x80) >> 7]
mode = ''.join([str(x) for x in mode])
if(mode == '0000'):
  mode = str((alm1[3] & 0x40) >> 6) + mode
else:
  mode = 'X' + mode
mode = mode_lookup(mode)
enabled = not not (estatus & 0x01)
pending = not not (pstatus & 0x01)
print('{}  {}  {}  {:7}  {:7}  {}'.format(dow, date, time, enabled, pending, mode))

dow, date, time = format_time(alm2)
mode = [(alm2[2] & 0x80) >> 7, (alm2[1] & 0x80) >> 7, (alm2[0] & 0x80) >> 7]
mode = ''.join([str(x) for x in mode])
if(mode == '000'):
  mode = str((alm2[2] & 0x40) >> 6) + mode
else:
  mode = 'X' + mode
mode = mode_lookup(mode)
enabled = not not (estatus & 0x02)
pending = not not (pstatus & 0x02)
print('{}  {}  {}  {:7}  {:7}  {}'.format(dow, date, time, enabled, pending, mode))

#!/usr/bin/python3
# Reference: https://datasheets.maximintegrated.com/en/ds/DS3231.pdf

import smbus
import argparse
import re

BUS=0

DEV_ADDR=0x68

REG_ALARM0_TIME=0x00 # current time, not alarm
REG_ALARM1_TIME=0x07 # through 0x0A
REG_ALARM2_TIME=0x0B # through 0x0D
REG_ALARM_INT_ENABLE=0x0E

days=['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']

def convert_to_bcd(decimal):
  place, bcd = 0, 0
  while decimal > 0:
    nybble = decimal % 10
    bcd += nybble << place
    decimal = int(decimal / 10)
    place += 4
  return bcd

def set_enable(which_alarm):
  bus = smbus.SMBus(BUS)

  prev = bus.read_byte_data(DEV_ADDR, REG_ALARM_INT_ENABLE)
  bus.write_byte_data(DEV_ADDR, REG_ALARM_INT_ENABLE, prev | which_alarm)

def set_time(dow, day, hh, mm, ss, month, year):
  data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
  data[0] = convert_to_bcd(ss)
  data[1] = convert_to_bcd(mm)
  data[2] = convert_to_bcd(hh)
  data[3] = convert_to_bcd(dow)
  data[3] |= 0b01000000
  data[4] = convert_to_bcd(day)
  data[5] = convert_to_bcd(month)
  data[6] = convert_to_bcd(year % 100)

  bus = smbus.SMBus(BUS)                            
  register = REG_ALARM0_TIME
  bus.write_i2c_block_data(DEV_ADDR, register, data)

def set_alarm(dow, day, hh, mm, ss, hourly, which_alarm):
  data = [0x00, 0x00, 0x00, 0x80]
  data[0] = convert_to_bcd(ss)
  data[1] = convert_to_bcd(mm)
  data[2] = convert_to_bcd(hh)
  if(hourly):
    data[2] |= 0x80
  if(day):
    data[3] = convert_to_bcd(day)
    if(dow):
      data[3] |= 0b01000000
  print(['{:x}'.format(x) for x in data])

  register = REG_ALARM1_TIME
  if(which_alarm == 2):
    register = REG_ALARM2_TIME
    data = data[1:]

  bus = smbus.SMBus(BUS)
  bus.write_i2c_block_data(DEV_ADDR, register, data)


parser = argparse.ArgumentParser(description='Set the alarms on the DS3231.')
parser.add_argument('--no-enable', '-n', dest='enable', action='store_false', default=True, help='Do NOT automatically enable the alarm after setting.')
parser.add_argument('--day', '-d', dest='day', help='Either day-of-week (Sun/Mon/Tue/Wed/Thu/Fri/Sat) or date of month.')
parser.add_argument('--hourly', dest='hourly', action='store_true', default=False, help='Alarm every hour at the specified time.')
parser.add_argument('--alarm', '-a', dest='which_alarm', type=int, default=1, help='Which alarm (1 or 2) to set; default 1.')
parser.add_argument('--set-time', '-s', dest='date', help='Set the current actual time on the RTC.  Specify date here as YYYY-MM-DD.  Use --day to set the day of week, and time as specified below.')
parser.add_argument(dest='time', help='Time, in 24-hour format, HH:MM:SS.  Alarm 2 always sets SS to 00.')

args = parser.parse_args()
match = re.search('^(?P<HH>[0-2][0-9]):(?P<MM>[0-5][0-9]):(?P<SS>[0-5][0-9])$', args.time)
if(not match):
  parser.error('Time must be in format HH:MM:SS.')
hh = int(match.group('HH'))
mm = int(match.group('MM'))
ss = int(match.group('SS'))

dow = False
day = 0
if(args.day):
  if(args.day.lower() in days):
    dow = True
    day = 1 + days.index(args.day.lower())
  else:
    try:
      day = int(args.day)
    except:
      pass
    if(day < 1 or day > 31):
      day = 0
  if(day == 0):
    parser.error('Day must be date of month (1-31) or day of week (Sun/Mon/Tue/Wed/Thu/Fri/Sat).')

# print(args)
if(args.date):
  match = re.search('^(?P<year>20[0-9]{2})-(?P<month>[01][0-9])-(?P<day>[0-3][0-9])$', args.date)
  if(not match):
    parser.error('Date must be in format 20YY-MM-DD.')
  if(dow == True):
    dow = day
  else:
    dow = 1
  day = int(match.group('day'))
  month = int(match.group('month'))
  year = int(match.group('year'))
  set_time(dow, day, hh, mm, ss, month, year)
else:
  set_alarm(dow, day, hh, mm, ss, args.hourly, args.which_alarm)
  if(args.enable):
    set_enable(args.which_alarm)



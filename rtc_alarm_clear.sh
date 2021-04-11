#!/bin/bash

# see DS3231 datasheet for register explanations:
# https://datasheets.maximintegrated.com/en/ds/DS3231.pdf

# note: bash represents binary as 2#xxxxxxxx instead of 0bxxxxxxxx

BUS=1

# register 0x0F
# 0b000000xx
DEFAULT_0F=2#00000000
BIT_A1F=0
BIT_A2F=1

echo 0x68 > /sys/bus/i2c/devices/i2c-1/delete_device

i2cset -y ${BUS} 0x68 0x0F 0x00

echo ds3231 0x68 > /sys/bus/i2c/devices/i2c-1/new_device


# python3-manage-ds3231-rtc
Some Python 3 scripts to read/set/enable/disable BOTH alarms on the DS3231 Real Time Clock (RTC) module

These scripts will allow you to read or set the various clocks on the DS3231 RTC.  The DS3231 has two alarms, but the standard Linux driver only uses the first one.  I haven't found any better way than this to use the second.

Unfortunately, this approach requires that the module's I2C address NOT already be bound.  So you need to disable the normal /dev/rtc interface to access alarm 2.

Check out `rtc_alarm_clear.sh` for an example of how to add or delete the RTC device to a running system and how to clear the alarms using the `i2cset` command.

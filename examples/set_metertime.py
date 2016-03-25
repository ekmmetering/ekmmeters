""" Simple example set Omnimeter time.
(c) 2016 EKM Metering.
"""
from ekmmeters import *

my_port_name = "/dev/ttyS0"
my_meter_address = "300001162"

ekm_set_log(ekm_print_log)
port = SerialPort(my_port_name)

if (port.initPort() == True):
    my_meter = V4Meter(my_meter_address)
    my_meter.attachPort(port)
else:
    print "Cannot open port"
    exit()


yy = 2023
mm = 11
dd = 22
hh = 15
min = 39
ss = 2

if (my_meter.setTime(yy, mm, dd, hh, min, ss)):
    if my_meter.request():
        time_str = my_meter.getField(Field.Meter_Time)
        dt = my_meter.splitEkmDate(int(time_str))
        print (str(dt.mm) + "-" + str(dt.dd) + "-" + str(dt.yy) + " " +
               str(dt.hh).zfill(2) + ":" + str(dt.minutes).zfill(2) + ":" + str(dt.ss).zfill(2))
    else:
        print "Request failed."
else:
    print "Set time failed."

port.closePort()
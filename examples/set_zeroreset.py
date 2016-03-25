""" Simple example zero reset
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

if my_meter.setZeroResettableKWH():
    if my_meter.request():
        print my_meter.getField(Field.Resettable_Rev_kWh_Tot)
        print my_meter.getField(Field.Resettable_kWh_Tot)

port.closePort()
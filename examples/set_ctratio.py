""" Simple example set CT Ratio
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

if my_meter.setCTRatio(CTRatio.Amps_800):
    if my_meter.request():
        ct_str = my_meter.getField(Field.CT_Ratio)
        print "CT is " + ct_str


port.closePort()
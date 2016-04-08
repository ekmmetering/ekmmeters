""" Simple example read getting 2 fields
(c) 2016 EKM Metering.
"""
from ekmmeters import *

my_port_name = "COM3"
my_meter_address = "10001438"

ekm_set_log(ekm_no_log)
port = SerialPort(my_port_name)

if (port.initPort() == True):
    my_meter = V4Meter(my_meter_address)
    my_meter.attachPort(port)
else:
    print "Cannot open port"
    exit()

for i in range(1000):
    if my_meter.request():
        my_read_buffer = my_meter.getReadBuffer()
        # you can also traverse the buffer yourself,
        #but this is the simplest way to get it all.
        print "*------"
        print my_meter.getField(Field.Power_Factor_Ln_1)
        print my_meter.getField(Field.Cos_Theta_Ln_1)


port.closePort()
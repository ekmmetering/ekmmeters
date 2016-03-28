""" Simple example read
(c) 2016 EKM Metering.
"""
from ekmmeters import *

my_port_name = "COM3"
my_meter_address = "300001162"

ekm_set_log(ekm_print_log)
port = SerialPort(my_port_name)

if (port.initPort() == True):
    my_meter = V4Meter(my_meter_address)
    my_meter.attachPort(port)
else:
    print "Cannot open port"
    exit()

if my_meter.request():
    my_read_buffer = my_meter.getReadBuffer()
    # you can also traverse the buffer yourself,
    #but this is the simplest way to get it all.
    json_str = my_meter.jsonRender(my_read_buffer)
    print json_str

port.closePort()
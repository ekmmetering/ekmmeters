""" Simple example pulse out
(c) 2016 EKM Metering.
"""
from ekmmeters import *

#port and meter
my_port_name = "COM3"
my_meter_address = "300001162"

#logging to console
ekm_set_log(ekm_print_log)

#open port and init
port = SerialPort(my_port_name)
if (port.initPort() == True):
    my_meter = V4Meter(my_meter_address)
    my_meter.attachPort(port)
else:
    # no port no meter
    print "Cannot open port"
    exit()


if my_meter.setPulseOutputRatio(PulseOutput.Ratio_5):
    if my_meter.request():
        po_str = my_meter.getField(Field.Pulse_Output_Ratio)
        print po_str

port.closePort()
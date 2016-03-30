""" Simple example relay set
(c) 2016 EKM Metering.
"""
from ekmmeters import *


#set your port and meter
my_port_name = "COM3"
my_meter_address = "300001162"

#just print the log
ekm_set_log(ekm_print_log)

#set up
port = SerialPort(my_port_name)
if (port.initPort() == True):
    my_meter = V4Meter(my_meter_address)
    my_meter.attachPort(port)
else:
    # not happening
    print "Cannot open port"
    exit()


if my_meter.setRelay(RelayInterval.Hold, Relay.Relay1, RelayState.RelayOpen):
    if my_meter.setRelay(2, Relay.Relay1, RelayState.RelayClose):
        print "Complete"

port.closePort()
""" Simple example set max demand interval
(c) 2016 EKM Metering.
"""
from ekmmeters import *

# port and meter to use
my_port_name = "/dev/ttyO4"
my_meter_address = "000300001463"

#log to console
ekm_set_log(ekm_print_log)


port = SerialPort(my_port_name)
if (port.initPort() == True):
    my_meter = V4Meter(my_meter_address)
    my_meter.attachPort(port)
else:
    print("Cannot open port")
    exit()


my_meter.setMaxDemandResetNow()


port.closePort()

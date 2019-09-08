""" Simple example set max demand period
(c) 2016 EKM Metering.
"""
from ekmmeters import *

# define port and meter
my_port_name = "/dev/ttyO4"
my_meter_address = "000300001463"
# log is print to console
ekm_set_log(ekm_print_log)

# create port and meter
port = SerialPort(my_port_name)
if (port.initPort() == True):
    my_meter = V4Meter(my_meter_address)
    my_meter.attachPort(port)
else:
    print("Cannot open port")
    exit()


#set and check
if my_meter.setMaxDemandPeriod(MaxDemandPeriod.At_30_Minutes):
    if my_meter.request():
        mdp_str = my_meter.getField(Field.Max_Demand_Period)
        if mdp_str == str(MaxDemandPeriod.At_15_Minutes):
            print("15 Minutes")
        if mdp_str == str(MaxDemandPeriod.At_30_Minutes):
            print("30 Minutes")
        if mdp_str == str(MaxDemandPeriod.At_60_Minutes):
            print("60 Minutes")

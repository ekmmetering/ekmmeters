""" Simple example set holiday dates
(c) 2016 EKM Metering.
"""
import random
from ekmmeters import *

#port setup
my_port_name = "COM3"
my_meter_address = "300001162"

#log to console
ekm_set_log(ekm_print_log)

# init port and meter
port = SerialPort(my_port_name)
if (port.initPort() == True):
    my_meter = V4Meter(my_meter_address)
    my_meter.attachPort(port)
else:
    print "Cannot open port"
    exit()

# input over range(Extents.Holidays)
for holiday in range(Extents.Holidays):
    day = random.randint(1,28)
    mon = random.randint(1,12)
    my_meter.assignHolidayDate(holiday, mon, day)
my_meter.setHolidayDates()

# input directly
param_buf = OrderedDict()
param_buf["Holiday_1_Month"] = 1
param_buf["Holiday_1_Day"] = 1
param_buf["Holiday_2_Month"] = 2
param_buf["Holiday_2_Day"] = 3
param_buf["Holiday_3_Month"] = 4
param_buf["Holiday_3_Day"] = 4
param_buf["Holiday_4_Month"] = 4
param_buf["Holiday_4_Day"] = 5
param_buf["Holiday_5_Month"] = 5
param_buf["Holiday_5_Day"] = 4
param_buf["Holiday_6_Month"] = 0
param_buf["Holiday_6_Day"] = 0
param_buf["Holiday_7_Month"] = 0
param_buf["Holiday_7_Day"] = 0
param_buf["Holiday_8_Month"] = 0
param_buf["Holiday_8_Day"] = 0
param_buf["Holiday_9_Month"] = 0
param_buf["Holiday_9_Day"] = 0
param_buf["Holiday_10_Month"] = 0
param_buf["Holiday_10_Day"] = 0
param_buf["Holiday_11_Month"] = 0
param_buf["Holiday_11_Day"] = 0
param_buf["Holiday_12_Month"] = 0
param_buf["Holiday_12_Day"] = 0
param_buf["Holiday_13_Month"] = 0
param_buf["Holiday_13_Day"] = 0
param_buf["Holiday_14_Month"] = 0
param_buf["Holiday_14_Day"] = 0
param_buf["Holiday_15_Month"] = 0
param_buf["Holiday_15_Day"] = 0
param_buf["Holiday_16_Month"] = 0
param_buf["Holiday_16_Day"] = 0
param_buf["Holiday_17_Month"] = 0
param_buf["Holiday_17_Day"] = 0
param_buf["Holiday_18_Month"] = 0
param_buf["Holiday_18_Day"] = 0
param_buf["Holiday_19_Month"] = 0
param_buf["Holiday_19_Day"] = 0
param_buf["Holiday_20_Month"] = 1
param_buf["Holiday_20_Day"] = 9

if my_meter.setHolidayDates(param_buf):
    print "Set holiday dates success."

port.closePort()
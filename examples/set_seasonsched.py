""" Simple example set seasons schedule
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

my_meter.assignSeasonSchedule(Seasons.Season_1, 1, 1, Schedules.Schedule_1)
my_meter.assignSeasonSchedule(Seasons.Season_2, 3, 21, Schedules.Schedule_2)
my_meter.assignSeasonSchedule(Seasons.Season_3, 6, 20, Schedules.Schedule_3)
my_meter.assignSeasonSchedule(Seasons.Season_4, 9, 21, Schedules.Schedule_8)
if my_meter.setSeasonSchedules():
    print "Completed"


param_buf = OrderedDict()
param_buf["Season_1_Start_Month"] = 1
param_buf["Season_1_Start_Day"] = 1
param_buf["Season_1_Schedule"] = 1
param_buf["Season_2_Start_Month"] = 3
param_buf["Season_2_Start_Day"] = 21
param_buf["Season_2_Schedule"] = 2
param_buf["Season_3_Start_Month"] = 6
param_buf["Season_3_Start_Day"] = 20
param_buf["Season_3_Schedule"] = 3
param_buf["Season_4_Start_Month"] = 9
param_buf["Season_4_Start_Day"] = 21
param_buf["Season_4_Schedule"] = 4
if my_meter.setSeasonSchedules(param_buf):
    print "Completed"

param_buf =OrderedDict()
param_buf["Schedule"] = 0
param_buf["Hour_1"] = 1
param_buf["Min_1"] = 11
param_buf["Rate_1"] = 1
param_buf["Hour_2"] = 2
param_buf["Min_2"] = 21
param_buf["Rate_2"] = 2
param_buf["Hour_3"] = 3
param_buf["Min_3"] = 31
param_buf["Rate_3"] = 3
param_buf["Hour_4"] = 4
param_buf["Min_4"] = 41
param_buf["Rate_4"] = 4
if my_meter.setScheduleTariffs(param_buf):
    print "Success"
""" Simple example set schedule tariff
(c) 2016 EKM Metering.
"""
import random
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


my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_1, 0,0,1)
my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_2, 5,30,2)
my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_3, 12,0,3)
my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_3, 17,30,3)
if (my_meter.setScheduleTariffs()):
    print "Success"



for schedule in range(Extents.Schedules):
    # create a random time and rate for the schedule
    min_start = random.randint(0,49)
    hr_start = random.randint(0,19)
    rate_start = random.randint(1,7)
    increment = 0
    for tariff in range(Extents.Tariffs):
        increment += 1
        if (not my_meter.assignScheduleTariff(schedule, tariff,
                                      hr_start + increment,
                                      min_start + increment,
                                      rate_start + increment)):
            print "Assignment failed."

    my_meter.setScheduleTariffs()




port.closePort()
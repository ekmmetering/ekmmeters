""" Simple example read to db
(c) 2016 EKM Metering.
"""
import os
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

os.remove("test.db")
my_db = SqliteMeterDB("test.db")
my_db.dbCreate()

arbitrary_run_iterations = 20

for i in range(arbitrary_run_iterations):
    if my_meter.request():
        my_meter.insert(my_db)

port.closePort()
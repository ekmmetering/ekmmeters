""" Simple example set LCD
(c) 2016 EKM Metering.
"""
from ekmmeters import *

#set up port
my_port_name = "COM3"
my_meter_address = "300001162"

# log to console
ekm_set_log(ekm_print_log)

# init port and create meter
port = SerialPort(my_port_name)
if (port.initPort() == True):
    my_meter = V4Meter(my_meter_address)
    my_meter.attachPort(port)
else:
    print "Cannot open port"
    exit()

# Method one: preferred
lcd_items = [LCDItems.RMS_Volts_Ln_1, LCDItems.Line_Freq]
if my_meter.setLCDCmd(lcd_items):
    print "Meter should now show Line 1 Volts and Frequency."

# Method two: parsing strings (use append normally)
lcd_items = [my_meter.lcdString("RMS_Volts_Ln_1"), my_meter.lcdString("Line_Freq")]
if my_meter.setLCDCmd(lcd_items):
    print "Meter should now show Line 1 Volts and Frequency."

port.closePort()
""" Simple example set LCD
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

# Method one: preferred
lcd_items = [LCDItems.RMS_Volts_Ln_1, LCDItems.Line_Freq]
if my_meter.setLCDCmd(lcd_items):
    print "Meter should now show Line 1 Volts and Frequency."

# Method two: parsing strings (use append normally)
lcd_items = [my_meter.lcdString("RMS_Volts_Ln_1"), my_meter.lcdString("Line_Freq")]
if my_meter.setLCDCmd(lcd_items):
    print "Meter should now show Line 1 Volts and Frequency."

port.closePort()
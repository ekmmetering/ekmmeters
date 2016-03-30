""" Simple example summarize
(c) 2016 EKM Metering.
"""
import time
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


class ASummaryObserver(MeterObserver):

    def __init__(self, interval):

        super(ASummaryObserver, self).__init__()
        self.m_summary_interval = interval
        self.m_start = time.time()
        self.m_sample_volts_sum = 0
        self.m_sample_volts = 0
        self.m_sample_interval_sum = 0
        self.m_sample_cnt = 0
        self.m_last_time = time.time()
        self.m_last_interval = 0
        self.m_15s_interval = int((time.time() * 1000)/(self.m_summary_interval * 1000))
        self.m_last_15s_interval = self.m_15s_interval

    def update(self, def_buf):
        time_now = time.time()
        self.m_last_interval = time_now - self.m_last_time
        self.m_last_time = time_now
        self.m_sample_interval_sum += self.m_last_interval

        self.m_15s_interval =  int((time.time() * 1000)/(self.m_summary_interval * 1000))
        if self.m_15s_interval > self.m_last_15s_interval:
            self.m_last_15s_interval = self.m_15s_interval
            self.doSummary()

        self.m_sample_cnt += 1
        self.m_sample_volts = def_buf[Field.RMS_Volts_Ln_1][MeterData.NativeValue]
        self.m_sample_volts_sum += self.m_sample_volts

    def doSummary(self):
        print ""
        print str(self.m_summary_interval) + " second summary"
        if self.m_sample_cnt > 0:
            print "Mean Voltage: " + str(self.m_sample_volts_sum/self.m_sample_cnt)
            print "Mean Interval " + str(self.m_sample_interval_sum/self.m_sample_cnt)
        self.m_sample_cnt = 0
        self.m_sample_volts_sum = 0
        self.m_sample_interval_sum = 0



ekm_set_log(ekm_no_log)
my_observer = ASummaryObserver(10)
my_meter.registerObserver(my_observer)

poll_reads = 120
print "Starting " + str(poll_reads) + " read poll."
read_cnt = 0
fail_cnt = 0
while(read_cnt < poll_reads):
    read_cnt += 1
    if not my_meter.request():
        fail_cnt += 1
        if fail_cnt > 3:
            print ">3 consecutive fails. Please check connection and restart"
            exit()
    else:
        fail_cnt = 0

port.closePort()

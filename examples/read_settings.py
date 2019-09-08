""" Simple example read settings
(c) 2016 EKM Metering.
"""
from ekmmeters import *

#port and meter
my_port_name = "/dev/ttyO4"
my_meter_address = "000300001463"
#logging to console
ekm_set_log(ekm_print_log)

#open port and init
port = SerialPort(my_port_name)
if (port.initPort() == True):
    my_meter = V4Meter(my_meter_address)
    my_meter.attachPort(port)
else:
    # no port no meter
    print ("Cannot open port")
    exit()


# First readthedocs example, complete.

if my_meter.readSettings():

    print ("Schedule".ljust(15) + "Tariff".ljust(15) + "Date".ljust(10))
    for schedule in range(Extents.Schedules):
        for tariff in range(Extents.Tariffs):
            schedule_tariff = my_meter.extractSchedule(schedule, tariff)
            print (("Schedule_" + schedule_tariff.Schedule).ljust(15) +
                   ("Tariff_" + schedule_tariff.Tariff).ljust(15) +
                   (schedule_tariff.Hour+":"+schedule_tariff.Min).ljust(10))

    print("Month".ljust(7) + "kWh_Tariff_1".ljust(14) + "kWh_Tariff_2".ljust(14) +
           "kWh_Tariff_3".ljust(14) + "kWh_Tariff_4".ljust(14) + "kWh_Tot".ljust(10) +
           "Rev_kWh_Tariff_1".ljust(18) + "Rev_kWh_Tariff_2".ljust(18) +
           "Rev_kWh_Tariff_3".ljust(18) + "Rev_kWh_Tariff_4".ljust(18) + "Rev_kWh_Tot".ljust(11))
    for month in range(Extents.Months):
        md = my_meter.extractMonthTariff(month)
        print(md.Month.ljust(7) + md.kWh_Tariff_1.ljust(14) +
                  md.kWh_Tariff_2.ljust(14) + md.kWh_Tariff_3.ljust(14) +
                  md.kWh_Tariff_4.ljust(14) + md.kWh_Tot.ljust(10) +
                  md.Rev_kWh_Tariff_1.ljust(18) + md.Rev_kWh_Tariff_2.ljust(18) +
                  md.Rev_kWh_Tariff_3.ljust(18) + md.Rev_kWh_Tariff_4.ljust(18) +
                  md.Rev_kWh_Tot.ljust(10))

    print("Holiday".ljust(12) + "Date".ljust(20))
    for holiday in range(Extents.Holidays):
        holidaydate = my_meter.extractHolidayDate(holiday)
        print(("Holiday_" + holidaydate.Holiday).ljust(12) +
              (holidaydate.Month + "-" + holidaydate.Day).ljust(20))
    holiday_weekend_schedules = my_meter.extractHolidayWeekendSchedules()
    print ("Holiday schedule = " + holiday_weekend_schedules.Holiday)
    print ("Weekend schedule = " + holiday_weekend_schedules.Weekend)

# readthedocs individual example, complete.
if my_meter.readSettings():
    months_fwd_blk = my_meter.getMonthsBuffer(ReadMonths.kWh)
    months_rev_blk = my_meter.getMonthsBuffer(ReadMonths.kWhReverse)
    sched_blk_1 = my_meter.getSchedulesBuffer(ReadSchedules.Schedules_1_To_4)
    sched_blk_2 = my_meter.getSchedulesBuffer(ReadSchedules.Schedules_5_To_6)
    holiday_blk = my_meter.getHolidayDatesBuffer()

    print (my_meter.jsonRender(months_fwd_blk))
    print (my_meter.jsonRender(months_rev_blk))
    print (my_meter.jsonRender(sched_blk_1))
    print (my_meter.jsonRender(sched_blk_2))
    print (my_meter.jsonRender(holiday_blk))





port.closePort()

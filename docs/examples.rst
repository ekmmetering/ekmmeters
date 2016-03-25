Examples
--------

All of these examples, and several more, can be found in the examples subdirectory of the source distribution.

To get started, you will want to make sure your meter is set up and you know the name of the port.  If in doubt,
download a trial copy of EKM Dash and insure that your meters are connected and talking.

Every example below is surrounded by a few lines of setup and teardown.

.. code-block:: python

   import os      # to delete example db before create
   import random  # to generate example data
   import time    # to support summarizer sample

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

   # Example goes here

   port.closePort()

Read
^^^^

The full set off measurements for your Omnimeter are returned with request().

.. code-block:: python

   if my_meter.request():
       my_read_buffer = my_meter.getReadBuffer()

       # you can also traverse the buffer yourself,
       #but this is the simplest way to get it all.

       json_str = my_meter.jsonRender(my_read_buffer)
       print json_str

Save to Database
^^^^^^^^^^^^^^^^

A simple wrapper for Sqlite is included in the library.  The
example below, if a way to end the loop and exception handling were added,
is perfectly suitable to a simple storage utility.

If you already have an ORM in place, such as SQLAlchemy, you should define an
appropriate object and load it by traversing the read buffer.  But for most
simple cases, the following will suffice.

.. code-block:: python

   os.remove("test.db")  # keep our example simple

   my_db = SqliteMeterDB("test.db")
   my_db.dbCreate()

   arbitrary_iterations = 20

   for i in range(arbitrary_iterations):
       if my_meter.request():
           my_meter.insert(my_db)

Set CT Ratio
^^^^^^^^^^^^

.. code-block:: python

   if my_meter.setCTRatio(CTRatio.Amps_800):
       if my_meter.request():
           ct_str = my_meter.getField(Field.CT_Ratio)
           print "CT is " + ct_str


Max Demand Period
^^^^^^^^^^^^^^^^^

.. code-block:: python

   if my_meter.setMaxDemandPeriod(MaxDemandPeriod.At_15_Minutes):
       if my_meter.request():
           mdp_str = my_meter.getField(Field.Max_Demand_Period)
           if mdp_str == str(MaxDemandPeriod.At_15_Minutes):
               print "15 Minutes"
           if mdp_str == str(MaxDemandPeriod.At_30_Minutes):
               print "30 Minutes"
           if mdp_str == str(MaxDemandPeriod.At_60_Minutes):
               print "60 Minutes"

Max Demand Interval
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   my_meter.setMaxDemandInterval(MaxDemandInterval.Daily)

Set Pulse Output Ratio
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   if my_meter.setPulseOutputRatio(PulseOutput.Ratio_5):
       if my_meter.request():
           po_str = my_meter.getField(Field.Pulse_Output_Ratio)
           print po_str

Set Pulse Input Ratio
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   if my_meter.setPulseRatio(Pulse.Ln3, 55):
       if my_meter.request():
           pr_str = my_meter.getField(Field.Pulse_Ratio_1)
           print pr_str

Set Relay
^^^^^^^^^

.. code-block:: python

   if my_meter.setRelay(RelayInterval.Hold, Relay.Relay1, RelayState.RelayOpen):
       if my_meter.setRelay(2, Relay.Relay1, RelayState.RelayClose):
           print "Complete"

Set Meter Time
^^^^^^^^^^^^^^

EKM meter time is stored in a proprietary year-first format which includes day of week.
The API will strip off the century and calculate day of week.

It is possible for a corrupt date to contain a ? character.  If it does, you
will get a value exception when you convert it before calling splitEkmDate().


.. code-block:: python

   yy = 2023
   mm = 11
   dd = 22
   hh = 15
   min = 39
   ss = 2

   if (my_meter.setTime(yy, mm, dd, hh, min, ss)):
       if my_meter.request():
           time_str = my_meter.getField(Field.Meter_Time)
           dt = my_meter.splitEkmDate(int(time_str))
           print (str(dt.mm) + "-" +
                  str(dt.dd) + "-" +
                  str(dt.yy) + " " +
                  str(dt.hh).zfill(2) + ":" +
                  str(dt.minutes).zfill(2) + ":" +
                  str(dt.ss).zfill(2))
       else:
           print "Request failed."
   else:
       print "Set time failed."

Zero Resettable kWh
^^^^^^^^^^^^^^^^^^^
.. code-block:: python

   if my_meter.setZeroResettableKWH():
       if my_meter.request():
           print my_meter.getField(Field.Resettable_Rev_kWh_Tot)
           print my_meter.getField(Field.Resettable_kWh_Tot)


Set Season Schedules
^^^^^^^^^^^^^^^^^^^^

The most direct approach is to use assignSeasonSchedule().  This example sets
up four slightly-off seasons.

.. code-block:: python

   my_meter.assignSeasonSchedule(Seasons.Season_1, 1, 1, Schedules.Schedule_1)
   my_meter.assignSeasonSchedule(Seasons.Season_2, 3, 21, Schedules.Schedule_2)
   my_meter.assignSeasonSchedule(Seasons.Season_3, 6, 20, Schedules.Schedule_3)
   my_meter.assignSeasonSchedule(Seasons.Season_4, 9, 21, Schedules.Schedule_8)
   my_meter.setSeasonSchedules()

If you are not using library constantss for the seasons and schedules, testing the
assignSeasonSchedule() for True is strongly recommended.

You can also populate the season schedule using a dictionary, which simplifies
loading a meter from passed JSON.

.. code-block:: python

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

Set Schedule Tariffs
^^^^^^^^^^^^^^^^^^^^

Schedules are set one at a time.  Each schedule has four tariffs,
described by a start hour and minute.  The following example creates one
schedule with tariffs beginning at midnight (rate = 1), 5:30 am (rate = 2),
noon (rate = 3), and 5:30 pm (rate 4).


.. code-block:: python

   my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_1, 0,0,1)
   my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_2, 5,30,2)
   my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_3, 12,0,3)
   my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_3, 17,30,3)
   if (my_meter.setScheduleTariffs()):
       print "Success"

If yu are not using library constants, it is strong recommended testing assignScheduleTariff() for True.
You can also use the range(Extents.<name>) idiom to populate many schedules.

.. code-block:: python

   for schedule in range(Extents.Schedules):
       # create a random time and rate for the schedule
       min_start = random.randint(0,49)
       hr_start = random.randint(0,19)
       rate_start = random.randint(1,7)
       increment = 0
       for tariff in range(Extents.Tariffs):
           increment += 1
           my_meter.assignScheduleTariff(schedule, tariff,
                                         hr_start + increment,
                                         min_start + increment,
                                         rate_start + increment)
       my_meter.setScheduleTariffs()

If you are defining a schedule via JSON or XML, you can set the tariffs with a dictionary:

.. code-block:: python

   param_buf = OrderedDict()
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

Set Holiday Dates
^^^^^^^^^^^^^^^^^

Because the holiday list is relatively long, it is the only block which
does not hide the zero offset in the assign() function using constants.  However,
the range(Extents.Holidays) idiom can still be used to fill the holiday table:

.. code-block:: python

   for holiday in range(Extents.Holidays):
       day = random.randint(1,28)
       mon = random.randint(1,12)
       my_meter.assignHolidayDate(holiday, mon, day)

   my_meter.setHolidayDates()

As with the other settings commands, a dictionary can be passed to the set*() function for JSON and XML support.

.. code-block:: python

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

Set LCD Display
^^^^^^^^^^^^^^^

The simplest way to set display items is with the setLCDCmd() call:

.. code-block:: python

   lcd_items = [LCDItems.RMS_Volts_Ln_1, LCDItems.Line_Freq]
   if my_meter.setLCDCmd(lcd_items):
       print "Meter should now show Line 1 Volts and Frequency."

If you are supporting a JSON or XML based client, you do not need to recreate the
list of LCD items.  Simply call lcdString():

.. code-block:: python

   lcd_items = [my_meter.lcdString("RMS_Volts_Ln_1"),
                my_meter.lcdString("Line_Freq")]
   if my_meter.setLCDCmd(lcd_items):
       print "Meter should now show Line 1 Volts and Frequency."

Read Settings
^^^^^^^^^^^^^

A schedule has four tariff periods (each defined by a start hour and minute).  These four time
periods are used to collect kilowatt hours and reverse kilowatt hours over months and seaons.
Holidays and weekends can have seperate schedules, used within seasons and months.

The meter allows up to eight schedules, retains the last six months of data, and (of course)
allows four seasons.  Up to 20 holidays can be listed under a single holiday schedule.

The simplest way get the data is all at once, with readSettings(), and use the provided
traversal idiom to extract the data.

We start by reading all the settings tables into the meter buffers.

.. code-block:: python

   if my_meter.readSettings():

       # print header line
       print("Schedule".ljust(15) + "Tariff".ljust(15) +
             "Date".ljust(10) + "Rate".ljust(15))

       # There are eight schedules and four tariffs to traverse.  We can
       # safely get indices for extractScheduleTariff -- which returns a
       # single tariff as a tuple -- using the idiom
       # of range(Extents.<item_type>)

       for schedule in range(Extents.Schedules):

           for tariff in range(Extents.Tariffs):

               schedule_tariff = my_meter.extractScheduleTariff(schedule, tariff)

               # and now we can print the returned tuple in a line
               print (("Schedule_" + schedule_tariff.Schedule).ljust(15) +
                      ("kWh_Tariff_" + schedule_tariff.Tariff).ljust(15) +
                      (schedule_tariff.Hour+":"+
                       schedule_tariff.Min).ljust(10) +
                      (schedule_tariff.Rate.ljust(15)))

Continuing the traversal of data returned from readSettings(), we get per month data:

.. code-block:: python

   # print header line
   print("Month".ljust(7) + "kWh_Tariff_1".ljust(14) + "kWh_Tariff_2".ljust(14) +
          "kWh_Tariff_3".ljust(14) + "kWh_Tariff_4".ljust(14) +
          "kWh_Tot".ljust(10) + "Rev_kWh_Tariff_1".ljust(18) +
          "Rev_kWh_Tariff_2".ljust(18) + "Rev_kWh_Tariff_3".ljust(18) +
          "Rev_kWh_Tariff_4".ljust(18) + "Rev_kWh_Tot".ljust(11))

   # traverse the provided six months:
   for month in range(Extents.Months):

        # extract the data for each month
        md = my_meter.extractMonthTariff(month)

        # and print the line
        print(md.Month.ljust(7) + md.kWh_Tariff_1.ljust(14) +
                  md.kWh_Tariff_2.ljust(14) + md.kWh_Tariff_3.ljust(14) +
                  md.kWh_Tariff_4.ljust(14) + md.kWh_Tot.ljust(10) +
                  md.Rev_kWh_Tariff_1.ljust(18) + md.Rev_kWh_Tariff_2.ljust(18) +
                  md.Rev_kWh_Tariff_3.ljust(18) + md.Rev_kWh_Tariff_4.ljust(18) +
                  md.Rev_kWh_Tot.ljust(10))

And continue to list the 20 holidays and their schedules:

.. code-block:: python

   # print the header
   print("Holiday".ljust(12) + "Date".ljust(20))

   # traverse the defined holidays
   for holiday in range(Extents.Holidays):

        # get the tuple ffor each individual holiday
        holidaydate = my_meter.extractHolidayDate(holiday)

        # and print the line
        print(("Holiday_" + holidaydate.Holiday).ljust(12) +
              (holidaydate.Month + "-" + holidaydate.Day).ljust(20))

    # the schedules assigned to the above holidays, and to weekends
    holiday_weekend_schedules = my_meter.extractHolidayWeekendSchedules()
    print "Holiday schedule = " + holiday_weekend_schedules.Holiday
    print "Weekend schedule = " + holiday_weekend_schedules.Weekend


An approach requiring far fewer lines of code to extract the data (but probably
much more code to parse and handle it) is to simply return the SerialBlocks for each
read.

.. code-block:: python

   if my_meter.readSettings():

       months_fwd_blk = my_meter.getMonthsBuffer(ReadMonths.kWh)
       months_rev_blk = my_meter.getMonthsBuffer(ReadMonths.kWhReverse)
       sched_1 = my_meter.getSchedulesBuffer(ReadSchedules.Schedules_1_To_4)
       sched_2 = my_meter.getSchedulesBuffer(ReadSchedules.Schedules_5_To_8)
       holiday_blk = my_meter.getHolidayDatesBuffer()

       print my_meter.jsonRender(months_fwd_blk)
       print my_meter.jsonRender(months_rev_blk)
       print my_meter.jsonRender(sched_1)
       print my_meter.jsonRender(sched_2)
       print my_meter.jsonRender(holiday_blk)

This looks wonderfully simple.  Unfortunately, unless you are just sending the data over the net,
it is much more work to traverse and extract.  Do note that weekend and holiday schedules are at the very end
of the holiday block.

The readSettings() function breaks out to :func:`~ekmmeters.Meter.readScheduleTariffs`, :func:`~ekmmeters.Meter.readMonthTariffs` and  :func:`~ekmmeters.Meter.readHolidayDates`.
If you take this approach you will need to call readMonthTariffs() twice, with ReadMonths.kWh and ReadMonths.kWhReverse, and call
readScheduleTariffs() twice as well, with ReadSchedules.Schedules_1_To_4 and ReadSchedules.Schedules_5_To_8.


Notify and Summarize
^^^^^^^^^^^^^^^^^^^^

This library is intended for programmers at all levels.  Most users seeking to summarize their data or generate
notifications can do so simply in the main polling loop.  However, sometimes only an observer pattern will do.
This is a very simple implementation and easily learned, but nothing in this example is necessary for mastery of
the API.

Each meter object has a chain of 0 to n observer objects.  When a request is issued, the meter calls the Update()
method of every observer object registered in its chain.  All observer objects descend from MeterObserver, and require
an override of the Update method and constructor.

Using set_notify.py an set_summarize.py is the fastest and easiest way to explore these examples.  Both examples
require a request loop at the *bottom* of the file, before closing the serial port.  It is a simple count limited
request loop, and is useful when building software against this library.

.. code-block:: python

   ekm_set_log(ekm_no_log)  # comment out to restore

   poll_reads = 120   # counts to iterate
   print "Starting " + str(poll_reads) + " read poll."
   read_cnt = 0  # read attempts
   fail_cnt = 0  # consecutive failed reads
   while (read_cnt < poll_reads):
      read_cnt += 1
      if not my_meter.request():
         fail_cnt += 1
         if fail_cnt > 3:
            print ">3 consecutive fails. Please check connection and restart"
            exit()
   else:
      fail_cnt = 0


The notification observer example requires that your meter have pulse input line one hooked up, if only as two wires
you can close.  To create a notification observer, start by subclassing MeterObserver immediately before the snippet above.  The
constructor sets a startup test condition and initializes the last pulse count used for comparison.

Note that our Update() override gets the native (float) value directly, using MeterData.NativeValue.  It could as easily
return MeterData.StringValue, and cast.  The first Update() sets the initial comparison value.  Subsequent Update()
calls compare the pulse count and check to see if there is a change.  The doNotify() method is our triggered event, and
can of course do anything Python can.

.. code-block:: python

   class ANotifyObserver(MeterObserver):

    def __init__(self):

        super(ANotifyObserver, self).__init__()
        self.m_startup = True
        self.m_last_pulse_cnt = 0

    def Update(self, def_buf):

        pulse_cnt = def_buf[Field.Pulse_Cnt_1][MeterData.NativeValue]

        if self.m_startup:
            self.m_last_pulse_cnt = pulse_cnt
            self.m_startup = False
        else:
            if self.m_last_pulse_cnt < pulse_cnt:
                self.doNotify()
                self.m_last_pulse_cnt = pulse_cnt

    def doNotify(self):
        print "Bells!  Alarms!  Do that again!"

And finally -- right before dropping into our poll loop, we instantiate our subclassed MeterObserver, and register it in the
meter's observer chain.  We also put the pulse count on the LCD, and set the input ratio to one so every time we close
the pulse input, we fire our event.


.. code-block:: python

   my_observer = ANotifyObserver()
   my_meter.registerObserver(my_observer)

   my_meter.setLCDCmd([LCDItems.Pulse_Cn_1])
   my_meter.setPulseRatio(Pulse.Ln1, 1)


set_summarize.py, in the examples directory of the source distribution, provides a MeterObserver which keeps a voltage
summary over an arbitrary number of seconds, passed in the constructor.  While slightly longer than the example above,
it does not require wiring the meter pulse inputs.



Examples
--------

All of these examples, and several more, can be found in the examples
subdirectory of the github source.

To get started, you will want to make sure your meter is set up and you
know the name of the port.  If in doubt, download a trial copy of EKM Dash and
insure that your meters are connected and talking.

Every example below is surrounded by a few lines of setup and teardown.

.. code-block:: python
   :emphasize-lines: 20
   :linenos:

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

All of the serial commands to the meter return True or False, and log the exceptions.  In a long running
agent, there is no user action (or programmatic action) requiring exception data: you can only retry until
it is clear that the port is not talking to a meter.  Generally failing calls will fall through a very short
timeout.


Every method making a serial call accepts an optional password parameter (eight
numeric characters in a string).  The default, shipped with the meter, is "00000000".  Most systems
urge setting passwords immediately.  We don't recommend that unless it is a feature on a mature
system with a real level of security risk.  EKM has no back door into your meter.  If you reset and
lose your password, it is gone.  All of the examples below omit the password parameter and use the
default.

Read
****

Meters are read with :func:`~ekmmeters.Meter.request`, which always returns a True or False.  Request takes 
an optional termination flag which forces a "end this conversation" string to be sent to the meter. This is only
used inside other serial calls: you can just ignore it and leave the default value of True.

The full set of measurements for your Omnimeter are returned with :func:`~ekmmeters.Meter.request` on 
both V3 and V4 Omnimeters. Omnimeters return data in 255 byte chunks.  The supported V3 meter fields come back in one chunk (referred to in the EKM documentation as an A read), and the V4 Omnimeter uses two chunks (referred to as an AB read).  The request method is the same on both meter versions.

.. code-block:: python
   :emphasize-lines: 2, 7
   :linenos:

   if my_meter.request():
       my_read_buffer = my_meter.getReadBuffer()

       # you can also traverse the buffer yourself,
       #but this is the simplest way to get it all.

       json_str = my_meter.jsonRender(my_read_buffer)
       print json_str

Save to Database
****************

A simple wrapper for Sqlite is included in the library.  

If you already have an ORM in place, such as SQLAlchemy, you should define an
appropriate object and load it by traversing the read buffer.  But for most
simple cases, the following will suffice.

The method :func:`~ekmmeters.Meter.insert` tells the meter object to put the data away in an
instantiated MeterDB.

The default behavior of a MeterDB object is built around portable-as-possible SQL: 
one create statement, which should only be called once, two index creates, an insert, 
and a drop.  In this example we delete the Sqlite database entirely and call create each time.

.. code-block:: python
   :emphasize-lines: 1,3,4,9,10
   :linenos:

   os.remove("test.db")  # keep our example simple

   my_db = SqliteMeterDB("test.db")
   my_db.dbCreate()

   arbitrary_iterations = 20

   for i in range(arbitrary_iterations):
       if my_meter.request():
           my_meter.insert(my_db)

CT Ratio
********

The CT ratio tells the meter how to scale the input from an inductive pickup.
Allowed values are shown under :class:`~ekmmeters.CTRatio`.

The CT ration is set with the method :func:`~ekmmeters.Meter.setCTRatio`.
The field CT_Ratio is returned in every read request.


.. code-block:: python
   :emphasize-lines: 1, 3
   :linenos:

   if my_meter.setCTRatio(CTRatio.Amps_800):
       if my_meter.request():
           ct_str = my_meter.getField(Field.CT_Ratio)
           print "CT is " + ct_str


Max Demand Period
*****************

The max demand period is a value in the set :class:`~ekmmeters.MaxDemandPeriod`.
It is written with the method :func:`~ekmmeters.Meter.setMaxDemandPeriod`. The field
Max_Demand_Period is returned in every read request.

.. code-block:: python
   :emphasize-lines: 1, 3, 4, 6, 8
   :linenos:

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
*******************

Max demand interval is written using :func:`~ekmmeters.Meter.setMaxDemandInterval`, which
can return True or False. It accepts values in the set :class:`~ekmmeters.MaxDemandInterval`.

.. code-block:: python
   :emphasize-lines: 1
   :linenos:

   if my_meter.setMaxDemandInterval(MaxDemandInterval.Daily):
        print "Success"

Pulse Output Ratio
******************

The pulse output ratio is set using :func:`~ekmmeters.V4Meter.setPulseOutputRatio`, which
can return True or False. The value must be in the set :class:`~ekmmeters.PulseOutput`.
The field Pulse_Output_Ratio is is returned in every read request.

.. code-block:: python
   :emphasize-lines: 1, 3
   :linenos:

   if my_meter.setPulseOutputRatio(PulseOutput.Ratio_5):
       if my_meter.request():
           po_str = my_meter.getField(Field.Pulse_Output_Ratio)
           print po_str

Pulse Input Ratio
*****************

The pulse input ratios is set using :func:`~ekmmeters.V4Meter.setPulseInputRatio`, which
can return True or False.

Each of the three pulse lines has an integer input ratio (how many times you
must close the pulse circuit to register one pulse).  The fields Pulse_Ratio_1, Pulse_Ratio_2 and
Pulse_Ratio_3 are returned with every read request.  The example below shows line one being set.

.. code-block:: python
   :emphasize-lines: 1, 3
   :linenos:

   if my_meter.setPulseInputRatio(Pulse.Ln1, 55):
       if my_meter.request():
           pr_str = my_meter.getField(Field.Pulse_Ratio_1)
           print pr_str

Set Relay
*********

The relay is toggled using the method :func:`~ekmmeters.V4Meter.setRelay`, which
can return True or False.

The V4 Omnimeter has 2 relays, which can hold permanently or for a requested
duration.  The interval limits are in :class:`~ekmmeters.RelayInterval`, the relay to
select in :class:`~ekmmeters.Relay`, and the requested state in :class:`~ekmmeters.RelayState`.

If hold-and-stay value is the zero interval.  Using the hold constant, Min or 0
will switch the default state on or off (:class:`~ekmmeters.RelayState`).

.. code-block:: python
   :emphasize-lines: 1, 2, 3, 5
   :linenos:

   if my_meter.setRelay(RelayInterval.Hold, 
                        Relay.Relay1, 
                        RelayState.RelayOpen):
                        
       if my_meter.setRelay(2, Relay.Relay1, RelayState.RelayClose):
           print "Complete"

Set Meter Time
**************

The meter time, which is used by the meter to calculate and store time of use tariffs,
is set using the method :func:`~ekmmeters.VMeter.setTime`, and returns True or False.
The Meter_Time field is returned with every request.  The method :func:`~ekmmeters.VMeter.splitEkmDate` 
(which takes an integer) will break the date out into constituent parts.

In practice, it is quite difficult to corrupt the meter time, but if it becomes invalid,
a request can return a '?' in one of the field positions.    In that case your cast to int
will throw a ValueException.

EKM meter time is stored in a proprietary year-first format requiring day of week.
The API will strip off the century and calculate day of week for you.

Note the meter time is not the same as the timestamp at read, which every agent should
capture.  Your computer clock, which is calibrated to a time service, is more accurate. The
API does not make any assumptions about how you will use Meter_Time, what time
zones to employ, or the desirability of periodic corrections (though you can use this library
to do all those things).

.. code-block:: python
   :emphasize-lines: 8,10,11
   :linenos:

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

Zero Resettable
***************

The V4 fields Resettable_Rev_kWh_Tot and Resettable_kWh_Tot are zeroed with
function :func:`~ekmmeters.V4Meter.setZeroResettableKWH`, which returns True or False.

.. code-block:: python
   :emphasize-lines: 1,3,4
   :linenos:

   if my_meter.setZeroResettableKWH():
       if my_meter.request():
           print my_meter.getField(Field.Resettable_Rev_kWh_Tot)
           print my_meter.getField(Field.Resettable_kWh_Tot)


Season Schedules
****************

There are eight schedules, each with four tariff periods.  Schedules can be
assigned to seasons, with each season defined by a start day and month.

The season definitions are set with :func:`~ekmmeters.Meter.setSeasonSchedules`,
which returns True or False.  :func:`~ekmmeters.Meter.setSeasonSchedules`
can use an internal meter buffer or a passed dictionary.  Using the internal
buffer and :func:`~ekmmeters.Meter.assignSeasonSchedule` is the simplest approach.

While you can pass an int, using :class:`~ekmmeters.Seasons` and :class:`~ekmmeters.Schedules`
for the parameters is strongly recommended.

.. code-block:: python
   :emphasize-lines: 1, 2, 3, 4, 6
   :linenos:

   my_meter.assignSeasonSchedule(Seasons.Season_1, 1, 1, Schedules.Schedule_1)
   my_meter.assignSeasonSchedule(Seasons.Season_2, 3, 21, Schedules.Schedule_2)
   my_meter.assignSeasonSchedule(Seasons.Season_3, 6, 20, Schedules.Schedule_3)
   my_meter.assignSeasonSchedule(Seasons.Season_4, 9, 21, Schedules.Schedule_8)

   if my_meter.setSeasonSchedules():
       print "Success"

The method :func:`~ekmmeters.Meter.assignSeasonSchedule` will return False if the values are
out of bounds (though this was omitted from the example above for simplicity).

You can also populate the season schedule using a dictionary, which simplifies
loading a meter from passed JSON.

.. code-block:: python
   :emphasize-lines: 1, 15
   :linenos:

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
********************

A schedule is defined by up to four tariff periods, each with a start hour
and minute.  The meter will manage up to eight schedules.

Schedules are set one at a time via :func:`~ekmmeters.Meter.setScheduleTariffs`, 
returning True or False.   The simplest way to set up the call is with
:func:`~ekmmeters.Meter.assignSeasonSchedule`, which writes to the meter object
internal buffer.  The sets :class:`~ekmmeters.Schedules` and  :class:`~ekmmeters.Tariffs` are
provided for readability and convenience.

The following example creates one schedule with tariffs beginning at
midnight (rate = 1), 5:30 am (rate = 2), noon (rate = 3), and 5:30 pm (rate 1).


.. code-block:: python
   :emphasize-lines: 1, 2, 3, 4, 6
   :linenos:

   my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_1, 0,0,1)
   my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_2, 5,30,2)
   my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_3, 12,0,3)
   my_meter.assignScheduleTariff(Schedules.Schedule_1, Tariffs.Tariff_4, 17,30,1)

   if (my_meter.setScheduleTariffs()):
       print "Success"

Note that :func:`~ekmmeters.Meter.assignSeasonSchedule` should be tested for False in
a production deployment.

You can also use the range(Extents.<name>) iterator to define all the schedules at once. The test
below sets the first tariff and then steps hour and minute for the next three.

.. code-block:: python
   :emphasize-lines: 1, 7
   :linenos:

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
   :emphasize-lines: 1, 16
   :linenos:

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

Holiday Dates
*************

A list of up to 20 holidays can be set to use a single schedule (which applies 
the relevant time of use tariffs to your holidays).  The list of holiday dates is 
written with :func:`~ekmmeters.Meter.setHolidayDates`, which returns True or False.

Because the holiday list is relatively long, it is the only block without a set of
helper constants: if you use :func:`~ekmmeters.Meter.assignHolidayDate` directly,
the holiday is described by an integer from 0 to 19.

A more common use case will see all holidays stored and set at once. The
range(Extents.Holidays) idiom can be used to fill the holiday table:

.. code-block:: python
   :emphasize-lines: 1, 43
   :linenos:

   for holiday in range(Extents.Holidays):
       day = random.randint(1,28)
       mon = random.randint(1,12)
       my_meter.assignHolidayDate(holiday, mon, day)

   my_meter.setHolidayDates()

As with the other settings commands, a dictionary can be passed to :func:`~ekmmeters.Meter.setHolidayDates`
for JSON and XML support.

.. code-block:: python
   :emphasize-lines: 1, 43
   :linenos:

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

LCD Display
***********

A V4 Omnimeter alternates through up to 40 display items.  There are 42
possible display fields, defined in :class:`~ekmmeters.LCDItems`.

The simplest way to set display items is with the :func:`~ekmmeters.V4Meter.setLCDCmd`  call,
which takes a list of :class:`~ekmmeters.LCDItems` and returns True or False.


.. code-block:: python
   :emphasize-lines: 1, 2
   :linenos:

   lcd_items = [LCDItems.RMS_Volts_Ln_1, LCDItems.Line_Freq]
   if my_meter.setLCDCmd(lcd_items):
       print "Meter should now show Line 1 Volts and Frequency."

While every other meter command call with more than a couple of parameters uses
a dictionary to organize the data, the LCD display items are a single list of
40 integers.  A JSON or XML call populated by integer codes is not a good thing.  You
can translate the name of any value in :class:`~ekmmeters.LCDItems` to a
corresponding integer with :func:`~ekmmeters.V4Meter.lcdString`.

.. code-block:: python
   :emphasize-lines: 1, 2, 4
   :linenos:

   lcd_items = [my_meter.lcdString("RMS_Volts_Ln_1"),
                my_meter.lcdString("Line_Freq")]

   if my_meter.setLCDCmd(lcd_items):
       print "Meter should now show Line 1 Volts and Frequency."

Read Settings
*************

The tariff data used by the Omnimeter amounts to a small relational database, compressed
into fixed length lists.  There are up to eight schedules, each schedule can track up to
four tariff periods, and schedules can be assigned to holidays, weekends, and seasons.  The running
kWh and reverse kWh for each tariff period is returned with every read, and can be
requested for the last six recorded months.

The simplest way get the data is all at once, with :func:`~ekmmeters.VMeter.readSettings`, which
returns True or False.  As it combines 5 read commands, :func:`~ekmmeters.VMeter.readSettings` takes
longer than most other API calls.

The data is easy to get but harder to walk.  If you do not want to manage offsets and position,
you can use the "for <item> in range(Extents.<items>" iteration style, below.  Since the lists on
the meter are always the same length, you can use the code below as it is, and put your own
storage or send function at the bottom of each loop.

We start by reading all the settings tables out the meter object buffers.

.. code-block:: python
   :emphasize-lines: 12, 14, 16
   :linenos:

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
   :emphasize-lines: 9, 12
   :linenos:

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

And continue to list the 20 holidays and their assigned schedule, plus the assigned
weekend schedule.

.. code-block:: python
   :emphasize-lines: 5, 8, 15
   :linenos:

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

Without the print statements -- assuming you are just pulling the meter data
out into your own storage or display, and you can write my_save_tariff(),
my_save_month(), my_save_holidays() and my_save_holiday_weekend() functions --
the extraction traversal is much shorter.  (Please note that unlike every
other example on this page, the code below isn't runnable --- the my_save functions
are just placeholders for your own database writes or display calls).

.. code-block:: python
   :emphasize-lines: 4, 8, 12, 15, 16
   :linenos:

    for schedule in range(Extents.Schedules):
        for tariff in range(Extents.Tariffs):
            my_tariff_tuple = my_meter.extractScheduleTariff(schedule, tariff)
            my_save_tariff(my_tariff_tuple)  # handle the tupe printed above

    for month in range(Extents.Months):
        my_months_tuple = my_meter.extractMonthTariff(month)
        my_save_month(my_months_tuple) # handle the tuple printed above

   for holiday in range(Extents.Holidays):
        holidaydate = my_meter.extractHolidayDate(holiday)
        my_save_holidays(holidaydate.Month, holidaydate.Day)

    holiday_weekend_schedules = my_meter.extractHolidayWeekendSchedules()
    my_save_holiday_weekend(holiday_weekend_schedules.Holiday,
                            holiday_weekend_schedules.Weekend)


By writing four functions to bridge to your own storage or display, you can put away
all the non-request meter data quite simply.  Getting the bufffers directly
as dictionaries requires individual handling of all repeating fields, and appropriate
handling of both schedule blocks and both month blocks stored on the meter.  The following
example will print all the fields handled by the traversals above, using directly 
requested buffers.

.. code-block:: python
   :emphasize-lines: 3, 4, 5, 6, 7
   :linenos:

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


The readSettings() function breaks out to :func:`~ekmmeters.Meter.readScheduleTariffs`,
:func:`~ekmmeters.Meter.readMonthTariffs` and  :func:`~ekmmeters.Meter.readHolidayDates`.
If you take this approach you will need to call :func:`~ekmmeters.Meter.readMonthTariffs` twice, with ReadMonths.kWh
and ReadMonths.kWhReverse, and call :func:`~ekmmeters.Meter.readScheduleTariffs` twice as well,
with parameters ReadSchedules.Schedules_1_To_4 and ReadSchedules.Schedules_5_To_8.


Meter Observer
**************

This library is intended for programmers at all levels.  Most users seeking to summarize their data or generate
notifications can do so simply in the main polling loop.  However, sometimes only an observer pattern will do.
This is a very simple implementation and easily learned, but nothing in this example is necessary for mastery of
the API.

Each meter object has a chain of 0 to n observer objects.  When a request is issued, the meter calls the subclassed update() method of every observer object registered in its chain.  All observer objects descend from MeterObserver, and require an override of the Update method and constructor.

Given that most applications will poll tightly on Meter::request(), why would you do it this way? An observer pattern
might be appropriate if you are planning on doing a lot of work with the data for each read over an array of meters,
and want to keep the initial and read handling results in a single class  If you are familiar with the idiom, subclassing MeterObserver can be a fast way to create utilities.  The update method is exception wrapped: a failure in your override will not block the next read.

All of that said, the right way is the course the way which is simplest and clearest for your project.

Using set_notify.py an set_summarize.py is the most approachable way to explore the pattern.  All the required code is below, but it may be more rewarding to run from and modify the examples.  

We start by moddifying the skeleton we set up at the beginning of this page. with a request loop at the *bottom* of the file, right before closing the serial port.  It is a simple count limited request loop, and is useful when building software against this library.

.. code-block:: python
   :linenos:

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
you can close.  To create a notification observer, start by subclassing MeterObserver immediately before the snippet above.  The constructor sets a startup test condition and initializes the last pulse count used for comparison.

.. code-block:: python
   :emphasize-lines: 9
   :linenos:

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

Note that our Update() override gets the native (float) value directly, using MeterData.NativeValue.  It could as easily return MeterData.StringValue, and cast.  The first update() sets the initial comparison value.  Subsequent update() calls compare the pulse count and check to see if there is a change.  The doNotify() method is our triggered event, and can of course do anything Python can.

And finally -- right before dropping into our poll loop, we instantiate our subclassed MeterObserver, and register it in the
meter's observer chain.  We also put the pulse count on the LCD, and set the input ratio to one so every time we close
the pulse input, we fire our event.


.. code-block:: python
   :emphasize-lines: 1, 2
   :linenos:

   my_observer = ANotifyObserver()
   my_meter.registerObserver(my_observer)

   my_meter.setLCDCmd([LCDItems.Pulse_Cn_1])
   my_meter.setPulseInputRatio(Pulse.Ln1, 1)


This example is found in full in the github examples directory for ekmmeters, as set_notifypy.
A second example, set_summarize.py,  provides a MeterObserver which keeps a voltage
summary over an arbitrary number of seconds, passed in the constructor.  While slightly longer than the example above,
it does not require wiring the meter pulse inputs.



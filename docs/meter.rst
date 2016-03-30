Meter Class
-----------

The Meter class is the base class for V3Meter and V4Meter.  It is never called directly. It encapsulates
the next data to send, the last data read, and all of the possible serial commands.

.. currentmodule:: ekmmeters
.. toctree::
   :maxdepth: 2
.. autoclass:: Meter
    :members:   getMeterAddress, setMaxDemandPeriod, setMaxDemandResetInterval, setMeterPassword,
                setSeasonSchedules, setMaxDemandResetNow, setTime, setCTRatio, setHolidayDates,
                setWeekendHolidaySchedules, request, readSettings, readHolidayDates, readMonthTariffs,
                readScheduleTariffs, registerObserver, unregisterObserver, readCmdMsg, splitEkmDate,
                jsonRender, getReadBuffer, getHolidayDatesBuffer, getMonthsBuffer, getSchedulesBuffer,
                serialPostEnd, clearCmdMsg, initParamLists,assignScheduleTariff,
                setScheduleTariffs, assignSeasonSchedule, assignHolidayDate, extractScheduleTariff,
                extractMonthTariff, extractHolidayDate, extractHolidayWeekendSchedules

SerialBlock Class
*****************

Serial block is a simple subclass of OrderedDictionary.  The subclassing is primarily cautionary.

.. autoclass:: SerialBlock



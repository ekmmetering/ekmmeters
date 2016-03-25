Meter Class
-----------

The Meter class is the base class for V3Meter and V4Meter.  It is never called directly. It encapsulates
the next data to send, the last data read, and all of the possible serial commands.

.. currentmodule:: ekmmeters
.. toctree::
   :maxdepth: 2
.. autoclass:: Meter
    :members:   getMeterAddress, setMaxDemandPeriod, setMaxDemandInterval, setMeterPassword,
                setSeasonSchedules, setMaxDemandReset, setTime, setCTRatio, setHolidayDates,
                setWeekendHolidaySchedules, request, readSettings, readHolidayDates, readMonthTariffs,
                readScheduleTariffs, registerObserver, unregisterObserver, readCmdMsg, splitEkmDate,
                jsonRender, getReadBuffer, getHolidayDatesBuffer, getMonthsBuffer, getSchedulesBuffer,
                serialPostEnd, clearCmdMsg, serialCmdPwdAuth, calc_crc16, initParamLists,
                initSchd_1_to_4, initSchd_5_to_8, initHldyDates, initMons, initRevMons, assignScheduleTariff,
                setScheduleTariffs, assignSeasonSchedule, assignHolidayDate, extractScheduleTariff,
                extractMonthTariff, extractHolidayDate, extractHolidayWeekendSchedules

.. autoclass:: SerialBlock



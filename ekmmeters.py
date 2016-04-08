""" ekmmeters.py
(c) 2015, 2016 EKM Metering.

The ekmmeters library API for v3 and v4 EKM Omnimeters.

Tested and released under Python 2.6 (tested Centos 6.x only)
and Python 2.7x (Python and Iron Python).

This software is provided under an MIT license:
    https://opensource.org/licenses/MIT
"""
import struct
import time
from collections import OrderedDict
from collections import namedtuple
from datetime import date
import sqlite3
import binascii
import serial
import traceback
import sys
import json
import datetime


def ekm_no_log(output_string):
    """ No-op predefined module level logging callback.

    Args:
        output_string (str): string to output.
    """
    pass


def ekm_print_log(output_string):
    """ Simple print predefined module level logging callback.

    Args:
        output_string (str): string to output.

    Returns:

    """
    print(output_string)
    pass


global ekmmeters_log_func  #: Module level log or diagnostic print
ekmmeters_log_func = ekm_no_log
global ekmmeters_log_level
ekmmeters_log_level = 3
global __EKMMETERS_VERSION
__EKMMETERS_VERSION = "0.2.4"


def ekm_set_log(function_name):
    """ Set predefined or user-defined module level log output function.

    Args:
        function_name (function):  function taking 1 string returning nothing.
    """
    global ekmmeters_log_func
    ekmmeters_log_func = function_name
    pass


def ekm_log(logstr, priority=3):
    """ Send string to module level log

    Args:
        logstr (str): string to print.
        priority (int): priority, supports 3 (default) and 4 (special).
    """
    if priority <= ekmmeters_log_level:
        dt = datetime.datetime
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M.%f")
        ekmmeters_log_func("[EKM Meter Debug Message: " + stamp + "] -> " + logstr)
    pass


def ekm_set_log_level(level=3):
    """ Set the logging level.
    Args:
        level (int): cutoff level (print at level and below).
    """
    global ekmmeters_log_level
    ekmmeters_log_level = level
    pass


class MeterData():
    """ Each :class:`~ekmmeters.SerialBlock` value is an array with these offsets. All Omnimeter versions.

    =============== =
    SizeValue       0
    TypeValue       1
    ScaleValue      2
    StringValue     3
    NativeValue     4
    CalculatedFlag  5
    EventFlag       6
    =============== =


    """
    SizeValue = 0
    TypeValue = 1
    ScaleValue = 2
    StringValue = 3
    NativeValue = 4
    CalculatedFlag = 5
    EventFlag = 6


class MaxDemandResetInterval():
    """ As passed in :func:`~ekmmeters.Meter.setMaxDemandResetInterval`.  V4 Omnimeters.

    ======= =
    Off     0
    Monthly 1
    Weekly  2
    Daily   3
    Hourly  4
    ======= =

    """
    Off = 0
    Monthly = 1
    Weekly = 2
    Daily = 3
    Hourly = 4


class MaxDemandPeriod():
    """As passed in :func:`~ekmmeters.Meter.setMaxDemandPeriod`. V3 and V4 Omnimeters.

    ============= =
    At_15_Minutes 1
    At_30_Minutes 2
    At_60_Minutes 3
    ============= =

    """
    At_15_Minutes = 1
    At_30_Minutes = 2
    At_60_Minutes = 3


class LCDItems():
    """ As passed in :func:`~ekmmeters.V4Meter.addLcdItem`.  V4 Omnimeters.

    =================== ==
    kWh_Tot              1
    Rev_kWh_Tot          2
    RMS_Volts_Ln_1       3
    RMS_Volts_Ln_2       4
    RMS_Volts_Ln_3       5
    Amps_Ln_1            6
    Amps_Ln_2            7
    Amps_Ln_3            8
    RMS_Watts_Ln_1       9
    RMS_Watts_Ln_2      10
    RMS_Watts_Ln_3      11
    RMS_Watts_Tot       12
    Power_Factor_Ln_1   13
    Power_Factor_Ln_2   14
    Power_Factor_Ln_3   15
    kWh_Tariff_1        16
    kWh_Tariff_2        17
    kWh_Tariff_3        18
    kWh_Tariff_4        19
    Rev_kWh_Tariff_1    20
    Rev_kWh_Tariff_2    21
    Rev_kWh_Tariff_3    22
    Rev_kWh_Tariff_4    23
    Reactive_Pwr_Ln_1   24
    Reactive_Pwr_Ln_2   25
    Reactive_Pwr_Ln_3   26
    Reactive_Pwr_Tot    27
    Line_Freq           28
    Pulse_Cnt_1         29
    Pulse_Cnt_2         30
    Pulse_Cnt_3         31
    kWh_Ln_1            32
    Rev_kWh_Ln_1        33
    kWh_Ln_2            34
    Rev_kWh_Ln_2        35
    kWh_Ln_3            36
    Rev_kWh_Ln_3        37
    Reactive_Energy_Tot 38
    Max_Demand_Rst      39
    Rev_kWh_Rst         40
    State_Inputs        41
    Max_Demand          42
    =================== ==

    """
    kWh_Tot = 1
    Rev_kWh_Tot = 2
    RMS_Volts_Ln_1 = 3
    RMS_Volts_Ln_2 = 4
    RMS_Volts_Ln_3 = 5
    Amps_Ln_1 = 6
    Amps_Ln_2 = 7
    Amps_Ln_3 = 8
    RMS_Watts_Ln_1 = 9
    RMS_Watts_Ln_2 = 10
    RMS_Watts_Ln_3 = 11
    RMS_Watts_Tot = 12
    Power_Factor_Ln_1 = 13
    Power_Factor_Ln_2 = 14
    Power_Factor_Ln_3 = 15
    kWh_Tariff_1 = 16
    kWh_Tariff_2 = 17
    kWh_Tariff_3 = 18
    kWh_Tariff_4 = 19
    Rev_kWh_Tariff_1 = 20
    Rev_kWh_Tariff_2 = 21
    Rev_kWh_Tariff_3 = 22
    Rev_kWh_Tariff_4 = 23
    Reactive_Pwr_Ln_1 = 24
    Reactive_Pwr_Ln_2 = 25
    Reactive_Pwr_Ln_3 = 26
    Reactive_Pwr_Tot = 27
    Line_Freq = 28
    Pulse_Cnt_1 = 29
    Pulse_Cnt_2 = 30
    Pulse_Cnt_3 = 31
    kWh_Ln_1 = 32
    Rev_kWh_Ln_1 = 33
    kWh_Ln_2 = 34
    Rev_kWh_Ln_2 = 35
    kWh_Ln_3 = 36
    Rev_kWh_Ln_3 = 37
    Reactive_Energy_Tot = 38
    Max_Demand_Rst = 39
    Rev_kWh_Rst = 40
    State_Inputs = 41
    Max_Demand = 42


class CTRatio():
    """ As passed in :func:`~ekmmeters.Meter.setCTRatio`.  V3 and V4 Omnimeters.

    ========= ====
    Amps_100   100
    Amps_200   200
    Amps_400   400
    Amps_600   600
    Amps_800   800
    Amps_1000 1000
    Amps_1200 1200
    Amps_1500 1500
    Amps_2000 2000
    Amps_3000 3000
    Amps_4000 4000
    Amps_5000 5000
    ========= ====

    """
    Amps_100 = 200
    Amps_200 = 200
    Amps_400 = 400
    Amps_600 = 600
    Amps_800 = 800
    Amps_1000 = 1000
    Amps_1200 = 1200
    Amps_1500 = 1500
    Amps_2000 = 2000
    Amps_3000 = 3000
    Amps_4000 = 4000
    Amps_5000 = 5000


class Field():
    """ Union of all V3A and V4AB Fields Returned.

    Use these values to directy get read data with
    Meter::getField() or in directy traversal of
    :class:`~ekmmeters.SerialBlock`.

    ========================= =======================
    Meter_Address             12 character Mfr ID'
    Time_Stamp                Epoch in ms at read
    Model                     Meter model
    Firmware                  Meter firmware
    kWh_Tot                   Meter power total
    kWh_Tariff_1              Power in timeslot 1
    kWh_Tariff_2              Power in timeslot 2
    kWh_Tariff_3              Power in timeslot 3
    kWh_Tariff_4              Power in timeslot 4
    Rev_kWh_Tot               Meter rev. total
    Rev_kWh_Tariff_1          Rev power in timeslot 1
    Rev_kWh_Tariff_2          Rev power in timeslot 2
    Rev_kWh_Tariff_3          Rev power in timeslot 3
    Rev_kWh_Tariff_4          Rev power in timeslot 4
    RMS_Volts_Ln_1            Volts line 1
    RMS_Volts_Ln_2            Volts line 2
    RMS_Volts_Ln_3            Volts line 3
    Amps_Ln_1                 Current line 1
    Amps_Ln_2                 Current line 2
    Amps_Ln_3                 Current line 3
    RMS_Watts_Ln_1            Instantaneous watts line 1
    RMS_Watts_Ln_2            Instantaneous watts line 2
    RMS_Watts_Ln_3            Instantaneous watts line 3
    RMS_Watts_Tot             Instantaneous watts 1 + 2 + 3
    Cos_Theta_Ln_1            Prefix in :class:`~ekmmeters.CosTheta`
    Cos_Theta_Ln_2            Prefix in :class:`~ekmmeters.CosTheta`
    Cos_Theta_Ln_3            Prefix in :class:`~ekmmeters.CosTheta`
    Max_Demand                Demand in period
    Max_Demand_Period         :class:`~ekmmeters.MaxDemandPeriod`
    Meter_Time                :func:`~ekmmeters.Meter.setTime` and :func:`~ekmmeters.Meter.splitEkmDate`
    CT_Ratio                  :class:`~ekmmeters.Meter.setCTRatio`
    Pulse_Cnt_1               Pulse Count Line 1
    Pulse_Cnt_2               Pulse Count Line 2
    Pulse_Cnt_3               Pulse Count Line 3
    Pulse_Ratio_1             :func:`~ekmmeters.V4Meter.setPulseInputRatio`
    Pulse_Ratio_2             :func:`~ekmmeters.V4Meter.setPulseInputRatio`
    Pulse_Ratio_3             :func:`~ekmmeters.V4Meter.setPulseInputRatio`
    State_Inputs'             :class:`~ekmmeters.StateIn`
    Power_Factor_Ln_1         EKM Power Factor
    Power_Factor_Ln_2         EKM Power Factor
    Power_Factor_Ln_3         EKM Power Factor
    Reactive_Energy_Tot       Total VAR
    kWh_Ln_1                  Line 1 power
    kWh_Ln_2                  Line 2 power
    kWh_Ln_3                  Line 3 power
    Rev_kWh_Ln_1              Line 1 reverse power
    Rev_kWh_Ln_2              Line 2 reverse power
    Rev_kWh_Ln_3              Line 3 revers power
    Resettable_kWh_Tot        :func:`~ekmmeters.V4Meter.setZeroResettableKWH`
    Resettable_Rev_kWh_Tot    :func:`~ekmmeters.V4Meter.setZeroResettableKWH`
    Reactive_Pwr_Ln_1         VAR Line 1
    Reactive_Pwr_Ln_2         VAR Line 2
    Reactive_Pwr_Ln_3         VAR Line 3
    Reactive_Pwr_Tot          VAR Total
    Line_Freq                 Freq. Hz.
    State_Watts_Dir           :class:`~ekmmeters.DirectionFlag`
    State_Out                 :class:`~ekmmeters.StateOut`
    kWh_Scale                 :class:`~ekmmeters.ScaleKWH`
    RMS_Watts_Max_Demand      Power peak in period
    Pulse_Output_Ratio        :class:`~ekmmeters.PulseOutput`
    Net_Calc_Watts_Ln_1       RMS_Watts with Direction
    Net_Calc_Watts_Ln_2       RMS_Watts with Direction
    Net_Calc_Watts_Ln_3       RMS_Watts with Direction
    Net_Calc_Watts_Tot        RMS_Watts with Direction
    Status_A                  Reserved diagnostic.
    Status_B                  Reserved diagnostic.
    Status_C                  Reserved diagnostic.
    ========================= =======================

    Power_Factor is the only power factor measurement supported by
    upstring EKM products.  The original Cos Theta value
    is provided as an API-only feature.

    """
    Meter_Address = 'Meter_Address'
    Time_Stamp = 'Time_Stamp'
    Model = 'Model'
    Firmware = 'Firmware'
    kWh_Tot = 'kWh_Tot'
    kWh_Tariff_1 = 'kWh_Tariff_1'
    kWh_Tariff_2 = 'kWh_Tariff_2'
    kWh_Tariff_3 = 'kWh_Tariff_3'
    kWh_Tariff_4 = 'kWh_Tariff_4'
    Rev_kWh_Tot = 'Rev_kWh_Tot'
    Rev_kWh_Tariff_1 = 'Rev_kWh_Tariff_1'
    Rev_kWh_Tariff_2 = 'Rev_kWh_Tariff_2'
    Rev_kWh_Tariff_3 = 'Rev_kWh_Tariff_3'
    Rev_kWh_Tariff_4 = 'Rev_kWh_Tariff_4'
    RMS_Volts_Ln_1 = 'RMS_Volts_Ln_1'
    RMS_Volts_Ln_2 = 'RMS_Volts_Ln_2'
    RMS_Volts_Ln_3 = 'RMS_Volts_Ln_3'
    Amps_Ln_1 = 'Amps_Ln_1'
    Amps_Ln_2 = 'Amps_Ln_2'
    Amps_Ln_3 = 'Amps_Ln_3'
    RMS_Watts_Ln_1 = 'RMS_Watts_Ln_1'
    RMS_Watts_Ln_2 = 'RMS_Watts_Ln_2'
    RMS_Watts_Ln_3 = 'RMS_Watts_Ln_3'
    RMS_Watts_Tot = 'RMS_Watts_Tot'
    Cos_Theta_Ln_1 = 'Cos_Theta_Ln_1'
    Cos_Theta_Ln_2 = 'Cos_Theta_Ln_2'
    Cos_Theta_Ln_3 = 'Cos_Theta_Ln_3'
    Max_Demand = 'Max_Demand'
    Max_Demand_Period = 'Max_Demand_Period'
    Meter_Time = 'Meter_Time'
    CT_Ratio = 'CT_Ratio'
    Pulse_Cnt_1 = 'Pulse_Cnt_1'
    Pulse_Cnt_2 = 'Pulse_Cnt_2'
    Pulse_Cnt_3 = 'Pulse_Cnt_3'
    Pulse_Ratio_1 = 'Pulse_Ratio_1'
    Pulse_Ratio_2 = 'Pulse_Ratio_2'
    Pulse_Ratio_3 = 'Pulse_Ratio_3'
    State_Inputs = 'State_Inputs'
    Power_Factor_Ln_1 = 'Power_Factor_Ln_1'
    Power_Factor_Ln_2 = 'Power_Factor_Ln_2'
    Power_Factor_Ln_3 = 'Power_Factor_Ln_3'
    Reactive_Energy_Tot = 'Reactive_Energy_Tot'
    kWh_Ln_1 = 'kWh_Ln_1'
    kWh_Ln_2 = 'kWh_Ln_2'
    kWh_Ln_3 = 'kWh_Ln_3'
    Rev_kWh_Ln_1 = 'Rev_kWh_Ln_1'
    Rev_kWh_Ln_2 = 'Rev_kWh_Ln_2'
    Rev_kWh_Ln_3 = 'Rev_kWh_Ln_3'
    Resettable_kWh_Tot = 'Resettable_kWh_Tot'
    Resettable_Rev_kWh_Tot = 'Resettable_Rev_kWh_Tot'
    Reactive_Pwr_Ln_1 = 'Reactive_Pwr_Ln_1'
    Reactive_Pwr_Ln_2 = 'Reactive_Pwr_Ln_2'
    Reactive_Pwr_Ln_3 = 'Reactive_Pwr_Ln_3'
    Reactive_Pwr_Tot = 'Reactive_Pwr_Tot'
    Line_Freq = 'Line_Freq'
    State_Watts_Dir = 'State_Watts_Dir'
    State_Out = 'State_Out'
    kWh_Scale = 'kWh_Scale'
    RMS_Watts_Max_Demand = 'RMS_Watts_Max_Demand'
    Pulse_Output_Ratio = 'Pulse_Output_Ratio'
    Net_Calc_Watts_Ln_1 = 'Net_Calc_Watts_Ln_1'
    Net_Calc_Watts_Ln_2 = 'Net_Calc_Watts_Ln_2'
    Net_Calc_Watts_Ln_3 = 'Net_Calc_Watts_Ln_3'
    Net_Calc_Watts_Tot = 'Net_Calc_Watts_Tot'
    Status_A = 'Status_A'
    Status_B = 'Status_B'
    Status_C = 'Status_C'


class Seasons():
    """ As passed to :func:`~ekmmeters.Meter.assignSeasonSchedule`.  V3 and V4 Omnimeters.

    assign* methods use a zero based index for seasons.
    You may set a season using one of these constants
    or fill and iterate over range(Extents.Seaons).

    ======== =
    Season_1 0
    Season_2 1
    Season_3 2
    Season_4 3
    ======== =

    """
    Season_1 = 0
    Season_2 = 1
    Season_3 = 2
    Season_4 = 3


class Months():
    """ As  passed to :func:`~ekmmeters.Meter.extractMonthTariff`.  V3 and V4 Omnimeters.

    ======== =
    Month_1  0
    Month_2  1
    Month_3  2
    Month_4  3
    Month_5  4
    Month_6  5
    ======== =

    """
    Month_1 = 0
    Month_2 = 1
    Month_3 = 2
    Month_4 = 3
    Month_5 = 4
    Month_6 = 5


class Tariffs():
    """ As passed to :func:`~ekmmeters.Meter.assignScheduleTariff`. V3 and V4 Omnimeters.

     ========  =
     Tariff_1  0
     Tariff_2  1
     Tariff_3  2
     Tariff_4  3
     ========  =

    """
    Tariff_1 = 0
    Tariff_2 = 1
    Tariff_3 = 2
    Tariff_4 = 3


class Extents():
    """ Traversal extents to use with for range(Extent) idiom.  V3 and V4 Omnimeters.

    Use of range(Extent.Entity) as an iterator insures safe
    assignnment without off by one errors.

    ========== ==
    Seasons     4
    Holidays   20
    Tariffs     4
    Schedules   8
    Months      6
    ========== ==

    """
    Seasons = 4
    Holidays = 20
    Tariffs = 4
    Schedules = 8
    Months = 6


class PulseOutput():
    """ As passed to :func:`~ekmmeters.V4Meter.setPulseOutputRatio`.  V4 Omnimeters.

    ========== ==========
    Ratio_1    Ratio_40
    Ratio_2    Ratio_50
    Ratio_4    Ratio_80
    Ratio_5    Ratio_100
    Ratio_8    Ratio_200
    Ratio_10   Ratio_400
    Ratio_16   Ratio_800
    Ratio_20   Ratio_1600
    Ratio_25
    ========== ==========

    """
    Ratio_1 = 1
    Ratio_2 = 2
    Ratio_4 = 4
    Ratio_5 = 5
    Ratio_8 = 8
    Ratio_10 = 10
    Ratio_16 = 16
    Ratio_20 = 20
    Ratio_25 = 25
    Ratio_40 = 40
    Ratio_50 = 50
    Ratio_80 = 80
    Ratio_100 = 100
    Ratio_200 = 200
    Ratio_400 = 400
    Ratio_800 = 800
    Ratio_1600 = 1600


class Pulse():
    """ As passed to :func:`~ekmmeters.V4Meter.setPulseInputRatio`.  V4 Omnimeters.

    Simple constant to clarify call.

    === =
    In1 1
    In2 2
    In3 3
    === =

    """
    In1 = 1
    In2 = 2
    In3 = 3


class Schedules():
    """ Allowed schedules.  V3 and V4 Omnimeters.

    Schedules on the meter are zero based, these apply to most passed
    schedule parameters.

    ========== =
    Schedule_1 0
    Schedule_2 1
    Schedule_3 2
    Schedule_4 3
    Schedule_5 4
    Schedule_6 5
    Schedule_7 6
    Schedule_8 7
    ========== =

    """
    Schedule_1 = 0
    Schedule_2 = 1
    Schedule_3 = 2
    Schedule_4 = 3
    Schedule_5 = 4
    Schedule_6 = 5
    Schedule_7 = 6
    Schedule_8 = 7


class ReadSchedules():
    """ For :func:`~ekmmeters.Meter.readScheduleTariffs` and :func:`~ekmmeters.Meter.getSchedulesBuffer`.  V3 and V4.

    ================  ==================================
    Schedules_1_To_4  1st 4 blocks tariffs and schedules
    Schedules_5_To_8  2nd 4 blocks tariffs and schedules
    ================  ==================================

    """

    Schedules_1_To_4 = 0
    Schedules_5_To_8 = 1


class ReadMonths():
    """ As passed to :func:`~ekmmeters.Meter.readMonthTariffs` and :func:`~ekmmeters.Meter.getMonthsBuffer`.  V3 and V4.

    Use to select the forward or reverse six month tariff data.

    ========== ================================
    kWh        Select forward month tariff data
    kWhReverse Select reverse month tariff data
    ========== ================================

    """
    kWh = 1
    kWhReverse = 2


class DirectionFlag():
    """ On V4, State_Watts_Dir mask shows RMS_Watts direction on line 1-3.

    The Direction flag is used to generate Calc_Net_Watts field on every
    read. Each word in constant is the direction of the corresponding at
    the moment of read.  Ex ForwardReverseForward means RMS_Watts lines one
    and three are positive, and line two is negtive.


    =====================  =
    ForwardForwardForward  1
    ForwardForwardReverse  2
    ForwardReverseForward  3
    ReverseForwardForward  4
    ForwardReverseReverse  5
    ReverseForwardReverse  6
    ReverseReverseForward  7
    ReverseReverseReverse  8
    =====================  =

    """
    ForwardForwardForward = 1
    ForwardForwardReverse = 2
    ForwardReverseForward = 3
    ReverseForwardForward = 4
    ForwardReverseReverse = 5
    ReverseForwardReverse = 6
    ReverseReverseForward = 7
    ReverseReverseReverse = 8


class ScaleKWH():
    """ Scaling or kWh values controlled by Fields.kWh.  V4 Omnimeters.

    If MeterData.ScaleValue is ScaleType.KWH, Fields.kWh_Scale one of these.

    =========== == ===========
    NoScale      0 no scaling
    Scale10      1 scale 10^-1
    Scale100     2 scale 10^-2
    EmptyScale  -1 Reserved
    =========== == ===========

    """
    NoScale = 0
    Scale10 = 1
    Scale100 = 2
    EmptyScale = -1


class ScaleType():
    """ Scale type defined in SerialBlock.  V4 Omnimeters.

    These values are set when a field is defined a SerialBlock.
    A Div10 or Div100 results in immediate scaling, otherwise
    the scaling is perfformed per the value in Field.kWh_Scale
    as described in ScaleKWH.

    ======  ==============================
    KWH     :class:`~ekmmeters.ScaleKWH`
    No      Do not scale
    Div10   Scale 10^-1
    Div100  Scale 10^-2
    ======  ==============================

    """
    KWH = "kwh"
    No = "None"
    Div10 = "10"
    Div100 = "100"


class FieldType():
    """ Every SerialBlock element has a field type.   V3 and V4 Omnimeters.

    Data arrives as ascii.  Field type determines disposition.
    The destination type is Python.

    ============ ==========================
    NoType       Not type assigned, invalid
    Hex          Implicit hex string
    Int          Implicit int
    Float        Implicit float
    String       Leave as string, terminate
    PowerFactor  EKM L or C prefixed pf
    ============ ==========================


    """
    NoType = "None"     #: no type assigned
    Hex = "hex"         #: leave as hexified string
    Int = "int"         #: int in python
    Float = "float"     #: float in python
    String = "string"   #: string in python
    PowerFactor = "pf"  #: do power factor conversion


class Relay():
    """ Relay specified in :func:`~ekmmeters.V4Meter.setRelay`.  V4 Omnimeters.

    ====== ================
    Relay1 OUT1 on V4 Meter
    Relay2 OUT2 on V4 Meter
    ====== ================

    """
    Relay1 = 1  #: Relay 1 Selection code for v4 meter
    Relay2 = 2  #: Relay 2 Selection code for v4 meter


class RelayState():
    """ Relay state in :func:`~ekmmeters.V4Meter.setRelay`.  V4 Omnimeters.

    =========== =
    RelayOpen   0
    RelayClosed 1
    =========== =

    """
    RelayOpen = 0   #: Relay Open command code for v4 meter
    RelayClose =  1  #: Relay Close command code for v4 meter


class RelayInterval():
    """ Relay interval in :func:`~ekmmeters.V4Meter.setRelay`.  V4 Omnimeters.

    ===== ======================
    Max   9999 seconds
    Min   0, parameter limit
    Hold  0 (lock relay state)
    ===== ======================

    """
    Max = 9999  #: Maximum wait
    Min = 0     #: Lowest legal value
    Hold = Min  #: Hold is just zero

class StateOut():
    """ Pulse output state at time of read.  V4 Omnimeters.

    =======  =
    OffOff   1
    OffOn    2
    OnOff    3
    OnOn     4
    =======  =

    """
    OffOff = 1
    OffOn = 2
    OnOff = 3
    OnOn = 4

class StateIn():
    """ State of each pulse line at time of read.  V4 Omnimeters.

    ================= =
    HighHighHigh      0
    HighHighLow       1
    HighLowHigh       2
    HighLowLow        3
    LowHighHigh       4
    LowHighLow        5
    LowLowHigh        6
    LowLowLow         7
    ================= =

    """
    HighHighHigh = 0
    HighHighLow = 1
    HighLowHigh = 2
    HighLowLow = 3
    LowHighHigh = 4
    LowHighLow = 5
    LowLowHigh = 6
    LowLowLow = 7

class CosTheta():
    """ Prefix characters returned in power factor. Note a cos of zero has one space.  V3 and V4 Omnimeters.

    """
    InductiveLag = "L"
    CapacitiveLead = "C"
    NoLeadOrLag = (" ")


class SerialBlock(OrderedDict):
    """ Simple subclass of collections.OrderedDict.

    Key is a :class:`~ekmmeters.Field` and value is :class:`~ekmmeters.MeterData` indexed array.

    The :class:`~ekmmeters.MeterData` points to one of the following:

    ==============  ==============================================
    SizeValue       Integer.  Equivalent to struct char[SizeValue]
    TypeValue       A :class:`~ekmmeters.FieldType` value.
    ScaleValue      A :class:`~ekmmeters.ScaleType` value.
    StringValue     Printable, scaled and formatted content.
    NativeValue     Converted, scaled value of field native type.
    CalculatedFlag  If True, not part of serial read, calculated.
    EventFlag       If True, state value
    ==============  ==============================================

    """

    def __init__(self):
        super(SerialBlock, self).__init__()


class SerialPort(object):
    """ Wrapper for serial port commands.

    It should only be necessary to create one SerialPort per real port.

    Object construction sets the class variables.  The port is opened with
    initPort(), and any serial exceptions will thrown at that point.

    The standard serial settings for v3 and v4 EKM meters are 9600 baud,
    7 bits, 1 stop bit, no parity.  The baud rate may be reset but all timings
    and test in this library are at 9600 baud.  Bits, stop and parity may not
    be changed.
    """

    def __init__(self, ttyport, baudrate=9600, force_wait = 0.1):
        """
        Args:
            ttyport (str): port name, ex 'COM3' '/dev/ttyUSB0'
            baudrate (int): optional, 9600 default and recommended
            force_wait(float) : optional post commnd sleep, if required
        """
        self.m_ttyport = ttyport
        self.m_baudrate = baudrate
        self.m_ser = None
        self.m_fd = None
        self.m_max_waits = 60
        self.m_wait_sleep = 0.05
        self.m_force_wait = force_wait
        self.m_init_wait = 0.2
        pass

    def initPort(self):
        """ Required initialization call, wraps pyserial constructor. """
        try:
            self.m_ser = serial.Serial(port=self.m_ttyport,
                                       baudrate=self.m_baudrate,
                                       timeout=0,
                                       parity=serial.PARITY_EVEN,
                                       stopbits=serial.STOPBITS_ONE,
                                       bytesize=serial.SEVENBITS,
                                       rtscts=False)
            ekm_log("Pyserial version = " + serial.VERSION)
            ekm_log("Port = " + self.m_ttyport)
            ekm_log("Rate = " + str(self.m_baudrate))
            time.sleep(self.m_init_wait)
            return True
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        return False

    def getName(self):
        """ Getter for serial port name

        Returns:
            string: name of serial port (ex: 'COM3', '/dev/ttyS0')
        """
        return self.m_ttyport

    def closePort(self):
        """ Passthrough for pyserial port close()."""
        self.m_ser.close()
        pass

    def write(self, output):
        """Passthrough for pyserial Serial.write().

        Args:
            output (str): Block to write to port
        """
        view_str = output.encode('ascii', 'ignore')
        if (len(view_str) > 0):
            self.m_ser.write(view_str)
            self.m_ser.flush()
            time.sleep(self.m_force_wait)
        pass

    def setPollingValues(self, max_waits, wait_sleep):
        """ Optional polling loop control

        Args:
            max_waits (int):   waits
            wait_sleep (int):  ms per wait
        """
        self.m_max_waits = max_waits
        self.m_wait_sleep = wait_sleep

    def getResponse(self, context=""):
        """ Poll for finished block or first byte ACK.
        Args:
            context (str): internal serial call context.

        Returns:
            string: Response, implict cast from byte array.
        """
        waits = 0  # allowed interval counter
        response_str = ""  # returned bytes in string default
        try:
            waits = 0  # allowed interval counter
            while (waits < self.m_max_waits):
                bytes_to_read = self.m_ser.inWaiting()
                if bytes_to_read > 0:
                    next_chunk = str(self.m_ser.read(bytes_to_read)).encode('ascii', 'ignore')
                    response_str += next_chunk
                    if (len(response_str) == 255):
                        time.sleep(self.m_force_wait)
                        return response_str
                    if (len(response_str) == 1) and (response_str.encode('hex') == '06'):
                        time.sleep(self.m_force_wait)
                        return response_str
                else:  # hang out -- half shortest expected interval (50 ms)
                    waits += 1
                    time.sleep(self.m_force_wait)
            response_str = ""

        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        return response_str


class MeterDB(object):
    """ Base class for single-table reads database abstraction."""

    def __init__(self, connection_string):
        """
        Args:
            connection_string (str): database appropriate connection string
        """
        self.m_connection_string = connection_string
        self.m_all_fields = SerialBlock()
        self.combineAB()
        pass

    def setConnectString(self, connection_string):
        """ Setter for connection string.
        Args:
            connection_string (str): Connection string.
        """
        self.m_connection_string = connection_string
        pass

    def combineAB(self):
        """ Use the serial block definitions in V3 and V4 to create one field list. """
        v4definition_meter = V4Meter()
        v4definition_meter.makeAB()
        defv4 = v4definition_meter.getReadBuffer()

        v3definition_meter = V3Meter()
        v3definition_meter.makeReturnFormat()
        defv3 = v3definition_meter.getReadBuffer()

        for fld in defv3:
            if fld not in self.m_all_fields:
                compare_fld = fld.upper()
                if not "RESERVED" in compare_fld and not "CRC" in compare_fld:
                    self.m_all_fields[fld] = defv3[fld]

        for fld in defv4:
            if fld not in self.m_all_fields:
                compare_fld = fld.upper()
                if not "RESERVED" in compare_fld and not "CRC" in compare_fld:
                    self.m_all_fields[fld] = defv4[fld]
        pass

    def mapTypeToSql(self, fld_type=FieldType.NoType, fld_len=0):
        """ Translate FieldType to portable SQL Type.  Override if needful.
        Args:
            fld_type (int): :class:`~ekmmeters.FieldType` in serial block.
            fld_len (int): Binary length in serial block

        Returns:
            string: Portable SQL type and length where appropriate.
        """
        if fld_type == FieldType.Float:
            return "FLOAT"
        elif fld_type == FieldType.String:
            return "VARCHAR(" + str(fld_len) + ")"
        elif fld_type == FieldType.Int:
            return "INT"
        elif fld_type == FieldType.Hex:
            return "VARCHAR(" + str(fld_len * 2) + ")"
        elif fld_type == FieldType.PowerFactor:
            return "VARCHAR(" + str(fld_len) + ")"
        else:
            ekm_log("Type " + str(type) + " not handled by mapTypeToSql, returned VARCHAR(255)")
            return "VARCHAR(255)"

    def fillCreate(self, qry_str):
        """ Return query portion below CREATE.
        Args:
            qry_str (str): String as built.

        Returns:
            string: Passed string with fields appended.
        """
        count = 0
        for fld in self.m_all_fields:
            fld_type = self.m_all_fields[fld][MeterData.TypeValue]
            fld_len = self.m_all_fields[fld][MeterData.SizeValue]
            qry_spec = self.mapTypeToSql(fld_type, fld_len)
            if count > 0:
                qry_str += ", \n"
            qry_str = qry_str + '   ' + fld + ' ' + qry_spec
            count += 1

        qry_str += (",\n\t" + Field.Time_Stamp + " BIGINT,\n\t" +
                    "Raw_A VARCHAR(512),\n\t" +
                    "Raw_B VARCHAR(512)\n)")

        return qry_str

    def sqlCreate(self):
        """ Reasonably portable SQL CREATE for defined fields.
        Returns:
            string: Portable as possible SQL Create for all-reads table.
        """
        count = 0
        qry_str = "CREATE TABLE Meter_Reads ( \n\r"
        qry_str = self.fillCreate(qry_str)
        ekm_log(qry_str, 4)
        return qry_str

    def sqlInsert(self, def_buf, raw_a, raw_b):
        """ Reasonably portable SQL INSERT for from combined read buffer.
        Args:
            def_buf (SerialBlock): Database only serial block of all fields.
            raw_a (str): Raw A read as hex string.
            raw_b (str): Raw B read (if exists, otherwise empty) as hex string.

        Returns:
            str: SQL insert for passed read buffer
        """
        count = 0
        qry_str = "INSERT INTO  Meter_Reads ( \n\t"
        for fld in def_buf:
            if count > 0:
                qry_str += ", \n\t"
            qry_str = qry_str + fld
            count += 1
        qry_str += (",\n\t" + Field.Time_Stamp + ", \n\t" +
                    "Raw_A,\n\t" +
                    "Raw_B\n) \n" +
                    "VALUES( \n\t")
        count = 0
        for fld in def_buf:
            if count > 0:
                qry_str += ", \n\t"
            fld_type = def_buf[fld][MeterData.TypeValue]
            fld_str_content = def_buf[fld][MeterData.StringValue]
            delim = ""
            if (fld_type == FieldType.Hex) or \
                    (fld_type == FieldType.String) or \
                    (fld_type == FieldType.PowerFactor):
                delim = "'"
            qry_str = qry_str + delim + fld_str_content + delim
            count += 1
        time_val = int(time.time() * 1000)
        qry_str = (qry_str + ",\n\t" + str(time_val) + ",\n\t'" +
                   binascii.b2a_hex(raw_a) + "'" + ",\n\t'" +
                   binascii.b2a_hex(raw_b) + "'\n);")
        ekm_log(qry_str, 4)
        return qry_str

    def sqlIdxMeterTime(self):
        """ Reasonably portable Meter_Address and Time_Stamp index SQL create.
        Returns:
            str: SQL CREATE INDEX statement.
        """
        return ("CREATE INDEX idx_meter_time " +
                "ON Meter_Reads('" + Field.Meter_Address + "', '" +
                Field.Time_Stamp + "')")

    def sqlIdxMeter(self):
        """ Reasonably portable Meter_Address index SQL create.
        Returns:
            str: SQL CREATE INDEX statement.
        """
        return ("CREATE INDEX idx_meter " +
                "ON Meter_Reads('" + Field.Meter_Address + "')")

    def sqlDrop(self):
        """ Reasonably portable drop of reads table.
        Returns:
            str: SQL DROP TABLE statement.
        """
        qry_str = 'DROP TABLE Meter_Reads'
        return qry_str

    def dbInsert(self, def_buf, raw_a, raw_b):
        """ Call overridden dbExec() with built insert statement.
        Args:
            def_buf (SerialBlock): Block of read buffer fields to write.
            raw_a (str): Hex string of raw A read.
            raw_b (str): Hex string of raw B read or empty.
        """
        self.dbExec(self.sqlInsert(def_buf, raw_a, raw_b))

    def dbCreate(self):
        """ Call overridden dbExec() with built create statement. """
        self.dbExec(self.sqlCreate())

    def dbDropReads(self):
        """ Call overridden dbExec() with build drop statement. """
        self.dbExec(self.sqlDrop())

    def dbExec(self, query_str):
        """ Required override for MeterDB subclass, run a query.
        Args:
            query_str (str): SQL Query to run.
        """
        pass


class SqliteMeterDB(MeterDB):
    """MeterDB subclass for simple sqlite database"""

    def __init__(self, connection_string="default.db"):
        """
        Args:
            connection_string (str): name of sqlite database file.
        """
        super(SqliteMeterDB, self).__init__(connection_string)

    def dbExec(self, query_str):
        """ Required override of dbExec() from MeterDB(), run query.
        Args:
            query_str (str): query to run
        """
        try:
            connection = sqlite3.connect(self.m_connection_string)
            cursor = connection.cursor()
            cursor.execute(query_str)
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))
            return False
        pass

    def dict_factory(self, cursor, row):
        """ Sqlite callback accepting the cursor and the original row as a tuple.

        Simple return of JSON safe types.

        Args:
            cursor (sqlite cursor):  Original cursory
            row (sqlite row tuple): Original row.

        Returns:
            dict: modified row.
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            val = row[idx]
            name = col[0]
            if name == Field.Time_Stamp:
                d[col[0]] = str(val)
                continue
            if name == "Raw_A" or name == "Raw_B":  # or name == Field.Meter_Time:
                continue
            if name not in self.m_all_fields:
                continue
            if (str(val) != "None") and ((val > 0) or (val < 0)):
                d[name] = str(val)
        return d

    def raw_dict_factory(self, cursor, row):
        """ Sqlite callback accepting the cursor and the original row as a tuple.

        Simple return of JSON safe types, including raw read hex strings.

        Args:
            cursor (sqlite cursor):  Original cursory
            row (sqlite row tuple): Original row.

        Returns:
            dict: modified row.
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            val = row[idx]
            name = col[0]
            if name == Field.Time_Stamp or name == Field.Meter_Address:
                d[name] = str(val)
                continue
            if name == "Raw_A" or name == "Raw_B":
                d[name] = str(val)
                continue
        return d

    def renderJsonReadsSince(self, timestamp, meter):
        """ Simple since Time_Stamp query returned as JSON records.

        Args:
            timestamp (int): Epoch time in seconds.
            meter (str): 12 character meter address to query

        Returns:
            str: JSON rendered read records.

        """
        result = ""
        try:
            connection = sqlite3.connect(self.m_connection_string)
            connection.row_factory = self.dict_factory
            select_cursor = connection.cursor()
            select_cursor.execute("select * from Meter_Reads where " + Field.Time_Stamp +
                                  " > " + str(timestamp) + " and " + Field.Meter_Address +
                                  "= '" + meter + "';")
            reads = select_cursor.fetchall()
            result = json.dumps(reads, indent=4)

        except:
            ekm_log(traceback.format_exc(sys.exc_info()))
        return result

    def renderRawJsonReadsSince(self, timestamp, meter):
        """ Simple Time_Stamp query returned as JSON, with raw hex string fields.

        Args:
            timestamp (int): Epoch time in seconds.
            meter (str): 12 character meter address to query

        Returns:
            str: JSON rendered read records including raw hex fields.

        """
        result = ""
        try:
            connection = sqlite3.connect(self.m_connection_string)
            connection.row_factory = self.raw_dict_factory
            select_cursor = connection.cursor()
            select_cursor.execute("select " + Field.Time_Stamp + ", Raw_A, Raw_B, " +
                                  Field.Meter_Address + " from Meter_Reads where " +
                                  Field.Time_Stamp + " > " + str(timestamp) + " and " +
                                  Field.Meter_Address + " = '" + meter + "';")
            reads = select_cursor.fetchall()
            result = json.dumps(reads, indent=4)
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))
        return result


class Meter(object):
    """ Abstract base class.  Encapuslates serial operations and buffers. """

    def __init__(self, meter_address="000000000000"):
        """
        Args:
            meter_address (str): 12 char EKM meter address on front of meter.
        """
        self.m_meter_address = meter_address.zfill(12)
        self.m_raw_read_a = ""
        self.m_raw_read_b = ""
        self.m_observers = []
        self.m_cmd_interface = None
        self.m_serial_port = None
        self.m_command_msg = ""
        self.m_context = ""

        self.m_schd_1_to_4 = SerialBlock()
        self.initSchd_1_to_4()

        self.m_schd_5_to_8 = SerialBlock()
        self.initSchd_5_to_8()

        self.m_hldy = SerialBlock()
        self.initHldyDates()

        self.m_mons = SerialBlock()
        self.initMons()

        self.m_rev_mons = SerialBlock()
        self.initRevMons()

        self.m_seasons_sched_params = {}
        self.m_holiday_date_params = {}
        self.m_sched_tariff_params = {}
        self.initParamLists()

        pass

    def initParamLists(self):
        """ Initialize all short in-object send buffers to zero. """

        self.m_seasons_sched_params = {"Season_1_Start_Month": 0, "Season_1_Start_Day": 0,
                                       "Season_1_Schedule": 0, "Season_2_Start_Month": 0,
                                       "Season_2_Start_Day": 0, "Season_2_Schedule": 0,
                                       "Season_3_Start_Month": 0, "Season_3_Start_Day": 0,
                                       "Season_3_Schedule": 0, "Season_4_Start_Month": 0,
                                       "Season_4_Start_Day": 0, "Season_4_Schedule": 0}

        self.m_holiday_date_params = {"Holiday_1_Month": 0, "Holiday_1_Day": 0, "Holiday_2_Month": 0,
                                      "Holiday_2_Day": 0, "Holiday_3_Month": 0, "Holiday_3_Day": 0,
                                      "Holiday_4_Month": 0, "Holiday_4_Day": 0, "Holiday_5_Month": 0,
                                      "Holiday_5_Day": 0, "Holiday_6_Month": 0, "Holiday_6_Day": 0,
                                      "Holiday_7_Month": 0, "Holiday_7_Day": 0, "Holiday_8_Month": 0,
                                      "Holiday_8_Day": 0, "Holiday_9_Month": 0, "Holiday_9_Day": 0,
                                      "Holiday_10_Month": 0, "Holiday_10_Day": 0, "Holiday_11_Month": 0,
                                      "Holiday_11_Day": 0, "Holiday_12_Month": 0, "Holiday_12_Day": 0,
                                      "Holiday_13_Month": 0, "Holiday_13_Day": 0, "Holiday_14_Month": 0,
                                      "Holiday_14_Day": 0, "Holiday_15_Month": 0, "Holiday_15_Day": 0,
                                      "Holiday_16_Month": 0, "Holiday_16_Day": 0, "Holiday_17_Month": 0,
                                      "Holiday_17_Day": 0, "Holiday_18_Month": 0, "Holiday_18_Day": 0,
                                      "Holiday_19_Month": 0, "Holiday_19_Day": 0, "Holiday_20_Month": 0,
                                      "Holiday_20_Day": 0}

        self.m_sched_tariff_params = {"Schedule": 0, "Hour_1": 0, "Min_1": 0, "Rate_1": 0, "Hour_2": 0,
                                      "Min_2": 0, "Rate_2": 0, "Hour_3": 0, "Min_3": 0, "Rate_3": 0,
                                      "Hour_4": 0, "Min_4": 0, "Rate_4": 0}
        pass

    def getReadBuffer(self):
        """ Required override to fetch the read serial block.

        Returns:
            SerialBlock: Every supported field (A or A+B, includes all fields)
        """
        ekm_log("Meter::getReadBuffer called in superclass.")
        empty  = SerialBlock()
        return empty;

    def request(self, send_terminator=False):
        """ Required override, issue A or A+B reads and square up buffers.

        Args:
            send_terminator (bool): Send termination string at end of read.

        Returns:
            bool: True on successful read.
        """
        ekm_log("Meter::request called in superclass.")
        return False

    def serialPostEnd(self):
        """ Required override, issue termination string to port. """
        ekm_log("Meter::serialPostEnd called in superclass.")
        pass

    def setContext(self, context_str):
        """ Set context string for serial command.  Private setter.

        Args:
            context_str (str): Command specific string.
        """
        if (len(self.m_context) == 0) and (len(context_str) >= 7):
            if context_str[0:7] != "request":
                ekm_log("Context: " + context_str)
        self.m_context = context_str

    def getContext(self):
        """ Get context string for current serial command.  Private getter.

        Returns:
            str: Context string as set at start of command.
        """
        return self.m_context

    def calc_crc16(self, buf):
        """ Drop in pure python replacement for ekmcrc.c extension.

        Args:
            buf (bytes): String or byte array (implicit Python 2.7 cast)

        Returns:
            str: 16 bit CRC per EKM Omnimeters formatted as hex string.
        """
        crc_table = [0x0000, 0xc0c1, 0xc181, 0x0140, 0xc301, 0x03c0, 0x0280, 0xc241,
                     0xc601, 0x06c0, 0x0780, 0xc741, 0x0500, 0xc5c1, 0xc481, 0x0440,
                     0xcc01, 0x0cc0, 0x0d80, 0xcd41, 0x0f00, 0xcfc1, 0xce81, 0x0e40,
                     0x0a00, 0xcac1, 0xcb81, 0x0b40, 0xc901, 0x09c0, 0x0880, 0xc841,
                     0xd801, 0x18c0, 0x1980, 0xd941, 0x1b00, 0xdbc1, 0xda81, 0x1a40,
                     0x1e00, 0xdec1, 0xdf81, 0x1f40, 0xdd01, 0x1dc0, 0x1c80, 0xdc41,
                     0x1400, 0xd4c1, 0xd581, 0x1540, 0xd701, 0x17c0, 0x1680, 0xd641,
                     0xd201, 0x12c0, 0x1380, 0xd341, 0x1100, 0xd1c1, 0xd081, 0x1040,
                     0xf001, 0x30c0, 0x3180, 0xf141, 0x3300, 0xf3c1, 0xf281, 0x3240,
                     0x3600, 0xf6c1, 0xf781, 0x3740, 0xf501, 0x35c0, 0x3480, 0xf441,
                     0x3c00, 0xfcc1, 0xfd81, 0x3d40, 0xff01, 0x3fc0, 0x3e80, 0xfe41,
                     0xfa01, 0x3ac0, 0x3b80, 0xfb41, 0x3900, 0xf9c1, 0xf881, 0x3840,
                     0x2800, 0xe8c1, 0xe981, 0x2940, 0xeb01, 0x2bc0, 0x2a80, 0xea41,
                     0xee01, 0x2ec0, 0x2f80, 0xef41, 0x2d00, 0xedc1, 0xec81, 0x2c40,
                     0xe401, 0x24c0, 0x2580, 0xe541, 0x2700, 0xe7c1, 0xe681, 0x2640,
                     0x2200, 0xe2c1, 0xe381, 0x2340, 0xe101, 0x21c0, 0x2080, 0xe041,
                     0xa001, 0x60c0, 0x6180, 0xa141, 0x6300, 0xa3c1, 0xa281, 0x6240,
                     0x6600, 0xa6c1, 0xa781, 0x6740, 0xa501, 0x65c0, 0x6480, 0xa441,
                     0x6c00, 0xacc1, 0xad81, 0x6d40, 0xaf01, 0x6fc0, 0x6e80, 0xae41,
                     0xaa01, 0x6ac0, 0x6b80, 0xab41, 0x6900, 0xa9c1, 0xa881, 0x6840,
                     0x7800, 0xb8c1, 0xb981, 0x7940, 0xbb01, 0x7bc0, 0x7a80, 0xba41,
                     0xbe01, 0x7ec0, 0x7f80, 0xbf41, 0x7d00, 0xbdc1, 0xbc81, 0x7c40,
                     0xb401, 0x74c0, 0x7580, 0xb541, 0x7700, 0xb7c1, 0xb681, 0x7640,
                     0x7200, 0xb2c1, 0xb381, 0x7340, 0xb101, 0x71c0, 0x7080, 0xb041,
                     0x5000, 0x90c1, 0x9181, 0x5140, 0x9301, 0x53c0, 0x5280, 0x9241,
                     0x9601, 0x56c0, 0x5780, 0x9741, 0x5500, 0x95c1, 0x9481, 0x5440,
                     0x9c01, 0x5cc0, 0x5d80, 0x9d41, 0x5f00, 0x9fc1, 0x9e81, 0x5e40,
                     0x5a00, 0x9ac1, 0x9b81, 0x5b40, 0x9901, 0x59c0, 0x5880, 0x9841,
                     0x8801, 0x48c0, 0x4980, 0x8941, 0x4b00, 0x8bc1, 0x8a81, 0x4a40,
                     0x4e00, 0x8ec1, 0x8f81, 0x4f40, 0x8d01, 0x4dc0, 0x4c80, 0x8c41,
                     0x4400, 0x84c1, 0x8581, 0x4540, 0x8701, 0x47c0, 0x4680, 0x8641,
                     0x8201, 0x42c0, 0x4380, 0x8341, 0x4100, 0x81c1, 0x8081, 0x4040]

        crc = 0xffff
        for c in buf:
            index = (crc ^ ord(c)) & 0xff
            crct = crc_table[index]
            crc = (crc >> 8) ^ crct
        crc = (crc << 8) | (crc >> 8)
        crc &= 0x7F7F

        return "%04x" % crc

    def calcPF(self, pf):
        """ Simple wrap to calc legacy PF value

        Args:
            pf: meter power factor reading

        Returns:
            int: legacy push pf
        """
        pf_y = pf[:1]
        pf_x = pf[1:]
        result = 100
        if pf_y == CosTheta.CapacitiveLead:
            result = 200 - int(pf_x)
        elif pf_y == CosTheta.InductiveLag:
            result = int(pf_x)

        return result

    def setMaxDemandPeriod(self, period, password="00000000"):
        """ Serial call to set max demand period.

        Args:
            period (int): : as int.
            password (str): Optional password.

        Returns:
            bool: True on completion with ACK.
        """
        result = False
        self.setContext("setMaxDemandPeriod")
        try:
            if period < 1 or period > 3:
                self.writeCmdMsg("Correct parameter: 1 = 15 minute, 2 = 30 minute, 3 = hour")
                self.setContext("")
                return result

            if not self.request(False):
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_str = "015731023030353028" + binascii.hexlify(str(period)).zfill(2) + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success(setMaxDemandPeriod): 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def setMaxDemandResetInterval(self, interval, password="00000000"):
        """ Serial call to set max demand interval.

        Args:
            interval (int): :class:`~ekmmeters.MaxDemandResetInterval` as int.
            password (str): Optional password.

        Returns:
            bool: True on completion with ACK.
        """
        result = False
        self.setContext("setMaxDemandResetInterval")
        try:
            if interval < 0 or interval > 4:
                self.writeCmdMsg("Correct parameter: 0 = off, 1 = monthly, 2 = weekly, 3 = daily, 4 = hourly")
                self.setContext("")
                return result

            if not self.request(False):
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_str = "015731023030443528" + binascii.hexlify(str(interval).zfill(1)) + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success (setMaxDemandResetInterval): 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def setMeterPassword(self, new_pwd, pwd="00000000"):
        """ Serial Call to set meter password.  USE WITH CAUTION.

        Args:
            new_pwd (str): 8 digit numeric password to set
            pwd (str): Old 8 digit numeric password.

        Returns:
            bool: True on completion with ACK.
        """
        result = False
        self.setContext("setMeterPassword")
        try:
            if len(new_pwd) != 8 or len(pwd) != 8:
                self.writeCmdMsg("Passwords must be exactly eight characters.")
                self.setContext("")
                return result

            if not self.request(False):
                self.writeCmdMsg("Pre command read failed: check serial line.")
            else:
                if not self.serialCmdPwdAuth(pwd):
                    self.writeCmdMsg("Password failure")
                else:
                    req_pwd = binascii.hexlify(new_pwd.zfill(8))
                    req_str = "015731023030323028" + req_pwd + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success(setMeterPassword): 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def unpackStruct(self, data, def_buf):
        """ Wrapper for struct.unpack with SerialBlock buffer definitionns.

        Args:
            data (str): Implicit cast bytes to str, serial port return.
            def_buf (SerialBlock): Block object holding field lengths.

        Returns:
            tuple: parsed result of struct.unpack() with field definitions.
        """
        struct_str = "="
        for fld in def_buf:
            if not def_buf[fld][MeterData.CalculatedFlag]:
                struct_str = struct_str + str(def_buf[fld][MeterData.SizeValue]) + "s"
        if len(data) == 255:
            contents = struct.unpack(struct_str, str(data))
        else:
            self.writeCmdMsg("Length error.  Len() size = " + str(len(data)))
            contents = ()
        return contents



    def convertData(self, contents, def_buf, kwh_scale=ScaleKWH.EmptyScale):
        """ Move data from raw tuple into scaled and conveted values.

        Args:
            contents (tuple): Breakout of passed block from unpackStruct().
            def_buf (): Read buffer destination.
            kwh_scale (int):  :class:`~ekmmeters.ScaleKWH` as int, from Field.kWhScale`

        Returns:
            bool: True on completion.
        """
        log_str = ""
        count = 0
        
        # getting scale does not require a full read.  It does require that the
        # reads have the scale value in the first block read.  This requirement
        # is filled by default in V3 and V4 requests
        if kwh_scale == ScaleKWH.EmptyScale:
            if self.m_kwh_precision == ScaleKWH.EmptyScale :
                scale_offset = int(def_buf.keys().index(Field.kWh_Scale))
                self.m_kwh_precision = kwh_scale = int(contents[scale_offset])

        for fld in def_buf:

            if def_buf[fld][MeterData.CalculatedFlag]:
                count += 1
                continue

            if len(contents) == 0:
                count += 1
                continue

            try:  # scrub up messes on a field by field basis
                raw_data = contents[count]
                fld_type = def_buf[fld][MeterData.TypeValue]
                fld_scale = def_buf[fld][MeterData.ScaleValue]

                if fld_type == FieldType.Float:
                    float_data = float(str(raw_data))
                    divisor = 1
                    if fld_scale == ScaleType.KWH:
                        divisor = 1
                        if kwh_scale == ScaleKWH.Scale10:
                            divisor = 10
                        elif kwh_scale == ScaleKWH.Scale100:
                            divisor = 100
                        elif (kwh_scale != ScaleKWH.NoScale) and (kwh_scale != ScaleKWH.EmptyScale):
                            ekm_log("Unrecognized kwh scale.")
                    elif fld_scale == ScaleType.Div10:
                        divisor = 10
                    elif fld_scale == ScaleType.Div100:
                        divisor = 100
                    elif fld_scale != ScaleType.No:
                        ekm_log("Unrecognized float scale.")
                    float_data /= divisor
                    float_data_str = str(float_data)
                    def_buf[fld][MeterData.StringValue] = float_data_str
                    def_buf[fld][MeterData.NativeValue] = float_data

                elif fld_type == FieldType.Hex:
                    hex_data = raw_data.encode('hex')
                    def_buf[fld][MeterData.StringValue] = hex_data
                    def_buf[fld][MeterData.NativeValue] = hex_data

                elif fld_type == FieldType.Int:
                    integer_data = int(raw_data)
                    integer_data_str = str(integer_data)
                    if len(integer_data_str) == 0:
                        integer_data_str = str(0)
                    def_buf[fld][MeterData.StringValue] = integer_data_str
                    def_buf[fld][MeterData.NativeValue] = integer_data

                elif fld_type == FieldType.String:
                    string_data = str(raw_data)
                    def_buf[fld][MeterData.StringValue] = string_data
                    def_buf[fld][MeterData.NativeValue] = string_data

                elif fld_type == FieldType.PowerFactor:
                    def_buf[fld][MeterData.StringValue] = str(raw_data)
                    def_buf[fld][MeterData.NativeValue] = str(raw_data)

                else:
                    ekm_log("Unrecognized field type")

                log_str = log_str + '"' + fld + '":  "' + def_buf[fld][MeterData.StringValue] + '"\n'

            except:
                ekm_log("Exception on Field:" + str(fld))
                ekm_log(traceback.format_exc(sys.exc_info()))
                self.writeCmdMsg("Exception on Field:" + str(fld))

            count += 1

        return True

    def jsonRender(self, def_buf):
        """ Translate the passed serial block into string only JSON.

        Args:
            def_buf (SerialBlock): Any :class:`~ekmmeters.SerialBlock` object.

        Returns:
            str: JSON rendering of meter record.
        """
        try:
            ret_dict = SerialBlock()
            ret_dict[Field.Meter_Address] = self.getMeterAddress()
            for fld in def_buf:
                compare_fld = fld.upper()
                if not "RESERVED" in compare_fld and not "CRC" in compare_fld:
                    ret_dict[str(fld)] = def_buf[fld][MeterData.StringValue]
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))
            return ""
        return json.dumps(ret_dict, indent=4)

    def crcMeterRead(self, raw_read, def_buf):
        """ Internal read CRC wrapper.

        Args:
            raw_read (str): Bytes with implicit string cast from serial read
            def_buf (SerialBlock): Populated read buffer.

        Returns:
            bool:  True if passed CRC equals calculated CRC.
        """
        try:
            if len(raw_read) == 0:
                ekm_log("(" + self.m_context + ") Empty return read.")
                return False
            sent_crc = self.calc_crc16(raw_read[1:-2])
            logstr = "(" + self.m_context + ")CRC sent = " + str(def_buf["crc16"][MeterData.StringValue])
            logstr += " CRC calc = " + sent_crc
            ekm_log(logstr)
            if int(def_buf["crc16"][MeterData.StringValue], 16) == int(sent_crc, 16):
                return True

        # A cross simple test lines on a USB serial adapter, these occur every
        # 1000 to 2000 reads, and they show up here as a bad unpack or
        # a bad crc type call.  In either case, we suppress them a log will
        # become quite large.  ekmcrc errors come through as type errors.
        # Failures of int type conversion in 16 bit conversion occur as value
        # errors.
        except struct.error:
            ekm_log(str(sys.exc_info()))
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname, lineno, fn, text = frame
                ekm_log("Error in %s on line %d" % (fname, lineno))
            return False

        except TypeError:
            ekm_log(str(sys.exc_info()))
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname, lineno, fn, text = frame
                ekm_log("Error in %s on line %d" % (fname, lineno))
            return False

        except ValueError:
            ekm_log(str(sys.exc_info()))
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname, lineno, fn, text = frame
                ekm_log("Error in %s on line %d" % (fname, lineno))
            return False

        return False

    def splitEkmDate(self, dateint):
        """Break out a date from Omnimeter read.

        Note a corrupt date will raise an exception when you
        convert it to int to hand to this method.

        Args:
            dateint (int):  Omnimeter datetime as int.

        Returns:
            tuple: Named tuple which breaks out as followws:

            ========== =====================
            yy         Last 2 digits of year
            mm         Month 1-12
            dd         Day 1-31
            weekday    Zero based weekday
            hh         Hour 0-23
            minutes    Minutes 0-59
            ss         Seconds 0-59
            ========== =====================

        """
        date_str = str(dateint)
        dt = namedtuple('EkmDate', ['yy', 'mm', 'dd', 'weekday', 'hh', 'minutes', 'ss'])

        if len(date_str) != 14:
            dt.yy = dt.mm = dt.dd = dt.weekday = dt.hh = dt.minutes = dt.ss = 0
            return dt

        dt.yy = int(date_str[0:2])
        dt.mm = int(date_str[2:4])
        dt.dd = int(date_str[4:6])
        dt.weekday = int(date_str[6:8])
        dt.hh = int(date_str[8:10])
        dt.minutes = int(date_str[10:12])
        dt.ss = int(date_str[12:14])
        return dt

    def getMeterAddress(self):
        """ Getter for meter object 12 character address.

        Returns:
            str: 12 character address on front of meter
        """
        return self.m_meter_address

    def registerObserver(self, observer):
        """ Place an observer in the meter update() chain.

        Args:
            observer (MeterObserver): Subclassed MeterObserver.
        """
        self.m_observers.append(observer)
        pass

    def unregisterObserver(self, observer):
        """ Remove an observer from the meter update() chain.

        Args:
            observer (MeterObserver): Subclassed MeterObserver.
        """
        if observer in self.m_observers:
            self.m_observers.remove(observer)
        pass

    def initSchd_1_to_4(self):
        """ Initialize first tariff schedule :class:`~ekmmeters.SerialBlock`. """
        self.m_schd_1_to_4["reserved_40"] = [6, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_schd_1_to_4["Schd_1_Tariff_1_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_1_Tariff_1_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_1_Tariff_1_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_1_Tariff_2_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_1_Tariff_2_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_1_Tariff_2_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_1_Tariff_3_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_1_Tariff_3_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_1_Tariff_3_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_1_Tariff_4_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_1_Tariff_4_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_1_Tariff_4_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["reserved_41"] = [24, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_1_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_1_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_1_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_2_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_2_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_2_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_3_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_3_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_3_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_4_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_4_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_2_Tariff_4_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["reserved_42"] = [24, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_1_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_1_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_1_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_2_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_2_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_2_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_3_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_3_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_3_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_4_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_4_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_3_Tariff_4_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["reserved_43"] = [24, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_1_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_1_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_1_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_2_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_2_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_2_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_3_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_3_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_3_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_4_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_4_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["Schd_4_Tariff_4_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["reserved_44"] = [79, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_schd_1_to_4["crc16"] = [2, FieldType.Hex, ScaleType.No, "", 0, False, False]
        pass

    def initSchd_5_to_8(self):
        """ Initialize second(and last) tariff schedule :class:`~ekmmeters.SerialBlock`. """
        self.m_schd_5_to_8["reserved_30"] = [6, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_schd_5_to_8["Schd_5_Tariff_1_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_5_Tariff_1_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_5_Tariff_1_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_5_Tariff_2_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_5_Tariff_2_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_5_Tariff_2_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_5_Tariff_3_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_5_Tariff_3_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_5_Tariff_3_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_5_Tariff_4_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_5_Tariff_4_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_5_Tariff_4_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["reserved_31"] = [24, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_1_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_1_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_1_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_2_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_2_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_2_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_3_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_3_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_3_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_4_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_4_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_6_Tariff_4_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["reserved_32"] = [24, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_1_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_1_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_1_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_2_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_2_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_2_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_3_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_3_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_3_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_4_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_4_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_7_Tariff_4_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["reserved_33"] = [24, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_1_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_1_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_1_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_2_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_2_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_2_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_3_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_3_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_3_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_4_Hour"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_4_Min"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["Schd_8_Tariff_4_Rate"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["reserved_34"] = [79, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_schd_5_to_8["crc16"] = [2, FieldType.Hex, ScaleType.No, "", 0, False, False]
        pass

    def getSchedulesBuffer(self, period_group):
        """ Return the requested tariff schedule :class:`~ekmmeters.SerialBlock` for meter.

        Args:
            period_group (int):  A :class:`~ekmmeters.ReadSchedules` value.

        Returns:
            SerialBlock: The requested tariff schedules for meter.
        """
        empty_return = SerialBlock()
        if period_group == ReadSchedules.Schedules_1_To_4:
            return self.m_schd_1_to_4
        elif period_group == ReadSchedules.Schedules_5_To_8:
            return self.m_schd_5_to_8
        else:
            return empty_return

    def initHldyDates(self):
        """ Initialize holidays :class:`~ekmmeters.SerialBlock` """
        self.m_hldy["reserved_20"] = [6, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_hldy["Holiday_1_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_1_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_2_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_2_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_3_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_3_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_4_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_4_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_5_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_5_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_6_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_6_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_7_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_7_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_8_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_8_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_9_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_9_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_10_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_10_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_11_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_11_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_12_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_12_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_13_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_13_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_14_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_14_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_15_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_15_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_16_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_16_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_17_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_17_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_18_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_18_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_19_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_19_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_20_Mon"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_20_Day"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Weekend_Schd"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["Holiday_Schd"] = [2, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_hldy["reserved_21"] = [163, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_hldy["crc16"] = [2, FieldType.Hex, ScaleType.No, "", 0, False, False]
        pass

    def getHolidayDatesBuffer(self):
        """ Get the meter :class:`~ekmmeters.SerialBlock` for holiday dates."""
        return self.m_hldy

    def initMons(self):
        """ Initialize first month tariff :class:`~ekmmeters.SerialBlock` for meter """
        self.m_mons["reserved_echo_cmd"] = [6, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_mons["Month_1_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_1_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_1_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_1_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_1_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_2_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_2_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_2_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_2_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_2_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_3_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_3_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_3_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_3_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_3_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_4_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_4_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_4_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_4_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_4_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_5_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_5_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_5_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_5_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_5_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_6_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_6_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_6_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_6_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["Month_6_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_mons["reserved_1"] = [7, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_mons["crc16"] = [2, FieldType.Hex, ScaleType.No, "", 0, False, False]
        pass

    def initRevMons(self):
        """ Initialize second (and last) month tarifff :class:`~ekmmeters.SerialBlock` for meter. """
        self.m_rev_mons["reserved_echo_cmd"] = [6, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_rev_mons["Month_1_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_1_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_1_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_1_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_1_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_2_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_2_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_2_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_2_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_2_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_3_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_3_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_3_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_3_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_3_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_4_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_4_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_4_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_4_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_4_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_5_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_5_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_5_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_5_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_5_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_6_Tot"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_6_Tariff_1"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_6_Tariff_2"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_6_Tariff_3"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["Month_6_Tariff_4"] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_rev_mons["reserved_1"] = [7, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_rev_mons["crc16"] = [2, FieldType.Hex, ScaleType.No, "", 0, False, False]
        pass

    def getMonthsBuffer(self, direction):
        """ Get the months tariff SerialBlock for meter.

        Args:
            direction (int): A :class:`~ekmmeters.ReadMonths` value.

        Returns:
            SerialBlock: Requested months tariffs buffer.

        """
        if direction == ReadMonths.kWhReverse:
            return self.m_rev_mons

        # default direction == ReadMonths.kWh
        return self.m_mons

    def setMaxDemandResetNow(self, password="00000000"):
        """ Serial call zero max demand (Dash Now button)

        Args:
            password (str): Optional password

        Returns:
            bool: True on completion with ACK.
        """
        result = False
        self.setContext("setMaxDemandResetNow")
        try:
            if len(password) != 8:
                self.writeCmdMsg("Invalid password length.")
                self.setContext("")
                return result

            if not self.request(False):
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_str = "015731023030343028" + binascii.hexlify(str(0).zfill(6)) + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success(setMaxDemandResetNow): 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def setTime(self, yy, mm, dd, hh, minutes, ss, password="00000000"):
        """ Serial set time with day of week calculation.

        Args:
            yy (int): Last two digits of year.
            mm (int): Month 1-12.
            dd (int): Day 1-31
            hh (int): Hour 0 to 23.
            minutes (int): Minutes 0 to 59.
            ss (int): Seconds 0 to 59.
            password (str): Optional password.

        Returns:
            bool: True on completion and ACK.
        """
        result = False
        self.setContext("setTime")
        try:
            if mm < 1 or mm > 12:
                self.writeCmdMsg("Month must be between 1 and 12")
                self.setContext("")
                return result

            if dd < 1 or dd > 31:
                self.writeCmdMsg("Day must be between 1 and 31")
                self.setContext("")
                return result

            if hh < 0 or hh > 23:
                self.writeCmdMsg("Hour must be between 0 and 23, inclusive")
                self.setContext("")
                return result

            if minutes < 0 or minutes > 59:
                self.writeCmdMsg("Minutes must be between 0 and 59, inclusive")
                self.setContext("")
                return result

            if ss < 0 or ss > 59:
                self.writeCmdMsg("Seconds must be between 0 and 59, inclusive")
                self.setContext("")
                return result

            if len(password) != 8:
                self.writeCmdMsg("Invalid password length.")
                self.setContext("")
                return result

            if not self.request(False):
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    dt_buf = datetime.datetime(int(yy), int(mm), int(dd), int(hh), int(minutes), int(ss))
                    ekm_log("Writing Date and Time " + dt_buf.strftime("%Y-%m-%d %H:%M"))
                    dayofweek = dt_buf.date().isoweekday()
                    ekm_log("Calculated weekday " + str(dayofweek))

                    req_str = "015731023030363028"
                    req_str += binascii.hexlify(str(yy)[-2:])
                    req_str += binascii.hexlify(str(mm).zfill(2))
                    req_str += binascii.hexlify(str(dd).zfill(2))
                    req_str += binascii.hexlify(str(dayofweek).zfill(2))
                    req_str += binascii.hexlify(str(hh).zfill(2))
                    req_str += binascii.hexlify(str(minutes).zfill(2))
                    req_str += binascii.hexlify(str(ss).zfill(2))
                    req_str += "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success(setTime): 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def setCTRatio(self, new_ct, password="00000000"):
        """ Serial call to set CT ratio for attached inductive pickup.

        Args:
            new_ct (int): A :class:`~ekmmeters.CTRatio` value, a legal amperage setting.
            password (str): Optional password.

        Returns:
            bool: True on completion with ACK.
        """
        ret = False
        self.setContext("setCTRatio")
        try:
            self.clearCmdMsg()
            if ((new_ct != CTRatio.Amps_100) and (new_ct != CTRatio.Amps_200) and
                    (new_ct != CTRatio.Amps_400) and (new_ct != CTRatio.Amps_600) and
                    (new_ct != CTRatio.Amps_800) and (new_ct != CTRatio.Amps_1000) and
                    (new_ct != CTRatio.Amps_1200) and (new_ct != CTRatio.Amps_1500) and
                    (new_ct != CTRatio.Amps_2000) and (new_ct != CTRatio.Amps_3000) and
                    (new_ct != CTRatio.Amps_4000) and (new_ct != CTRatio.Amps_5000)):
                self.writeCmdMsg("Legal CT Ratios: 100, 200, 400, 600, " +
                                 "800, 1000, 1200, 1500, 2000, 3000, 4000 and 5000")
                self.setContext("")
                return ret

            if len(password) != 8:
                self.writeCmdMsg("Invalid password length.")
                self.setContext("")
                return ret

            if not self.request(False):
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_str = "015731023030443028" + binascii.hexlify(str(new_ct).zfill(4)) + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success(setCTRatio): 06 returned.")
                        ret = True
            self.serialPostEnd()

        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return ret

    def assignScheduleTariff(self, schedule, tariff, hour, minute, rate):
        """ Assign one schedule tariff period to meter bufffer.

        Args:
            schedule (int): A :class:`~ekmmeters.Schedules` value or in range(Extents.Schedules).
            tariff (int): :class:`~ekmmeters.Tariffs` value or in range(Extents.Tariffs).
            hour (int): Hour from 0-23.
            minute (int): Minute from 0-59.
            rate (int): Rate value.

        Returns:
            bool: True on completed assignment.
        """
        if ((schedule not in range(Extents.Schedules)) or
                (tariff not in range(Extents.Tariffs)) or
                (hour < 0) or (hour > 23) or (minute < 0) or
                (minute > 59) or (rate < 0)):
            ekm_log("Out of bounds in Schedule_" + str(schedule + 1))
            return False

        tariff += 1
        idx_min = "Min_" + str(tariff)
        idx_hour = "Hour_" + str(tariff)
        idx_rate = "Rate_" + str(tariff)
        if idx_min not in self.m_sched_tariff_params:
            ekm_log("Incorrect index: " + idx_min)
            return False
        if idx_hour not in self.m_sched_tariff_params:
            ekm_log("Incorrect index: " + idx_hour)
            return False
        if idx_rate not in self.m_sched_tariff_params:
            ekm_log("Incorrect index: " + idx_rate)
            return False

        self.m_sched_tariff_params[idx_rate] = rate
        self.m_sched_tariff_params[idx_hour] = hour
        self.m_sched_tariff_params[idx_min] = minute
        self.m_sched_tariff_params['Schedule'] = schedule
        return True

    def setScheduleTariffs(self, cmd_dict=None, password="00000000"):
        """ Serial call to set tariff periodds for a schedule.

        Args:
            cmd_dict (dict): Optional passed command dictionary.
            password (str): Optional password.

        Returns:
            bool: True on completion and ACK.
        """
        result = False
        self.setContext("setScheduleTariffs")

        if not cmd_dict:
            cmd_dict = self.m_sched_tariff_params

        try:
            if not self.request(False):
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_table = ""
                    req_table += binascii.hexlify(str(cmd_dict["Hour_1"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Min_1"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Rate_1"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Hour_2"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Min_2"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Rate_2"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Hour_3"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Min_3"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Rate_3"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Hour_4"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Min_4"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Rate_4"]).zfill(2))
                    req_table += binascii.hexlify(str(0).zfill(24))

                    table = binascii.hexlify(str(cmd_dict["Schedule"]).zfill(1))

                    req_str = "01573102303037" + table + "28" + req_table + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success(setScheduleTariffs): 06 returned.")
                        result = True

            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def assignSeasonSchedule(self, season, month, day, schedule):
        """ Define a single season and assign a schedule

        Args:
            season (int): A :class:`~ekmmeters.Seasons` value or in range(Extent.Seasons).
            month (int): Month 1-12.
            day (int):  Day 1-31.
            schedule (int): A :class:`~ekmmeters.LCDItems` value or in range(Extent.Schedules).

        Returns:
            bool: True on completion and ACK.
        """
        season += 1
        schedule += 1
        if ((season < 1) or (season > Extents.Seasons) or (schedule < 1) or
                (schedule > Extents.Schedules) or (month > 12) or (month < 0) or
                (day < 0) or (day > 31)):
            ekm_log("Out of bounds: month " + str(month) + " day " + str(day) +
                    " schedule " + str(schedule) + " season " + str(season))
            return False

        idx_mon = "Season_" + str(season) + "_Start_Day"
        idx_day = "Season_" + str(season) + "_Start_Month"
        idx_schedule = "Season_" + str(season) + "_Schedule"
        if idx_mon not in self.m_seasons_sched_params:
            ekm_log("Incorrect index: " + idx_mon)
            return False
        if idx_day not in self.m_seasons_sched_params:
            ekm_log("Incorrect index: " + idx_day)
            return False
        if idx_schedule not in self.m_seasons_sched_params:
            ekm_log("Incorrect index: " + idx_schedule)
            return False

        self.m_seasons_sched_params[idx_mon] = month
        self.m_seasons_sched_params[idx_day] = day
        self.m_seasons_sched_params[idx_schedule] = schedule
        return True

    def setSeasonSchedules(self, cmd_dict=None, password="00000000"):
        """ Serial command to set seasons table.

        If no dictionary is passed, the meter object buffer is used.

        Args:
            cmd_dict (dict): Optional dictionary of season schedules.
            password (str): Optional password

        Returns:
            bool: True on completion and ACK.
        """
        result = False
        self.setContext("setSeasonSchedules")

        if not cmd_dict:
            cmd_dict = self.m_seasons_sched_params

        try:
            if not self.request(False):
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_table = ""
                    req_table += binascii.hexlify(str(cmd_dict["Season_1_Start_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Season_1_Start_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Season_1_Schedule"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Season_2_Start_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Season_2_Start_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Season_2_Schedule"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Season_3_Start_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Season_3_Start_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Season_3_Schedule"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Season_4_Start_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Season_4_Start_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Season_4_Schedule"]).zfill(2))
                    req_table += binascii.hexlify(str(0).zfill(24))
                    req_str = "015731023030383028" + req_table + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success(setSeasonSchedules): 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def assignHolidayDate(self, holiday, month, day):
        """ Set a singe holiday day and month in object buffer.

        There is no class style enum for holidays.

        Args:
            holiday (int): 0-19 or range(Extents.Holidays).
            month (int): Month 1-12.
            day (int): Day 1-31

        Returns:
            bool: True on completion.
        """
        holiday += 1
        if (month > 12) or (month < 0) or (day > 31) or (day < 0) or (holiday < 1) or (holiday > Extents.Holidays):
            ekm_log("Out of bounds: month " + str(month) + " day " + str(day) + " holiday " + str(holiday))
            return False

        day_str = "Holiday_" + str(holiday) + "_Day"
        mon_str = "Holiday_" + str(holiday) + "_Month"
        if day_str not in self.m_holiday_date_params:
            ekm_log("Incorrect index: " + day_str)
            return False
        if mon_str not in self.m_holiday_date_params:
            ekm_log("Incorrect index: " + mon_str)
            return False
        self.m_holiday_date_params[day_str] = day
        self.m_holiday_date_params[mon_str] = month
        return True

    def setHolidayDates(self, cmd_dict=None, password="00000000"):
        """ Serial call to set holiday list.

        If a buffer dictionary is not supplied, the method will use
        the class object buffer populated with assignHolidayDate.

        Args:
            cmd_dict (dict): Optional dictionary of holidays.
            password (str): Optional password.

        Returns:
            bool: True on completion.
        """
        result = False
        self.setContext("setHolidayDates")
        if not cmd_dict:
            cmd_dict = self.m_holiday_date_params

        try:
            if not self.request(False):
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_table = ""
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_1_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_1_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_2_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_2_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_3_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_3_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_4_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_4_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_5_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_5_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_6_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_6_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_7_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_7_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_8_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_8_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_9_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_9_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_10_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_10_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_11_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_11_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_12_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_12_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_13_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_13_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_14_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_14_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_15_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_15_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_16_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_16_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_17_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_17_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_18_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_18_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_19_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_19_Day"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_20_Month"]).zfill(2))
                    req_table += binascii.hexlify(str(cmd_dict["Holiday_20_Day"]).zfill(2))
                    req_str = "015731023030423028" + req_table + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success(setHolidayDates: 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def setWeekendHolidaySchedules(self, new_wknd, new_hldy, password="00000000"):
        """ Serial call to set weekend and holiday :class:`~ekmmeters.Schedules`.

        Args:
            new_wknd (int): :class:`~ekmmeters.Schedules` value to assign.
            new_hldy (int): :class:`~ekmmeters.Schedules` value to assign.
            password (str): Optional password..

        Returns:
            bool: True on completion and ACK.
        """
        result = False
        self.setContext("setWeekendHolidaySchedules")
        try:
            if not self.request(False):
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_wkd = binascii.hexlify(str(new_wknd).zfill(2))
                    req_hldy = binascii.hexlify(str(new_hldy).zfill(2))
                    req_str = "015731023030433028" + req_wkd + req_hldy + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success(setWeekendHolidaySchedules): 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def readScheduleTariffs(self, tableset):
        """ Serial call to read schedule tariffs buffer

        Args:
            tableset (int): :class:`~ekmmeters.ReadSchedules` buffer to return.

        Returns:
            bool: True on completion and ACK.
        """
        self.setContext("readScheduleTariffs")
        try:
            req_table = binascii.hexlify(str(tableset).zfill(1))
            req_str = "01523102303037" + req_table + "282903"

            self.request(False)
            req_crc = self.calc_crc16(req_str[2:].decode("hex"))
            req_str += req_crc
            self.m_serial_port.write(req_str.decode("hex"))
            raw_ret = self.m_serial_port.getResponse(self.getContext())
            self.serialPostEnd()
            return_crc = self.calc_crc16(raw_ret[1:-2])

            if tableset == ReadSchedules.Schedules_1_To_4:
                unpacked_read = self.unpackStruct(raw_ret, self.m_schd_1_to_4)
                self.convertData(unpacked_read, self.m_schd_1_to_4, self.m_kwh_precision)
                if str(return_crc) == str(self.m_schd_1_to_4["crc16"][MeterData.StringValue]):
                    ekm_log("Schedules 1 to 4 CRC success (06 return")
                    self.setContext("")
                    return True

            elif tableset == ReadSchedules.Schedules_5_To_8:
                unpacked_read = self.unpackStruct(raw_ret, self.m_schd_5_to_8)
                self.convertData(unpacked_read, self.m_schd_5_to_8, self.m_kwh_precision)
                if str(return_crc) == str(self.m_schd_5_to_8["crc16"][MeterData.StringValue]):
                    ekm_log("Schedules 5 to 8 CRC success (06 return)")
                    self.setContext("")
                    return True
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return False

    def extractScheduleTariff(self, schedule, tariff):
        """ Read a single schedule tariff from meter object buffer.

        Args:
            schedule (int): A :class:`~ekmmeters.Schedules` value or in range(Extent.Schedules).
            tariff (int): A :class:`~ekmmeters.Tariffs` value or in range(Extent.Tariffs).

        Returns:
            bool: True on completion.
        """
        ret = namedtuple("ret", ["Hour", "Min", "Rate", "Tariff", "Schedule"])
        work_table = self.m_schd_1_to_4
        if Schedules.Schedule_5 <= schedule <= Schedules.Schedule_8:
            work_table = self.m_schd_5_to_8
        tariff += 1
        schedule += 1
        ret.Tariff = str(tariff)
        ret.Schedule = str(schedule)
        if (schedule < 1) or (schedule > Extents.Schedules) or (tariff < 0) or (tariff > Extents.Tariffs):
            ekm_log("Out of bounds: tariff " + str(tariff) + " for schedule " + str(schedule))
            ret.Hour = ret.Min = ret.Rate = str(0)
            return ret

        idxhr = "Schd_" + str(schedule) + "_Tariff_" + str(tariff) + "_Hour"
        idxmin = "Schd_" + str(schedule) + "_Tariff_" + str(tariff) + "_Min"
        idxrate = "Schd_" + str(schedule) + "_Tariff_" + str(tariff) + "_Rate"

        if idxhr not in work_table:
            ekm_log("Incorrect index: " + idxhr)
            ret.Hour = ret.Min = ret.Rate = str(0)
            return ret

        if idxmin not in work_table:
            ekm_log("Incorrect index: " + idxmin)
            ret.Hour = ret.Min = ret.Rate = str(0)
            return ret

        if idxrate not in work_table:
            ekm_log("Incorrect index: " + idxrate)
            ret.Hour = ret.Min = ret.Rate = str(0)
            return ret

        ret.Hour = work_table[idxhr][MeterData.StringValue]
        ret.Min = work_table[idxmin][MeterData.StringValue].zfill(2)
        ret.Rate = work_table[idxrate][MeterData.StringValue]
        return ret

    def readMonthTariffs(self, months_type):
        """ Serial call to read month tariffs block into meter object buffer.

        Args:
            months_type (int): A :class:`~ekmmeters.ReadMonths` value.

        Returns:
            bool: True on completion.
        """
        self.setContext("readMonthTariffs")
        try:

            req_type = binascii.hexlify(str(months_type).zfill(1))
            req_str = "01523102303031" + req_type + "282903"
            work_table = self.m_mons
            if months_type == ReadMonths.kWhReverse:
                work_table = self.m_rev_mons

            self.request(False)
            req_crc = self.calc_crc16(req_str[2:].decode("hex"))
            req_str += req_crc
            self.m_serial_port.write(req_str.decode("hex"))
            raw_ret = self.m_serial_port.getResponse(self.getContext())
            self.serialPostEnd()
            unpacked_read = self.unpackStruct(raw_ret, work_table)
            self.convertData(unpacked_read, work_table, self.m_kwh_precision)
            return_crc = self.calc_crc16(raw_ret[1:-2])
            if str(return_crc) == str(work_table["crc16"][MeterData.StringValue]):
                ekm_log("Months CRC success, type = " + str(req_type))
                self.setContext("")
                return True
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return False

    def extractMonthTariff(self, month):
        """ Extract the tariff for a single month from the meter object buffer.

        Args:
            month (int):  A :class:`~ekmmeters.Months` value or range(Extents.Months).

        Returns:
            tuple: The eight tariff period totals for month. The return tuple breaks out as follows:

            ================= ======================================
            kWh_Tariff_1      kWh for tariff period 1 over month.
            kWh_Tariff_2      kWh for tariff period 2 over month
            kWh_Tariff_3      kWh for tariff period 3 over month
            kWh_Tariff_4      kWh for tariff period 4 over month
            kWh_Tot           Total kWh over requested month
            Rev_kWh_Tariff_1  Rev kWh for tariff period 1 over month
            Rev_kWh_Tariff_3  Rev kWh for tariff period 2 over month
            Rev_kWh_Tariff_3  Rev kWh for tariff period 3 over month
            Rev_kWh_Tariff_4  Rev kWh for tariff period 4 over month
            Rev_kWh_Tot       Total Rev kWh over requested month
            ================= ======================================

        """
        ret = namedtuple("ret", ["Month", Field.kWh_Tariff_1, Field.kWh_Tariff_2, Field.kWh_Tariff_3,
                         Field.kWh_Tariff_4, Field.kWh_Tot, Field.Rev_kWh_Tariff_1,
                         Field.Rev_kWh_Tariff_2, Field.Rev_kWh_Tariff_3,
                         Field.Rev_kWh_Tariff_4, Field.Rev_kWh_Tot])
        month += 1
        ret.Month = str(month)
        if (month < 1) or (month > Extents.Months):
            ret.kWh_Tariff_1 = ret.kWh_Tariff_2 = ret.kWh_Tariff_3 = ret.kWh_Tariff_4 = str(0)
            ret.Rev_kWh_Tariff_1 = ret.Rev_kWh_Tariff_2 = ret.Rev_kWh_Tariff_3 = ret.Rev_kWh_Tariff_4 = str(0)
            ret.kWh_Tot = ret.Rev_kWh_Tot = str(0)
            ekm_log("Out of range(Extents.Months) month = " + str(month))
            return ret

        base_str = "Month_" + str(month) + "_"
        ret.kWh_Tariff_1 = self.m_mons[base_str + "Tariff_1"][MeterData.StringValue]
        ret.kWh_Tariff_2 = self.m_mons[base_str + "Tariff_2"][MeterData.StringValue]
        ret.kWh_Tariff_3 = self.m_mons[base_str + "Tariff_3"][MeterData.StringValue]
        ret.kWh_Tariff_4 = self.m_mons[base_str + "Tariff_4"][MeterData.StringValue]
        ret.kWh_Tot = self.m_mons[base_str + "Tot"][MeterData.StringValue]
        ret.Rev_kWh_Tariff_1 = self.m_rev_mons[base_str + "Tariff_1"][MeterData.StringValue]
        ret.Rev_kWh_Tariff_2 = self.m_rev_mons[base_str + "Tariff_2"][MeterData.StringValue]
        ret.Rev_kWh_Tariff_3 = self.m_rev_mons[base_str + "Tariff_3"][MeterData.StringValue]
        ret.Rev_kWh_Tariff_4 = self.m_rev_mons[base_str + "Tariff_4"][MeterData.StringValue]
        ret.Rev_kWh_Tot = self.m_rev_mons[base_str + "Tot"][MeterData.StringValue]
        return ret

    def readHolidayDates(self):
        """ Serial call to read holiday dates into meter object buffer.

        Returns:
            bool: True on completion.
        """
        self.setContext("readHolidayDates")
        try:
            req_str = "0152310230304230282903"
            self.request(False)
            req_crc = self.calc_crc16(req_str[2:].decode("hex"))
            req_str += req_crc
            self.m_serial_port.write(req_str.decode("hex"))
            raw_ret = self.m_serial_port.getResponse(self.getContext())
            self.serialPostEnd()
            unpacked_read = self.unpackStruct(raw_ret, self.m_hldy)
            self.convertData(unpacked_read, self.m_hldy, self.m_kwh_precision)
            return_crc = self.calc_crc16(raw_ret[1:-2])
            if str(return_crc) == str(self.m_hldy["crc16"][MeterData.StringValue]):
                ekm_log("Holidays and Schedules CRC success")
                self.setContext("")
                return True
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return False

    def extractHolidayDate(self, setting_holiday):
        """ Read a single holiday date from meter buffer.

        Args:
            setting_holiday (int):  Holiday from 0-19 or in range(Extents.Holidays)

        Returns:
            tuple: Holiday tuple, elements are strings.

            =============== ======================
            Holiday         Holiday 0-19 as string
            Day             Day 1-31 as string
            Month           Monty 1-12 as string
            =============== ======================

        """
        ret = namedtuple("result", ["Holiday", "Month", "Day"])
        setting_holiday += 1
        ret.Holiday = str(setting_holiday)

        if (setting_holiday < 1) or (setting_holiday > Extents.Holidays):
            ekm_log("Out of bounds:  holiday " + str(setting_holiday))
            ret.Holiday = ret.Month = ret.Day = str(0)
            return ret

        idxday = "Holiday_" + str(setting_holiday) + "_Day"
        idxmon = "Holiday_" + str(setting_holiday) + "_Mon"
        if idxmon not in self.m_hldy:
            ret.Holiday = ret.Month = ret.Day = str(0)
            return ret
        if idxday not in self.m_hldy:
            ret.Holiday = ret.Month = ret.Day = str(0)
            return ret
        ret.Day = self.m_hldy[idxday][MeterData.StringValue]
        ret.Month = self.m_hldy[idxmon][MeterData.StringValue]
        return ret

    def extractHolidayWeekendSchedules(self):
        """ extract holiday and weekend :class:`~ekmmeters.Schedule` from meter object buffer.

        Returns:
            tuple: Holiday and weekend :class:`~ekmmeters.Schedule` values, as strings.

            ======= ======================================
            Holiday :class:`~ekmmeters.Schedule` as string
            Weekend :class:`~ekmmeters.Schedule` as string
            ======= ======================================

        """
        result = namedtuple("result", ["Weekend", "Holiday"])
        result.Weekend = self.m_hldy["Weekend_Schd"][MeterData.StringValue]
        result.Holiday = self.m_hldy["Holiday_Schd"][MeterData.StringValue]
        return result

    def readSettings(self):
        """Recommended call to read all meter settings at once.

        Returns:
            bool: True if all subsequent serial calls completed with ACK.
        """
        success = (self.readHolidayDates() and
                   self.readMonthTariffs(ReadMonths.kWh) and
                   self.readMonthTariffs(ReadMonths.kWhReverse) and
                   self.readScheduleTariffs(ReadSchedules.Schedules_1_To_4) and
                   self.readScheduleTariffs(ReadSchedules.Schedules_5_To_8))
        return success

    def writeCmdMsg(self, msg):
        """ Internal method to set the command result string.

        Args:
            msg (str): Message built during command.
        """
        ekm_log("(writeCmdMsg | " + self.getContext() + ") " + msg)
        self.m_command_msg = msg

    def readCmdMsg(self):
        """ Getter for message set by last command.

        Returns:
            str: Last set message, if exists.
        """
        return self.m_command_msg

    def clearCmdMsg(self):
        """ Zero out the command message result hint string """
        self.m_command_msg = ""

    def serialCmdPwdAuth(self, password_str):
        """ Password step of set commands

        This method is normally called within another serial command, so it
        does not issue a termination string.  Any default password is set
        in the caller parameter list, never here.

        Args:
            password_str (str): Required password.

        Returns:
            bool: True on completion and ACK.
        """
        result = False
        try:
            req_start = "0150310228" + binascii.hexlify(password_str) + "2903"
            req_crc = self.calc_crc16(req_start[2:].decode("hex"))
            req_str = req_start + req_crc
            self.m_serial_port.write(req_str.decode("hex"))
            if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                ekm_log("Password accepted (" + self.getContext() + ")")
                result = True
            else:
                ekm_log("Password call failure no 06(" + self.getContext() + ")")
        except:
            ekm_log("Password call failure by exception(" + self.getContext() + ")")

            ekm_log(traceback.format_exc(sys.exc_info()))

        return result


class MeterObserver(object):
    """ Unenforced abstract base class for implementations of the observer pattern.

    To use, you must override the constructor and update().
    """

    def __init__(self):
        pass

    def update(self, definition_buffer):
        """ Called by attached :class:`~ekmmeters.Meter` on every :func:`~ekmmeters.Meter.request`.

        Args:
            definition_buffer (SerialBlock): SerialBlock for request
        """
        pass


class IntervalObserver(MeterObserver):
    """ Simplest possible MeterObserver subclass.  Use as template. """

    def __init__(self, interval):
        """

        Args:
            interval (int): Interval to summarize
        """
        super(IntervalObserver, self).__init__()
        self.m_interval = interval
        self.m_summary = SerialBlock()
        pass

    def update(self, def_buf):
        """ Required override of update method called by meter.

        No op in this example subclass.

        Args:
            def_buf (SerialBlock): Buffer from last read.
        """
        ekm_log("Example update() in IntervalObserver called.")
        pass


class V3Meter(Meter):
    """Subclass of Meter and interface to v3 meters."""

    def __init__(self, meter_address="000000000000"):
        """

        Args:
            meter_address (str): 12 character meter address from front of meter.
        """
        self.m_serial_port = None
        self.m_meter_address = ""
        self.m_last_outgoing_queue__time = 0
        self.m_last_incoming_queue_guid = ""
        self.m_raw_read_a = ""
        self.m_a_crc = False
        self.m_kwh_precision = ScaleKWH.Scale10

        super(V3Meter, self).__init__(meter_address)

        # definition buffer for synthetic read
        # (built after reads complete, may merge A and B if necessary)
        self.m_req = SerialBlock()

        self.m_blk_a = SerialBlock()
        self.initWorkFormat()

    def attachPort(self, serial_port):
        """Attach required :class:`~ekmmeters.SerialPort`.

        Args:
            serial_port (SerialPort): Serial port object, does not need to be initialized.
        """
        self.m_serial_port = serial_port
        pass

    def initWorkFormat(self):
        """ Initialize :class:`~ekmmeters.SerialBlock` for V3 read. """
        self.m_blk_a["reserved_10"] = [1, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Model] = [2, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.Firmware] = [1, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.Meter_Address] = [12, FieldType.String, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.kWh_Tot] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.kWh_Tariff_1] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.kWh_Tariff_2] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.kWh_Tariff_3] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.kWh_Tariff_4] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Rev_kWh_Tot] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Rev_kWh_Tariff_1] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Rev_kWh_Tariff_2] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Rev_kWh_Tariff_3] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Rev_kWh_Tariff_4] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.RMS_Volts_Ln_1] = [4, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.RMS_Volts_Ln_2] = [4, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.RMS_Volts_Ln_3] = [4, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.Amps_Ln_1] = [5, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.Amps_Ln_2] = [5, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.Amps_Ln_3] = [5, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.RMS_Watts_Ln_1] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.RMS_Watts_Ln_2] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.RMS_Watts_Ln_3] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.RMS_Watts_Tot] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Cos_Theta_Ln_1] = [4, FieldType.PowerFactor, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Cos_Theta_Ln_2] = [4, FieldType.PowerFactor, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Cos_Theta_Ln_3] = [4, FieldType.PowerFactor, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Max_Demand] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, True]
        self.m_blk_a[Field.Max_Demand_Period] = [1, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.Meter_Time] = [14, FieldType.String, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.CT_Ratio] = [4, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.Pulse_Cnt_1] = [8, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Pulse_Cnt_2] = [8, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Pulse_Cnt_3] = [8, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Pulse_Ratio_1] = [4, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.Pulse_Ratio_2] = [4, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.Pulse_Ratio_3] = [4, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.State_Inputs] = [3, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_a["reserved_11"] = [19, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Status_A] = [1, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_a["reserved_12"] = [4, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_a["crc16"] = [2, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Power_Factor_Ln_1] = [4, FieldType.Int, ScaleType.No, "0", 0, True, False]
        self.m_blk_a[Field.Power_Factor_Ln_2] = [4, FieldType.Int, ScaleType.No, "0", 0, True, False]
        self.m_blk_a[Field.Power_Factor_Ln_3] = [4, FieldType.Int, ScaleType.No, "0", 0, True, False]

    def request(self, send_terminator = False):
        """Required request() override for v3 and standard method to read meter.

        Args:
            send_terminator (bool): Send termination string at end of read.

        Returns:
            bool: CRC request flag result from most recent read
        """
        self.m_a_crc = False
        start_context = self.getContext()
        self.setContext("request[v3A]")
        try:
            self.m_serial_port.write("2f3f".decode("hex") +
                                     self.m_meter_address +
                                     "210d0a".decode("hex"))
            self.m_raw_read_a = self.m_serial_port.getResponse(self.getContext())
            unpacked_read_a = self.unpackStruct(self.m_raw_read_a, self.m_blk_a)
            self.convertData(unpacked_read_a, self.m_blk_a, 1)
            self.m_a_crc = self.crcMeterRead(self.m_raw_read_a, self.m_blk_a)
            if send_terminator:
                self.serialPostEnd()
            self.calculateFields()
            self.makeReturnFormat()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext(start_context)
        return self.m_a_crc

    def makeReturnFormat(self):
        """ Strip reserved and CRC for m_req :class:`~ekmmeters.SerialBlock`. """
        for fld in self.m_blk_a:
            compare_fld = fld.upper()
            if not "RESERVED" in compare_fld and not "CRC" in compare_fld:
                self.m_req[fld] = self.m_blk_a[fld]
        pass

    def getReadBuffer(self):
        """ Return :class:`~ekmmeters.SerialBlock` for last read.

        Appropriate for conversion to JSON or other extraction.

        Returns:
            SerialBlock: A read.
        """
        return self.m_req

    def insert(self, meter_db):
        """ Insert to :class:`~ekmmeters.MeterDB`  subclass.

        Please note MeterDB subclassing is only for simplest-case.

        Args:
            meter_db (MeterDB): Instance of subclass of MeterDB.
        """
        if meter_db:
            meter_db.dbInsert(self.m_req, self.m_raw_read_a, self.m_raw_read_b)
        else:
            ekm_log("Attempt to insert when no MeterDB assigned.")
        pass

    def updateObservers(self):
        """ Fire update method in all attached observers in order of attachment. """
        for observer in self.m_observers:
            try:
                observer.update(self.m_req)
            except:
                ekm_log(traceback.format_exc(sys.exc_info()))

    def getField(self, fld_name):
        """ Return :class:`~ekmmeters.Field` content, scaled and formatted.

        Args:
            fld_name (str): A :class:`~ekmmeters.Field` value which is on your meter.

        Returns:
            str: String value (scaled if numeric) for the field.
        """
        result = ""
        if fld_name in self.m_req:
            result = self.m_req[fld_name][MeterData.StringValue]
        else:
            ekm_log("Requested nonexistent field: " + fld_name)

        return result

    def calculateFields(self):

        pf1 = self.m_blk_a[Field.Cos_Theta_Ln_1][MeterData.StringValue]
        pf2 = self.m_blk_a[Field.Cos_Theta_Ln_2][MeterData.StringValue]
        pf3 = self.m_blk_a[Field.Cos_Theta_Ln_3][MeterData.StringValue]

        pf1_int = self.calcPF(pf1)
        pf2_int = self.calcPF(pf2)
        pf3_int = self.calcPF(pf3)

        self.m_blk_a[Field.Power_Factor_Ln_1][MeterData.StringValue] = str(pf1_int)
        self.m_blk_a[Field.Power_Factor_Ln_2][MeterData.StringValue] = str(pf2_int)
        self.m_blk_a[Field.Power_Factor_Ln_3][MeterData.StringValue] = str(pf3_int)

        self.m_blk_a[Field.Power_Factor_Ln_1][MeterData.NativeValue] = pf1_int
        self.m_blk_a[Field.Power_Factor_Ln_2][MeterData.NativeValue] = pf2_int
        self.m_blk_a[Field.Power_Factor_Ln_3][MeterData.NativeValue] = pf3_int

        pass

    def serialPostEnd(self):
        """ Post termination code to implicitly current meter. """
        ekm_log("Termination string sent (" + self.m_context + ")")
        self.m_serial_port.write("0142300375".decode("hex"))
        pass


class V4Meter(Meter):
    """ Commands and buffers for V4 Omnnimeter. """

    def __init__(self, meter_address="000000000000"):
        """

        Args:
            meter_address (str): 12 character meter address.
        """
        self.m_serial_port = None
        self.m_meter_address = ""
        self.m_raw_read_a = ""
        self.m_raw_read_b = ""
        self.m_a_crc = False
        self.m_b_crc = False
        self.m_kwh_precision = ScaleKWH.EmptyScale
        self.m_lcd_lookup = {}

        super(V4Meter, self).__init__(meter_address)

        # definition buffer for synthetic AB read (built after reads complete
        # static, offsets for retrieving and writing format values
        self.m_req = SerialBlock()

        # read formats
        self.m_blk_a = SerialBlock()
        self.initFormatA()

        self.m_blk_b = SerialBlock()
        self.initFormatB()

        self.initLcd()
        self.initLcdLookup()


    def attachPort(self, serial_port):
        """ Required override to attach the port to the meter.

        Args:
            serial_port (SerialPort): Declared serial port.  Does not need to be initialized.
        """
        self.m_serial_port = serial_port
        pass

    def initFormatA(self):
        """ Initialize A read :class:`~ekmmeters.SerialBlock`."""
        self.m_blk_a["reserved_1"] = [1, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Model] = [2, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.Firmware] = [1, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.Meter_Address] = [12, FieldType.String, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.kWh_Tot] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Reactive_Energy_Tot] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Rev_kWh_Tot] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.kWh_Ln_1] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.kWh_Ln_2] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.kWh_Ln_3] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Rev_kWh_Ln_1] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Rev_kWh_Ln_2] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Rev_kWh_Ln_3] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Resettable_kWh_Tot] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.Resettable_Rev_kWh_Tot] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_a[Field.RMS_Volts_Ln_1] = [4, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.RMS_Volts_Ln_2] = [4, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.RMS_Volts_Ln_3] = [4, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.Amps_Ln_1] = [5, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.Amps_Ln_2] = [5, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.Amps_Ln_3] = [5, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_a[Field.RMS_Watts_Ln_1] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.RMS_Watts_Ln_2] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.RMS_Watts_Ln_3] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.RMS_Watts_Tot] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Cos_Theta_Ln_1] = [4, FieldType.PowerFactor, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Cos_Theta_Ln_2] = [4, FieldType.PowerFactor, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Cos_Theta_Ln_3] = [4, FieldType.PowerFactor, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Reactive_Pwr_Ln_1] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Reactive_Pwr_Ln_2] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Reactive_Pwr_Ln_3] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Reactive_Pwr_Tot] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Line_Freq] = [4, FieldType.Float, ScaleType.Div100, "", 0, False, False]
        self.m_blk_a[Field.Pulse_Cnt_1] = [8, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Pulse_Cnt_2] = [8, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Pulse_Cnt_3] = [8, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.State_Inputs] = [1, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.State_Watts_Dir] = [1, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.State_Out] = [1, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_a[Field.kWh_Scale] = [1, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_a["reserved_2"] = [2, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Meter_Time] = [14, FieldType.String, ScaleType.No, "", 0, False, False]
        self.m_blk_a["reserved_3"] = [2, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_a["reserved_4"] = [4, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_a["crc16"] = [2, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_a[Field.Power_Factor_Ln_1] = [4, FieldType.Int, ScaleType.No, "0", 0, True, False]
        self.m_blk_a[Field.Power_Factor_Ln_2] = [4, FieldType.Int, ScaleType.No, "0", 0, True, False]
        self.m_blk_a[Field.Power_Factor_Ln_3] = [4, FieldType.Int, ScaleType.No, "0", 0, True, False]
        pass

    def initFormatB(self):
        """ Initialize B read :class:`~ekmmeters.SerialBlock`."""
        self.m_blk_b["reserved_5"] = [1, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_b[Field.Model] = [2, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_blk_b[Field.Firmware] = [1, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_blk_b[Field.Meter_Address] = [12, FieldType.String, ScaleType.No, "", 0, False, True]
        self.m_blk_b[Field.kWh_Tariff_1] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_b[Field.kWh_Tariff_2] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_b[Field.kWh_Tariff_3] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_b[Field.kWh_Tariff_4] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_b[Field.Rev_kWh_Tariff_1] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_b[Field.Rev_kWh_Tariff_2] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_b[Field.Rev_kWh_Tariff_3] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_b[Field.Rev_kWh_Tariff_4] = [8, FieldType.Float, ScaleType.KWH, "", 0, False, False]
        self.m_blk_b[Field.RMS_Volts_Ln_1] = [4, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_b[Field.RMS_Volts_Ln_2] = [4, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_b[Field.RMS_Volts_Ln_3] = [4, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_b[Field.Amps_Ln_1] = [5, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_b[Field.Amps_Ln_2] = [5, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_b[Field.Amps_Ln_3] = [5, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_b[Field.RMS_Watts_Ln_1] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_b[Field.RMS_Watts_Ln_2] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_b[Field.RMS_Watts_Ln_3] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_b[Field.RMS_Watts_Tot] = [7, FieldType.Int, ScaleType.No, "", 0, False, False]
        self.m_blk_b[Field.Cos_Theta_Ln_1] = [4, FieldType.PowerFactor, ScaleType.No, "", 0, False, False]
        self.m_blk_b[Field.Cos_Theta_Ln_2] = [4, FieldType.PowerFactor, ScaleType.No, "", 0, False, False]
        self.m_blk_b[Field.Cos_Theta_Ln_3] = [4, FieldType.PowerFactor, ScaleType.No, "", 0, False, False]
        self.m_blk_b[Field.RMS_Watts_Max_Demand] = [8, FieldType.Float, ScaleType.Div10, "", 0, False, False]
        self.m_blk_b[Field.Max_Demand_Period] = [1, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_b[Field.Pulse_Ratio_1] = [4, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_b[Field.Pulse_Ratio_2] = [4, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_b[Field.Pulse_Ratio_3] = [4, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_b[Field.CT_Ratio] = [4, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_b["reserved_6"] = [1, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_b[Field.Pulse_Output_Ratio] = [4, FieldType.Int, ScaleType.No, "", 0, False, True]
        self.m_blk_b["reserved_7"] = [53, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_b[Field.Status_A] = [1, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_blk_b[Field.Status_B] = [1, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_blk_b[Field.Status_C] = [1, FieldType.Hex, ScaleType.No, "", 0, False, True]
        self.m_blk_b[Field.Meter_Time] = [14, FieldType.String, ScaleType.No, "", 0, False, False]
        self.m_blk_b["reserved_8"] = [2, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_b["reserved_9"] = [4, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_b["crc16"] = [2, FieldType.Hex, ScaleType.No, "", 0, False, False]
        self.m_blk_b[Field.Net_Calc_Watts_Ln_1] = [7, FieldType.Int, ScaleType.No, "0", 0, True, False]
        self.m_blk_b[Field.Net_Calc_Watts_Ln_2] = [7, FieldType.Int, ScaleType.No, "0", 0, True, False]
        self.m_blk_b[Field.Net_Calc_Watts_Ln_3] = [7, FieldType.Int, ScaleType.No, "0", 0, True, False]
        self.m_blk_b[Field.Net_Calc_Watts_Tot] = [7, FieldType.Int, ScaleType.No, "0", 0, True, False]
        self.m_blk_b[Field.Power_Factor_Ln_1] = [4, FieldType.Int, ScaleType.No, "0", 0, True, False]
        self.m_blk_b[Field.Power_Factor_Ln_2] = [4, FieldType.Int, ScaleType.No, "0", 0, True, False]
        self.m_blk_b[Field.Power_Factor_Ln_3] = [4, FieldType.Int, ScaleType.No, "0", 0, True, False]
        pass

    def initLcdLookup(self):
        """ Initialize lookup table for string input of LCD fields """
        self.m_lcd_lookup["kWh_Tot"] = LCDItems.kWh_Tot
        self.m_lcd_lookup["Rev_kWh_Tot"] = LCDItems.Rev_kWh_Tot
        self.m_lcd_lookup["RMS_Volts_Ln_1"] = LCDItems.RMS_Volts_Ln_1
        self.m_lcd_lookup["RMS_Volts_Ln_2"] = LCDItems.RMS_Volts_Ln_2
        self.m_lcd_lookup["RMS_Volts_Ln_3"] = LCDItems.RMS_Volts_Ln_3
        self.m_lcd_lookup["Amps_Ln_1"] = LCDItems.Amps_Ln_1
        self.m_lcd_lookup["Amps_Ln_2"] = LCDItems.Amps_Ln_1
        self.m_lcd_lookup["Amps_Ln_3"] = LCDItems.Amps_Ln_3
        self.m_lcd_lookup["RMS_Watts_Ln_1"] = LCDItems.RMS_Watts_Ln_1
        self.m_lcd_lookup["RMS_Watts_Ln_2"] = LCDItems.RMS_Watts_Ln_2
        self.m_lcd_lookup["RMS_Watts_Ln_3"] = LCDItems.RMS_Watts_Ln_3
        self.m_lcd_lookup["RMS_Watts_Tot"] = LCDItems.RMS_Watts_Tot
        self.m_lcd_lookup["Power_Factor_Ln_1"] = LCDItems.Power_Factor_Ln_1
        self.m_lcd_lookup["Power_Factor_Ln_2"] = LCDItems.Power_Factor_Ln_2
        self.m_lcd_lookup["Power_Factor_Ln_3"] = LCDItems.Power_Factor_Ln_3
        self.m_lcd_lookup["kWh_Tariff_1"] = LCDItems.kWh_Tariff_1
        self.m_lcd_lookup["kWh_Tariff_2"] = LCDItems.kWh_Tariff_2
        self.m_lcd_lookup["kWh_Tariff_3"] = LCDItems.kWh_Tariff_3
        self.m_lcd_lookup["kWh_Tariff_4"] = LCDItems.kWh_Tariff_4
        self.m_lcd_lookup["Rev_kWh_Tariff_1"] = LCDItems.Rev_kWh_Tariff_1
        self.m_lcd_lookup["Rev_kWh_Tariff_2"] = LCDItems.Rev_kWh_Tariff_2
        self.m_lcd_lookup["Rev_kWh_Tariff_3"] = LCDItems.Rev_kWh_Tariff_3
        self.m_lcd_lookup["Rev_kWh_Tariff_4"] = LCDItems.Rev_kWh_Tariff_4
        self.m_lcd_lookup["Reactive_Pwr_Ln_1"] = LCDItems.Reactive_Pwr_Ln_1
        self.m_lcd_lookup["Reactive_Pwr_Ln_2"] = LCDItems.Reactive_Pwr_Ln_2
        self.m_lcd_lookup["Reactive_Pwr_Ln_3"] = LCDItems.Reactive_Pwr_Ln_3
        self.m_lcd_lookup["Reactive_Pwr_Tot"] = LCDItems.Reactive_Pwr_Tot
        self.m_lcd_lookup["Line_Freq"] = LCDItems.Line_Freq
        self.m_lcd_lookup["Pulse_Cnt_1"] = LCDItems.Pulse_Cnt_1
        self.m_lcd_lookup["Pulse_Cnt_2"] = LCDItems.Pulse_Cnt_2
        self.m_lcd_lookup["Pulse_Cnt_3"] = LCDItems.Pulse_Cnt_3
        self.m_lcd_lookup["kWh_Ln_1"] = LCDItems.kWh_Ln_1
        self.m_lcd_lookup["Rev_kWh_Ln_1"] = LCDItems.Rev_kWh_Ln_1
        self.m_lcd_lookup["kWh_Ln_2"] = LCDItems.kWh_Ln_2
        self.m_lcd_lookup["Rev_kWh_Ln_2"] = LCDItems.Rev_kWh_Ln_2
        self.m_lcd_lookup["kWh_Ln_3"] = LCDItems.kWh_Ln_3
        self.m_lcd_lookup["Rev_kWh_Ln_3"] = LCDItems.Rev_kWh_Ln_3
        self.m_lcd_lookup["Reactive_Energy_Tot"] = LCDItems.Reactive_Energy_Tot
        self.m_lcd_lookup["Max_Demand_Rst"] = LCDItems.Max_Demand_Rst
        self.m_lcd_lookup["Rev_kWh_Rst"] = LCDItems.Rev_kWh_Rst
        self.m_lcd_lookup["State_Inputs"] = LCDItems.State_Inputs
        self.m_lcd_lookup["Max_Demand"] = LCDItems.Max_Demand

    def request(self, send_terminator = False):
        """ Combined A and B read for V4 meter.

        Args:
            send_terminator (bool): Send termination string at end of read.

        Returns:
            bool: True on completion.
        """
        try:
            if self.requestA() and self.requestB():
                self.makeAB()
                self.calculateFields()
                self.updateObservers()
                return True
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        return False

    def requestA(self):
        """Issue an A read on V4 meter.

        Returns:
            bool: True if CRC match at end of call.
        """
        work_context = self.getContext()
        self.setContext("request[v4A]")
        self.m_serial_port.write("2f3f".decode("hex") + self.m_meter_address + "3030210d0a".decode("hex"))
        self.m_raw_read_a = self.m_serial_port.getResponse(self.getContext())
        unpacked_read_a = self.unpackStruct(self.m_raw_read_a, self.m_blk_a)
        self.convertData(unpacked_read_a, self.m_blk_a)
        self.m_kwh_precision = int(self.m_blk_a[Field.kWh_Scale][MeterData.NativeValue])
        self.m_a_crc = self.crcMeterRead(self.m_raw_read_a, self.m_blk_a)
        self.setContext(work_context)
        return self.m_a_crc

    def requestB(self):
        """ Issue a B read on V4 meter.

        Returns:
            bool: True if CRC match at end of call.
        """
        work_context = self.getContext()
        self.setContext("request[v4B]")
        self.m_serial_port.write("2f3f".decode("hex") + self.m_meter_address + "3031210d0a".decode("hex"))
        self.m_raw_read_b = self.m_serial_port.getResponse(self.getContext())
        unpacked_read_b = self.unpackStruct(self.m_raw_read_b, self.m_blk_b)
        self.convertData(unpacked_read_b, self.m_blk_b, self.m_kwh_precision)
        self.m_b_crc = self.crcMeterRead(self.m_raw_read_b, self.m_blk_b)
        self.setContext(work_context)
        return self.m_b_crc

    def makeAB(self):
        """ Munge A and B reads into single serial block with only unique fields."""
        for fld in self.m_blk_a:
            compare_fld = fld.upper()
            if not "RESERVED" in compare_fld and not "CRC" in compare_fld:
                self.m_req[fld] = self.m_blk_a[fld]
        for fld in self.m_blk_b:
            compare_fld = fld.upper()
            if not "RESERVED" in compare_fld and not "CRC" in compare_fld:
                self.m_req[fld] = self.m_blk_b[fld]
        pass

    def getReadBuffer(self):
        """ Return the read buffer containing A and B reads.

        Appropriate for JSON conversion or other processing in an agent.

        Returns:
            SerialBlock: A :class:`~ekmmeters.SerialBlock`  containing both A and B reads.
        """
        return self.m_req

    def getField(self, fld_name):
        """ Return :class:`~ekmmeters.Field` content, scaled and formatted.

        Args:
            fld_name (str): A `:class:~ekmmeters.Field` value which is on your meter.

        Returns:
            str: String value (scaled if numeric) for the field.
        """
        result = ""
        if fld_name in self.m_req:
            result = self.m_req[fld_name][MeterData.StringValue]
        else:
            ekm_log("Requested nonexistent field: " + fld_name)

        return result


    def calculateFields(self):
        """Write calculated fields for read buffer."""
        pf1 = self.m_blk_b[Field.Cos_Theta_Ln_1][MeterData.StringValue]
        pf2 = self.m_blk_b[Field.Cos_Theta_Ln_2][MeterData.StringValue]
        pf3 = self.m_blk_b[Field.Cos_Theta_Ln_3][MeterData.StringValue]

        pf1_int = self.calcPF(pf1)
        pf2_int = self.calcPF(pf2)
        pf3_int = self.calcPF(pf3)

        self.m_blk_b[Field.Power_Factor_Ln_1][MeterData.StringValue] = str(pf1_int)
        self.m_blk_b[Field.Power_Factor_Ln_2][MeterData.StringValue] = str(pf2_int)
        self.m_blk_b[Field.Power_Factor_Ln_3][MeterData.StringValue] = str(pf3_int)

        self.m_blk_b[Field.Power_Factor_Ln_1][MeterData.NativeValue] = pf1_int
        self.m_blk_b[Field.Power_Factor_Ln_2][MeterData.NativeValue] = pf2_int
        self.m_blk_b[Field.Power_Factor_Ln_3][MeterData.NativeValue] = pf2_int

        rms_watts_1 = self.m_blk_b[Field.RMS_Watts_Ln_1][MeterData.NativeValue]
        rms_watts_2 = self.m_blk_b[Field.RMS_Watts_Ln_2][MeterData.NativeValue]
        rms_watts_3 = self.m_blk_b[Field.RMS_Watts_Ln_3][MeterData.NativeValue]

        sign_rms_watts_1 = 1
        sign_rms_watts_2 = 1
        sign_rms_watts_3 = 1

        direction_byte = self.m_blk_a[Field.State_Watts_Dir][MeterData.NativeValue]

        if direction_byte == DirectionFlag.ForwardForwardForward:
            # all good
            pass
        if direction_byte == DirectionFlag.ForwardForwardReverse:
            sign_rms_watts_3 = -1
            pass
        if direction_byte == DirectionFlag.ForwardReverseForward:
            sign_rms_watts_2 = -1
            pass
        if direction_byte == DirectionFlag.ReverseForwardForward:
            sign_rms_watts_1 = -1
            pass
        if direction_byte == DirectionFlag.ForwardReverseReverse:
            sign_rms_watts_2 = -1
            sign_rms_watts_3 = -1
            pass
        if direction_byte == DirectionFlag.ReverseForwardReverse:
            sign_rms_watts_1 = -1
            sign_rms_watts_3 = -1
            pass
        if direction_byte == DirectionFlag.ReverseReverseForward:
            sign_rms_watts_1 = -1
            sign_rms_watts_2 = -1
            pass
        if direction_byte == DirectionFlag.ReverseReverseReverse:
            sign_rms_watts_1 = -1
            sign_rms_watts_2 = -1
            sign_rms_watts_3 = -1
            pass

        net_watts_1 = rms_watts_1 * sign_rms_watts_1
        net_watts_2 = rms_watts_2 * sign_rms_watts_2
        net_watts_3 = rms_watts_3 * sign_rms_watts_3
        net_watts_tot = net_watts_1 + net_watts_2 + net_watts_3

        self.m_blk_b[Field.Net_Calc_Watts_Ln_1][MeterData.NativeValue] = net_watts_1
        self.m_blk_b[Field.Net_Calc_Watts_Ln_2][MeterData.NativeValue] = net_watts_2
        self.m_blk_b[Field.Net_Calc_Watts_Ln_3][MeterData.NativeValue] = net_watts_3
        self.m_blk_b[Field.Net_Calc_Watts_Tot][MeterData.NativeValue] = net_watts_tot

        self.m_blk_b[Field.Net_Calc_Watts_Ln_1][MeterData.StringValue] = str(net_watts_1)
        self.m_blk_b[Field.Net_Calc_Watts_Ln_2][MeterData.StringValue] = str(net_watts_2)
        self.m_blk_b[Field.Net_Calc_Watts_Ln_3][MeterData.StringValue] = str(net_watts_3)
        self.m_blk_b[Field.Net_Calc_Watts_Tot][MeterData.StringValue] = str(net_watts_tot)

        pass

    def updateObservers(self):
        """ Call the update() method in all attached  observers in order of attachment.

        Called internally after request().
        """
        for observer in self.m_observers:
            observer.update(self.m_req)

    def insert(self, meter_db):
        """ Insert to :class:`~ekmmeters.MeterDB`  subclass.

        Please note MeterDB subclassing is only for simplest-case.

        Args:
            meter_db (MeterDB): Instance of subclass of MeterDB.
        """
        if meter_db:
            meter_db.dbInsert(self.m_req, self.m_raw_read_a, self.m_raw_read_b)
        else:
            ekm_log("Attempt to insert when no MeterDB assigned.")
        pass

    def lcdString(self, item_str):
        """Translate a string to corresponding LCD field integer

        Args:
            item_str (str): String identical to :class:`~ekmmeters.LcdItems` entry.

        Returns:
            int:  :class:`~ekmmeters.LcdItems` integer or 0 if not found.

        """
        if item_str in self.m_lcd_lookup:
            return self.m_lcd_lookup[item_str]
        else:
            return 0



    def setLCDCmd(self, display_list, password="00000000"):
        """ Single call wrapper for LCD set."

        Wraps :func:`~ekmmeters.V4Meter.setLcd` and associated init and add methods.

        Args:
            display_list (list): List composed of :class:`~ekmmeters.LCDItems`
            password (str): Optional password.

        Returns:
            bool: Passthrough from :func:`~ekmmeters.V4Meter.setLcd`
        """
        result = False
        try:
            self.initLcd()
            item_cnt = len(display_list)
            if (item_cnt > 40) or (item_cnt <= 0):
                ekm_log("LCD item list must have between 1 and 40 items")
                return False

            for display_item in display_list:
                self.addLcdItem(int(display_item))
            result = self.setLCD(password)
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        return result

    def setRelay(self, seconds, relay, status, password="00000000"):
        """Serial call to set relay.

        Args:
            seconds (int): Seconds to hold, ero is hold forever. See :class:`~ekmmeters.RelayInterval`.
            relay (int): Selected relay, see :class:`~ekmmeters.Relay`.
            status (int): Status to set, see :class:`~ekmmeters.RelayState`
            password (str): Optional password

        Returns:
            bool: True on completion and ACK.
        """
        result = False
        self.setContext("setRelay")
        try:
            self.clearCmdMsg()

            if len(password) != 8:
                self.writeCmdMsg("Invalid password length.")
                self.setContext("")
                return result

            if seconds < 0 or seconds > 9999:
                self.writeCmdMsg("Relay duration must be between 0 and 9999.")
                self.setContext("")
                return result

            if not self.requestA():
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_str = ""
                    req_str = ("01573102303038" +
                               binascii.hexlify(str(relay)).zfill(2) +
                               "28" +
                               binascii.hexlify(str(status)).zfill(2) +
                               binascii.hexlify(str(seconds).zfill(4)) + "2903")
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success: 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def serialPostEnd(self):
        """ Send termination string to implicit current meter."""
        ekm_log("Termination string sent (" + self.m_context + ")")

        try:
            self.m_serial_port.write("0142300375".decode("hex"))
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        pass

    def setPulseInputRatio(self, line_in, new_cnst, password="00000000"):
        """Serial call to set pulse input ratio on a line.

        Args:
            line_in (int): Member of :class:`~ekmmeters.Pulse`
            new_cnst (int): New pulse input ratio
            password (str): Optional password

        Returns:

        """
        result = False
        self.setContext("setPulseInputRatio")

        try:
            if not self.requestA():
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_const = binascii.hexlify(str(new_cnst).zfill(4))
                    line_const = binascii.hexlify(str(line_in - 1))
                    req_str = "01573102303041" + line_const + "28" + req_const + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success: 06 returned.")
                        result = True

            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def setZeroResettableKWH(self, password="00000000"):
        """ Serial call to zero resettable kWh registers.

        Args:
            password (str): Optional password.

        Returns:
            bool: True on completion and ACK.
        """
        result = False
        self.setContext("setZeroResettableKWH")
        try:
            if not self.requestA():
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_str = "0157310230304433282903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success: 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def setPulseOutputRatio(self, new_pout, password="00000000"):
        """ Serial call to set pulse output ratio.

        Args:
            new_pout (int):  Legal output, member of  :class:`~ekmmeters.PulseOutput` .
            password (str): Optional password

        Returns:
            bool: True on completion and ACK

        """
        result = False
        self.setContext("setPulseOutputRatio")
        try:
            if not self.requestA():
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_str = "015731023030443428" + binascii.hexlify(str(new_pout).zfill(4)) + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success: 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

    def initLcd(self):
        """
        Simple init for LCD item list
        """
        self.m_lcd_items = []
        pass

    def addLcdItem(self, lcd_item_no):
        """

        Simple append to internal buffer.

        Used with :func:`~ekmmeters.V4Meter.setLcd` and :func:`~ekmmeters.V4Meter.initLcd`

        Args:
            lcd_item_no (int): Member of :class:`~ekmmeters.LCDItems`
        """
        self.m_lcd_items.append(lcd_item_no)
        pass

    def setLCD(self, password="00000000"):
        """ Serial call to set LCD using meter object bufer.

        Used with :func:`~ekmmeters.V4Meter.addLcdItem`.

        Args:
            password (str): Optional password

        Returns:
            bool: True on completion and ACK.
        """
        result = False
        self.setContext("setLCD")
        try:
            self.clearCmdMsg()

            if len(password) != 8:
                self.writeCmdMsg("Invalid password length.")
                self.setContext("")
                return result

            if not self.request():
                self.writeCmdMsg("Bad read CRC on setting")
            else:
                if not self.serialCmdPwdAuth(password):
                    self.writeCmdMsg("Password failure")
                else:
                    req_table = ""

                    fill_len = 40 - len(self.m_lcd_items)

                    for lcdid in self.m_lcd_items:
                        append_val = binascii.hexlify(str(lcdid).zfill(2))
                        req_table += append_val

                    for i in range(0, fill_len):
                        append_val = binascii.hexlify(str(0).zfill(2))
                        req_table += append_val

                    req_str = "015731023030443228" + req_table + "2903"
                    req_str += self.calc_crc16(req_str[2:].decode("hex"))
                    self.m_serial_port.write(req_str.decode("hex"))
                    if self.m_serial_port.getResponse(self.getContext()).encode("hex") == "06":
                        self.writeCmdMsg("Success: 06 returned.")
                        result = True
            self.serialPostEnd()
        except:
            ekm_log(traceback.format_exc(sys.exc_info()))

        self.setContext("")
        return result

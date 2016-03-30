'''
Simple unit tests for the ekmmeters library.  While it should work
under any python unittest caller,  it requires attached, named meters,
and the serial port name to use.  The included sample values are as
employed in Windows, Linux and OS X release tests.
(c) 2015, 2016 EKM Metering.
This software is provided under an MIT license:
    https://opensource.org/licenses/MIT
'''
import ConfigParser
import random
import unittest

from ekmmeters import *


class TestObserver(MeterObserver):
    '''
    Observer subclass for test
    '''

    def __init__(self):
        '''
        Constructor for test observer
        '''
        super(MeterObserver, self).__init__()
        pass

    def update(self, definition_buffer):
        '''
        Required override of update() for this observer

        Parameters
        ----------
        definition_buffer : collections.OrderedDict
            Results of last read
        '''
        pass


def loadparams():
    '''
    Helper.  Call at start of any test function which needs the meter and port
    (all of them)

    '''
    test_ini = ConfigParser.ConfigParser()
    test_ini.read('unittest.ini')
    test_port = test_ini.get("PARAMS", 'test_port')
    v3_addr = test_ini.get("PARAMS", 'v3_addr')
    v4_addr = test_ini.get("PARAMS", 'v4_addr')
    dbpath = test_ini.get("PARAMS", 'dbpath')
    user_prompts = test_ini.getboolean("PARAMS", "user_prompts")
    wait = test_ini.getfloat("PARAMS", "force_wait")
    return (wait, test_port, v3_addr, v4_addr, dbpath, user_prompts)


class AcceptanceTest(unittest.TestCase):
    '''
    Lightweight traversal of all reads and settings.
    Non schedule settings tests include both read
    and write, with 2 consecutive values.

    Edit unittest.ini to parameterize test for
    currently attached meters and port

    In real use, the serial port would remain open over
    an entire session.  In this set of test methods,
    every test method can be executed directly and alone.

    Simple manual inspection required to:
    * Verify relay operation during test call
    * Check LCD display during test call
    * Check return for schedule period, month schedules.
      holiday dates, seasons, weekend schedules and
      resettable kWh. Use any unittests drop down tool.
      as UI.  Ideally a high current pickup
      is avaliable. Modify test calls as appropriate
      for inspection.
    '''

    @classmethod
    def setUpClass(cls):
        super(AcceptanceTest, cls).setUpClass()

    def testReadAndDb(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        print v4_addr
        port = SerialPort(test_port, force_wait=wait)
        print "*****  Read and database tests"
        print "Manually remove test database to force recreate"
        failed = False

        try:
            ekm_set_log(ekm_print_log)
            my_observer = IntervalObserver(10)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV3 = V3Meter(v3_addr)
            meterV4.attachPort(port)

            meterV4.registerObserver(my_observer)
            meterV3.attachPort(port)
            meterV4.request()
            meterV3.request()
            meterDB = SqliteMeterDB("test.db")
            meterDB.dbDropReads()
            meterDB.dbCreate()

            print "*****************************************************"
            print "***** Two reads from each meter"
            for i in range(2):
                i += 1
                try:
                    if meterV4.request():
                        meterV4.insert(meterDB)
                        test = meterV4.jsonRender(meterV4.getReadBuffer())
                        json_test = json.loads(test)
                        print "Read meter address (Request and jsonRender): " \
                              + json_test[Field.Meter_Address]
                        print json.dumps(json_test, indent=4)
                    else:
                        print "Fail v4 request\n"

                    if meterV3.request():
                        meterV3.insert(meterDB)
                        test = meterV3.jsonRender(meterV3.getReadBuffer())
                        json_test = json.loads(test)
                        print "Read meter address (Request and jsonRender): " \
                              + json_test[Field.Meter_Address]
                        print json.dumps(json_test, indent=4)
                    else:
                        print "Fail v3 request\n"
                except:
                    print traceback.format_exc(sys.exc_info())
                    for frame in traceback.extract_tb(sys.exc_info()[2]):
                        fname, lineno, fn, text = frame
                        print("Error in %s on line %d" % (fname, lineno))
                    return False
            print "***** End Two reads from each meter"
            print "*****************************************************"
            print "***** Database reads "
            print "***** MeterDB.renderJsonReadsSince (v3, v4): "
            print meterDB.renderJsonReadsSince(0, meterV4.getMeterAddress())
            print meterDB.renderJsonReadsSince(0, meterV3.getMeterAddress())
            print "*****************************************************"
            print "***** MeterDB.renderRaw JsonReadsSince (v3, v4): "
            print "\nMeterDB.renderRawJsonReadsSince: "
            print meterDB.renderRawJsonReadsSince(0, meterV4.getMeterAddress())
            print meterDB.renderRawJsonReadsSince(0, meterV3.getMeterAddress())
            print "***** End database reads"
            print "*****************************************************"
            print "***** Delete table "
            print "*****Run MeterDB.dbDropReads (clear) "
            print "***** End delete table"
            print "*****************************************************"
            self.assertEqual(True, True)

        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname, lineno, fn, text = frame
                print("Error in %s on line %d" % (fname, lineno))
            self.assertEqual(True, False)

        port.closePort()
        if failed == True:
            self.assertEqual(True, False)

    def testSetPasswordV3(self):
        failed = False
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        try:
            print "***** password V3 test"
            print "If this test fails, the meter password may be stuck at 00000001"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            self.assertEqual(meterV3.setMeterPassword("00000001", "00000000"), True)
            self.assertEqual(meterV3.setMeterPassword("00000000", "00000001"), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        if failed == True:
            self.assertEqual(True, False)

    def testSetPasswordV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print "***** password V3 test"
            print "If this test fails, the meter password may be stuck at 00000001"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            self.assertEqual(meterV3.setMeterPassword("00000001", "00000000"), True)
            self.assertEqual(meterV3.setMeterPassword("00000000", "00000001"), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testReadV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** read  V4 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.request(), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testReadScheduleTariffsV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** read  periods and times V4 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.readScheduleTariffs(ReadSchedules.Schedules_1_To_4), True)
            self.assertEqual(meterV4.readScheduleTariffs(ReadSchedules.Schedules_5_To_8), True)
            pt_buf_1 = meterV4.getSchedulesBuffer(ReadSchedules.Schedules_1_To_4)
            pt_buf_2 = meterV4.getSchedulesBuffer(ReadSchedules.Schedules_5_To_8)
            print meterV4.jsonRender(pt_buf_1)
            print meterV4.jsonRender(pt_buf_2)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testReadScheduleTariffsV3(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        failed = False
        port = SerialPort(test_port, force_wait=wait)
        try:
            print"***** read  periods and times V3 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            self.assertEqual(meterV3.readScheduleTariffs(ReadSchedules.Schedules_1_To_4), True)
            self.assertEqual(meterV3.readScheduleTariffs(ReadSchedules.Schedules_5_To_8), True)
            pt_buf_1 = meterV3.getSchedulesBuffer(ReadSchedules.Schedules_1_To_4)
            pt_buf_2 = meterV3.getSchedulesBuffer(ReadSchedules.Schedules_5_To_8)
            print meterV3.jsonRender(pt_buf_1)
            print meterV3.jsonRender(pt_buf_2)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testReadMonthsTariffsV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        failed = False
        port = SerialPort(test_port, force_wait=wait)
        try:
            print"***** read  months V4 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.readMonthTariffs(ReadMonths.kWh), True)
            mon_buf_kwh = meterV4.getMonthsBuffer(ReadMonths.kWh)
            print meterV4.jsonRender(mon_buf_kwh)
            self.assertEqual(meterV4.readMonthTariffs(ReadMonths.kWhReverse), True)
            mon_buf_rev_kwh = meterV4.getMonthsBuffer(ReadMonths.kWhReverse)
            print meterV4.jsonRender(mon_buf_rev_kwh)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testReadHolidayDatesV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** read  holidays V4 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.readHolidayDates(), True)
            hd_buf = meterV4.getHolidayDatesBuffer()
            print meterV4.jsonRender(hd_buf)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testReadHolidayDatesV3(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** read  holidays V3 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            self.assertEqual(meterV3.readHolidayDates(), True)
            hd_buf = meterV3.getHolidayDatesBuffer()
            print meterV3.jsonRender(hd_buf)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testReadMonthTariffsV3(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** read  months V3 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            self.assertEqual(meterV3.readMonthTariffs(ReadMonths.kWh), True)
            mon_buf_kwh = meterV3.getMonthsBuffer(ReadMonths.kWh)
            print meterV3.jsonRender(mon_buf_kwh)
            self.assertEqual(meterV3.readMonthTariffs(ReadMonths.kWhReverse), True)
            mon_buf_rev_kwh = meterV3.getMonthsBuffer(ReadMonths.kWhReverse)
            print meterV3.jsonRender(mon_buf_rev_kwh)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testReadV3(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** read  V3 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            self.assertEqual(meterV3.request(), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetCtV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        failed = False
        port = SerialPort(test_port, force_wait=wait)
        try:
            print"***** CT V4 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.setCTRatio(CTRatio.Amps_200), True)
            self.assertEqual(meterV4.request(), True)
            str_ct = meterV4.getField(Field.CT_Ratio)
            print "V4 CT after 200 set = " + str_ct
            self.assertEqual(str_ct == str(CTRatio.Amps_200), True)
            self.assertEqual(meterV4.setCTRatio(CTRatio.Amps_400), True)
            self.assertEqual(meterV4.request(), True)
            str_ct = meterV4.getField(Field.CT_Ratio)
            print "V4 CT after 400 set = " + str_ct
            self.assertEqual(str_ct == str(CTRatio.Amps_400), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetHoldayWeekendV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        failed = False
        port = SerialPort(test_port, force_wait=wait)
        try:
            print"***** Holiday weekend V4 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.setWeekendHolidaySchedules(1, 2), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetHolidayWeekendV3(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** Holiday weekend V3 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            self.assertEqual(meterV3.setWeekendHolidaySchedules(1, 2), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetMaxDemandIntervalV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"*****  Max Demand Interval Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.setMaxDemandResetInterval(MaxDemandResetInterval.Hourly), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetPulseOuputRatioV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** Pulse output V4 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.setPulseOutputRatio(PulseOutput.Ratio_5), True)
            self.assertEqual(meterV4.request(), True)
            str_out = meterV4.getField(Field.Pulse_Output_Ratio)
            self.assertEqual(str(str_out) == str(PulseOutput.Ratio_5), True)
            self.assertEqual(meterV4.setPulseOutputRatio(PulseOutput.Ratio_16), True)
            self.assertEqual(meterV4.request(), True)
            str_out = meterV4.getField(Field.Pulse_Output_Ratio)
            self.assertEqual(str(str_out) == str(PulseOutput.Ratio_16), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetCtV3(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            ekm_set_log(ekm_print_log)
            print"***** CT V3 Test"
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            self.assertEqual(meterV3.request(), True)
            self.assertEqual(meterV3.setCTRatio(CTRatio.Amps_200), True)
            self.assertEqual(meterV3.request(), True)
            str_ct = meterV3.getField(Field.CT_Ratio)
            print "V3 CT after 200 set = " + str_ct
            self.assertEqual(str_ct == str(CTRatio.Amps_200), True)
            self.assertEqual(meterV3.request(), True)
            self.assertEqual(meterV3.setCTRatio(CTRatio.Amps_400), True)
            self.assertEqual(meterV3.request(), True)
            str_ct = meterV3.getField(Field.CT_Ratio)
            print "V3 CT after 400 set = " + str_ct
            self.assertEqual(str_ct == str(CTRatio.Amps_400), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetTimeV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print "*****  Set Meter Time V4"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.request(), True)
            yy = 2016
            mm = 11
            dd = 22
            hh = 15
            min = 39
            ss = 2
            self.assertEqual(meterV4.setTime(yy, mm, dd, hh, min, ss), True)
            self.assertEqual(meterV4.request(), True)
            str_time = meterV4.getField(Field.Meter_Time)
            print str_time
            date_tuple = meterV4.splitEkmDate(int(str_time))
            if (((yy - 2000) == date_tuple.yy) and
                        (mm == date_tuple.mm) and
                        (dd == date_tuple.dd) and
                        (hh == date_tuple.hh) and
                        (min == date_tuple.minutes)):
                print  "Passed and return time agree pass 1"
            else:
                self.assertEqual(True, False)
            yy = 2019
            mm = 3
            dd = 16
            hh = 23
            min = 56
            ss = 5
            self.assertEqual(meterV4.setTime(yy, mm, dd, hh, min, ss), True)
            self.assertEqual(meterV4.request(), True)
            str_time = meterV4.getField(Field.Meter_Time)
            date_tuple = meterV4.splitEkmDate(int(str_time))
            if (((yy - 2000) == date_tuple.yy) and
                        (mm == date_tuple.mm) and
                        (dd == date_tuple.dd) and
                        (hh == date_tuple.hh) and
                        (min == date_tuple.minutes)):
                print  "Passed and return time agree pass 2"
            else:
                self.assertEqual(True, False)

            self.assertEqual(True, True)

        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetTimeV3(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        failed = False
        port = SerialPort(test_port, force_wait=wait)
        try:
            print "*****  Set Meter Time V3"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            self.assertEqual(meterV3.request(), True)
            yy = 2016
            mm = 11
            dd = 22
            hh = 15
            min = 39
            ss = 2
            self.assertEqual(meterV3.setTime(yy, mm, dd, hh, min, ss), True)
            self.assertEqual(meterV3.request(), True)

            str_time = meterV3.getField(Field.Meter_Time)
            date_tuple = meterV3.splitEkmDate(int(str_time))
            if (((yy - 2000) == date_tuple.yy) and
                        (mm == date_tuple.mm) and
                        (dd == date_tuple.dd) and
                        (hh == date_tuple.hh) and
                        (min == date_tuple.minutes)):
                print  "Passed and return time agree pass 1"
            else:
                self.assertEqual(True, False)

            yy = 2019
            mm = 3
            dd = 16
            hh = 23
            min = 56
            ss = 5

            self.assertEqual(meterV3.setTime(yy, mm, dd, hh, min, ss), True)
            self.assertEqual(meterV3.request(), True)
            str_time = meterV3.getField(Field.Meter_Time)
            date_tuple = meterV3.splitEkmDate(int(str_time))
            if (((yy - 2000) == date_tuple.yy) and
                        (mm == date_tuple.mm) and
                        (dd == date_tuple.dd) and
                        (hh == date_tuple.hh) and
                        (min == date_tuple.minutes)):
                print  "Passed and return time agree pass 2"
            else:
                self.assertEqual(True, False)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetMaxDemandPeriodV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** Max Demand Period V4 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.setMaxDemandPeriod(MaxDemandPeriod.At_15_Minutes), True)

            self.assertEqual(meterV4.request(), True)
            str_mdp = meterV4.getField(Field.Max_Demand_Period)
            if int(str_mdp) != MaxDemandPeriod.At_15_Minutes:
                self.assertEqual(False, True)
            self.assertEqual(meterV4.setMaxDemandPeriod(MaxDemandPeriod.At_30_Minutes), True)
            self.assertEqual(meterV4.request(), True)
            str_mdp = meterV4.getField(Field.Max_Demand_Period)
            if int(str_mdp) != MaxDemandPeriod.At_30_Minutes:
                self.assertEqual(False, True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetPulseInputRatioV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** Pulse ratio V4 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.request(), True)

            p1new = 34
            p2new = 93
            p3new = 87
            self.assertEqual(meterV4.setPulseInputRatio(Pulse.In1, p1new), True)
            self.assertEqual(meterV4.setPulseInputRatio(Pulse.In2, p2new), True)
            self.assertEqual(meterV4.setPulseInputRatio(Pulse.In3, p3new), True)
            self.assertEqual(meterV4.request(), True)
            str_pulse_1 = meterV4.getField(Field.Pulse_Ratio_1)
            str_pulse_2 = meterV4.getField(Field.Pulse_Ratio_2)
            str_pulse_3 = meterV4.getField(Field.Pulse_Ratio_3)
            self.assertEqual(str_pulse_1 == str(p1new), True)
            self.assertEqual(str_pulse_2 == str(p2new), True)
            self.assertEqual(str_pulse_3 == str(p3new), True)
            p1new = 121
            p2new = 343
            p3new = 454
            self.assertEqual(meterV4.setPulseInputRatio(Pulse.In1, p1new), True)
            self.assertEqual(meterV4.setPulseInputRatio(Pulse.In2, p2new), True)
            self.assertEqual(meterV4.setPulseInputRatio(Pulse.In3, p3new), True)
            self.assertEqual(meterV4.request(), True)
            str_pulse_1 = meterV4.getField(Field.Pulse_Ratio_1)
            str_pulse_2 = meterV4.getField(Field.Pulse_Ratio_2)
            str_pulse_3 = meterV4.getField(Field.Pulse_Ratio_3)
            self.assertEqual(str_pulse_1 == str(p1new), True)
            self.assertEqual(str_pulse_2 == str(p2new), True)
            self.assertEqual(str_pulse_3 == str(p3new), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetZeroResetV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** Test  resettable kwh v4"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.request(), True)
            str_rev_rst = meterV4.getField(Field.Resettable_Rev_kWh_Tot)
            str_rst = meterV4.getField(Field.Resettable_kWh_Tot)
            print "Inital: Fwd resettable = " + str_rst + "Rev resettable kwh " + str_rev_rst
            self.assertEqual(meterV4.setZeroResettableKWH(), True)
            self.assertEqual(meterV4.request(), True)
            str_rev_rst = meterV4.getField(Field.Resettable_Rev_kWh_Tot)
            str_rst = meterV4.getField(Field.Resettable_kWh_Tot)
            self.assertEqual(str_rev_rst == str(float(0)), True)
            self.assertEqual(str_rst == str(float(0)), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetScheduleTariffsV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        failed = False
        port = SerialPort(test_port, force_wait=wait)
        try:
            print"***** Test  set period times v4"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            param_buf =OrderedDict()
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
            self.assertEqual(meterV4.setScheduleTariffs(param_buf), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetScheduleTariffsV3(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** Test  set period times v3"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            param_buf =OrderedDict()
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
            self.assertEqual(meterV3.setScheduleTariffs(param_buf), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetSeasonSchedulesV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        failed = False
        port = SerialPort(test_port, force_wait=wait)
        try:
            print"***** Test  seasons v4"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
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
            self.assertEqual(meterV4.setSeasonSchedules(param_buf), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetHolidayDatesV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** Test  holidays v4"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            param_buf = OrderedDict()
            param_buf["Holiday_1_Month"] = 1
            param_buf["Holiday_1_Day"] = 1
            param_buf["Holiday_2_Month"] = 2
            param_buf["Holiday_2_Day"] = 3
            param_buf["Holiday_3_Month"] = 4
            param_buf["Holiday_3_Day"] = 4
            param_buf["Holiday_4_Month"] = 4
            param_buf["Holiday_4_Day"] = 5
            param_buf["Holiday_5_Month"] = 0
            param_buf["Holiday_5_Day"] = 0
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
            param_buf["Holiday_20_Month"] = 0
            param_buf["Holiday_20_Day"] = 0
            self.assertEqual(meterV4.setHolidayDates(param_buf), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetHolidayDatesV3(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** Test  holidays v3"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            param_buf = OrderedDict()
            param_buf["Holiday_1_Month"] = 1
            param_buf["Holiday_1_Day"] = 1
            param_buf["Holiday_2_Month"] = 2
            param_buf["Holiday_2_Day"] = 3
            param_buf["Holiday_3_Month"] = 4
            param_buf["Holiday_3_Day"] = 4
            param_buf["Holiday_4_Month"] = 4
            param_buf["Holiday_4_Day"] = 5
            param_buf["Holiday_5_Month"] = 0
            param_buf["Holiday_5_Day"] = 0
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
            param_buf["Holiday_20_Month"] = 0
            param_buf["Holiday_20_Day"] = 0
            self.assertEqual(meterV3.setHolidayDates(param_buf), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetSeasonSchedulesV3(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** Test  seasons v3"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
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
            self.assertEqual(meterV3.setSeasonSchedules(param_buf), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetMaxDemandPeriodV3(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print"***** Max Demand Period V3 Test"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV3 = V3Meter(v3_addr)
            meterV3.attachPort(port)
            self.assertEqual(meterV3.setMaxDemandPeriod(MaxDemandPeriod.At_15_Minutes), True)
            self.assertEqual(meterV3.request(), True)
            str_mdp = meterV3.getField(Field.Max_Demand_Period)
            if int(str_mdp) != MaxDemandPeriod.At_15_Minutes:
                self.assertEqual(False, True)
            self.assertEqual(meterV3.setMaxDemandPeriod(MaxDemandPeriod.At_30_Minutes), True)
            self.assertEqual(meterV3.request(), True)
            str_mdp = meterV3.getField(Field.Max_Demand_Period)
            if int(str_mdp) != MaxDemandPeriod.At_30_Minutes:
                self.assertEqual(False, True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetLcdV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        port = SerialPort(test_port, force_wait=wait)
        failed = False
        try:
            print "*****  Set LCD display V4  (manual check only)"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.request(), True)

            lcd_items = [LCDItems.RMS_Volts_Ln_1, LCDItems.Line_Freq]
            self.assertEqual(meterV4.setLCDCmd(lcd_items), True)
            if user_prompts:
                raw_input("*---------------------------------------------------*\n" +
                          "* Check Display, should be line 1 volts and line frequency. Press any key to continue." +
                          "\n*---------------------------------------------------*")

            lcd_items = [LCDItems.kWh_Ln_1]
            self.assertEqual(meterV4.setLCDCmd(lcd_items), True)
            if user_prompts:
                raw_input("*---------------------------------------------------*\n" +
                          " * Check Display, should be kwh line 1. Press any key to continue." +
                          "\n*---------------------------------------------------*")
            self.assertEqual(True, True)

        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testSetRelayV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        failed = False
        port = SerialPort(test_port, force_wait=wait)
        try:
            print "*****  Set Relay V4"
            ekm_set_log(ekm_print_log)
            self.assertEqual(port.initPort(), True)
            meterV4 = V4Meter(v4_addr)
            meterV4.attachPort(port)
            self.assertEqual(meterV4.request(), True)
            self.assertEqual(meterV4.setRelay(RelayInterval.Hold, Relay.Relay2, RelayState.RelayClose), True)
            self.assertEqual(meterV4.setRelay(RelayInterval.Hold, Relay.Relay1, RelayState.RelayClose), True)
            time.sleep(3)
            self.assertEqual(meterV4.setRelay(1, Relay.Relay1, RelayState.RelayOpen), True)
            self.assertEqual(meterV4.setRelay(1, Relay.Relay2, RelayState.RelayClose), True)
            time.sleep(3)
            self.assertEqual(meterV4.setRelay(RelayInterval.Hold, Relay.Relay2, RelayState.RelayOpen), True)
            self.assertEqual(meterV4.setRelay(RelayInterval.Hold, Relay.Relay1, RelayState.RelayOpen), True)
            self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())
        port.closePort()
        self.assertEqual(failed, False)

    def testReadWriteSettingsV4(self):
        wait, test_port , v3_addr, v4_addr, dbpath, user_prompts = loadparams()
        failed = False
        port = SerialPort(test_port, force_wait=wait)
        ekm_set_log(ekm_print_log)
        self.assertEqual(port.initPort(), True)
        try:
            for test_i in range(3):
                print("***********************************************")
                print "*****  Read and Write V4 Settings En Suite"
                # Prologue

                if test_i%2:
                    test_meter = V4Meter(v4_addr)
                else:
                    test_meter = V3Meter(v3_addr)
                print "Meter : " + test_meter.getMeterAddress()
                test_meter.attachPort(port)
                self.assertEqual(test_meter.request(), True)
                self.assertEqual(test_meter.readSettings(), True)
                print("***********************************************")
                print "Schedule".ljust(15) + "Tariff".ljust(15) + "Date".ljust(10) + "Rate".ljust(15)
                for schedule in range(Extents.Schedules):
                    for tariff in range(Extents.Tariffs):
                        schedule_tariff = test_meter.extractScheduleTariff(schedule, tariff)
                        print (("Schedule_" + schedule_tariff.Schedule).ljust(15) +
                                ("kWh_Tariff_" + schedule_tariff.Tariff).ljust(15) +
                                (schedule_tariff.Hour+":"+schedule_tariff.Min).ljust(10) +
                                (schedule_tariff.Rate.ljust(15)))
                print("***********************************************")
                for schedule in range(Extents.Schedules):
                    min_start = random.randint(0,49)
                    hr_start = random.randint(0,19)
                    rate_start = random.randint(1,7)
                    for tariff in range(Extents.Tariffs):
                        test_meter.assignScheduleTariff(schedule, tariff,
                                                     hr_start + tariff,
                                                     min_start + tariff,
                                                     rate_start + tariff)
                    test_meter.setScheduleTariffs()
                print("***********************************************")
                print("Month".ljust(7) + "kWh_Tariff_1".ljust(14) + "kWh_Tariff_2".ljust(14) + "kWh_Tariff_3".ljust(14) +
                        "kWh_Tariff_4".ljust(14) + "kWh_Tot".ljust(10) + "Rev_kWh_Tariff_1".ljust(18) +
                        "Rev_kWh_Tariff_2".ljust(18) + "Rev_kWh_Tariff_3".ljust(18) +
                        "Rev_kWh_Tariff_4".ljust(18) + "Rev_kWh_Tot".ljust(11))
                for month in range(Extents.Months):
                    md = test_meter.extractMonthTariff(month)
                    print(md.Month.ljust(7) + md.kWh_Tariff_1.ljust(14) + md.kWh_Tariff_2.ljust(14) +
                            md.kWh_Tariff_3.ljust(14) +  md.kWh_Tariff_4.ljust(14) + md.kWh_Tot.ljust(10) +
                            md.Rev_kWh_Tariff_1.ljust(18) + md.Rev_kWh_Tariff_2.ljust(18) +
                            md.Rev_kWh_Tariff_3.ljust(18) + md.Rev_kWh_Tariff_4.ljust(18) + md.Rev_kWh_Tot.ljust(10))
                print("***********************************************")
                test_meter.assignSeasonSchedule(Seasons.Season_1, 1, 1, Schedules.Schedule_1)
                test_meter.assignSeasonSchedule(Seasons.Season_2, 3, 21, Schedules.Schedule_2)
                test_meter.assignSeasonSchedule(Seasons.Season_3, 6, 20, Schedules.Schedule_3)
                test_meter.assignSeasonSchedule(Seasons.Season_4, 9, 21, Schedules.Schedule_8)
                test_meter.setSeasonSchedules()
                print("***********************************************")
                for holiday in range(Extents.Holidays):
                    day = random.randint(1,28)
                    mon = random.randint(1,12)
                    test_meter.assignHolidayDate(holiday, mon, day)
                test_meter.setHolidayDates()
                print("***********************************************")
                print("Holiday".ljust(12) + "Date".ljust(20))
                for holiday in range(Extents.Holidays):
                    holidaydate = test_meter.extractHolidayDate(holiday)
                    print(("Holiday_" + holidaydate.Holiday).ljust(12) +
                          (holidaydate.Month + "-" + holidaydate.Day).ljust(20))
                print("***********************************************")
                skeds = test_meter.extractHolidayWeekendSchedules()
                print "extracted holiday schedule = " + skeds.Holiday
                print "extracted weekend schedule = " + skeds.Weekend
                print("***********************************************")
                self.assertEqual(True, True)
        except:
            failed = True
            print traceback.format_exc(sys.exc_info())

        port.closePort()
        self.assertEqual(failed, False)
        pass


if __name__ == '__main__':
    unittest.main()

'''
Example for IronPython 2.7, SQL Server and ekmmeters
Tested with SQL Server 2014
(c) 2016 EKM Metering
'''

from ekmmeters import *
import importlib
import sys
import clr
clr.AddReference('System.Data')
from System.Data import *


class SqlServerMeterDB(MeterDB):
    def __init__(self, connection_string = ""):
        super(SqlServerMeterDB, self).__init__(connection_string)
        self.m_connection = ""
        SqlClient.SqlConnection(self.m_connection_string)

    def dbOpen(self):
        self.m_connection = SqlClient.SqlConnection(self.m_connection_string)
        self.m_connection.Open()

    def dbClose(self):
        self.m_connection.Close()

    def dbExec(self, query_str):
        try:
            action = SqlClient.SqlCommand(query_str, self.m_connection)
            reader = action.ExecuteReader()
            while reader.Read():
                ekm_log(reader[0])
            reader.Close()
            return True

        except:
            ekm_log(traceback.format_exc(sys.exc_info()))
            return False
        pass

def main():
    try:
        ekm_set_log(ekm_print_log)
        port = SerialPort("COM3", 9600)
        if not port.initPort():
            print "Cannot open port"
            return

        meterV4 = V4Meter("300001162")
        meterV4.attachPort(port)
        meterDB = SqlServerMeterDB()
        meterDB.setConnectString("Data Source=DESKTOP-0DI9R4D\SQLEXPRESS;Initial Catalog=my_reads;Integrated Security=True;")
        meterDB.dbOpen()
        meterDB.dbDropReads()
        meterDB.dbCreate()
        for i in range(10):
            if (meterV4.request()) :
                meterV4.insert(meterDB)
        meterDB.dbClose()
    except:
        print traceback.format_exc(sys.exc_info())

main()

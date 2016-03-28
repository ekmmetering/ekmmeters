'''
Example for IronPython 2.7 and ekmmeters
(c) 2016 EKM Metering
'''

from ekmmeters import *

import sys
#sys.path.append(r'C:\Python24\Lib')

import clr
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

from System.Drawing import Point
from System.Windows.Forms import Application, Button, Form, Label

class EKMSample(Form):

     def __init__(self):
         self.m_testport = 'COM3'  #: Port on test system
         self.m_test_meter = "300001162"     #: Test V4 meter
         ekm_set_log(ekm_print_log)
         print "\n****\nInitializing v3 and v4 for db test"

         self.Text = 'Sample EKM Iron Python App'

         self.label = Label()
         self.label.Text = "0.0"
         self.label.Location = Point(50, 50)
         self.label.Height = 30
         self.label.Width = 200

         self.count = 0

         button = Button()
         button.Text = "Read Meter: " + self.m_test_meter
         button.Location = Point(50, 100)
         button.Width = 180

         button.Click += self.buttonPressed

         self.Controls.Add(self.label)
         self.Controls.Add(button)

     def buttonPressed(self, sender, args):
        try:
            port = SerialPort(self.m_testport, 9600)
            meterV4 = V4Meter(self.m_test_meter)
            meterV4.attachPort(port)
            if port.initPort() == True:
                if meterV4.request() == True:
                    read_buf = meterV4.getReadBuffer()
                    meterV4.jsonRender(read_buf)
                    self.label.Text = read_buf["RMS_Volts_Ln_1"][MeterData.StringValue]
            port.closePort()
        except:
            print traceback.format_exc(sys.exc_info())
 

def main():

    form = EKMSample()
    Application.Run(form)

main()



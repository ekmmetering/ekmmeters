Unit Tests
----------

A very basic unit test framwork is avaliable in the Github project directory. It represents
the minimal level of compliance for check-in.

To use the  unit tests, you must update unittest.ini with your installed V3 and V4
meter addresses.  Both are required.  The serial port name is OS appropriate.  If you are
using an FTDI dongle, list ports to see what appears on insertion.

If you are learning the library, you will find very good coverage of library
functionality in the examples, and example code is an adaptation appropriate skeleton.
Unit test logic is built around unittests2, which provides the framework for execution
and largely dictates the pattern of error and port handling.

If you do choose to run the unit tests, you will need the ConifigParser, random
and unittest2 packages.


Unit Tests
----------

A very basic unit test framwork is avaliable in the Github project directory. It represents
the minimal level of compliance for check-in.

To use the  unit tests, you must update unittest.ini with your installed V3 and V4
meter addresses.  Both are required.  The serial port name is OS appropriate.  If you are
using an FTDI dongle, list ports to see what appears on insertion.

The unit tests also parameterize whether each serial commmand should pause after
completion, and for how long.  The default is 100ms, and you should not need to change
it.  Keep in mind your command is being sent as part of a series of 9600 baud exchanges
and the meter processor is quite slow: 100ms to insure serial buffer and interrupt handling
completes is a very small relative price.  In a well behaved serial driver in a flawless
environment, this number is not necessary. If it is useful, the fact will likely
only show up on repeated serial runs, where the meter is putting the most stress
it can on the UART and any oddness in the combination of drivers and hardware
will show up.  At the 100ms default, the unit tests complete in about 2 minues and 45
seconnds, most of which is blocking exchanges with the meter. At 50ms, the time
drops to about 2 minutes and ten seconds.  In most cases this is neither a necessary
or desirable optimization target.

If you are learning the library, you will find very good coverage of library
functionality in the examples, and example code is an adaptation appropriate skeleton.
Unit test logic is built around unittests2, which provides the framework for execution
and largely dictates the pattern of error and port handling.

If you do choose to run the unit tests, you will need the ConifigParser, random
and unittest2 packages.


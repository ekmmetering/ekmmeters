# ekmmeters
A Python Serial API for EKM Omnimeters

The purpose of this library is to provide a reliable and flexible interface
to EKM version 3 and version 44 Omnnimeters.  It is written to be compatible with existing
EKM field naming conventions and to be accessible to both the casual user --
who may not know Python well and simply wishes to script his or her meter --
and the experienced user who is creating a device agent to manage an
attached meter.

All calls except change meter number are provided, as are all constants for making meter
settings and retrieving data.

The software is provided under an MIT License.  
(c) 2015, 2016 EKM Metering, as appropriate.

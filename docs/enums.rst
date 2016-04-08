Constants
---------

Every protocol has a range of irreduible and necessary values.  This library
uses a simple static class variable, in the approximate style of the C++
enum, to encapsulate and describe the full set of required values.

.. currentmodule:: ekmmeters
.. toctree::
   :maxdepth: 1

Settings
********

Values used primarily (but not exclusively) for serial settings parameters.

.. autoclass:: MaxDemandResetInterval

.. autoclass:: MaxDemandPeriod

.. autoclass:: LCDItems

.. autoclass:: CTRatio

.. autoclass:: Pulse

.. autoclass:: PulseOutput

.. autoclass:: Relay

.. autoclass:: RelayState

.. autoclass:: RelayInterval

Serial Block
************

Values established when a SerialBlock is initialized.

.. autoclass:: MeterData

.. autoclass:: Field

.. autoclass:: ScaleType

.. autoclass:: FieldType

Meter
*****

Values used to select meter object buffers to operate on.  V4 and V3 Omnimeters.

.. autoclass:: ReadSchedules

.. autoclass:: ReadMonths

Data
****

Values which only appear in a read.  V4 Omnimeters.

.. autoclass:: DirectionFlag

.. autoclass:: ScaleKWH

.. autoclass:: StateIn

.. autoclass:: StateOut

Traversal
*********

Values primarily (but not exclusively) used for extraction from or assignment
to serial buffers.  V3 and V4 Omnimeters.

.. autoclass:: Extents

.. autoclass:: Seasons

.. autoclass:: Months

.. autoclass:: Tariffs

.. autoclass:: Schedules


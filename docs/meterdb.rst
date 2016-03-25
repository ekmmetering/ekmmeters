MeterDB Class
-------------

The MeterDb and SqliteMeterDB classes are designed as a helper for the simplest
use case: read a meter and save the measurements. A SQL Server descendant class
for Iron Python can also be found in the examples.

If you are using this library to write data to an existing program with an ORM
such as SQLAlchemy, do not use these classes: extract the data and load to an appropriate object.

Most users of MeterDB will employ an existing subclass (like SqliteMeterDB). Overriding MeterDB is
specifically for simple use cases, where overriding between one and five queries (create, insert,
drop, and 2 index creates) is more approachable than setting up or learning an ORM.

.. currentmodule:: ekmmeters
.. toctree::
   :maxdepth: 1
.. autoclass:: MeterDB
    :members:  setConnectString, mapTypeToSql, fillCreate, sqlCreate, sqlInsert, sqlIdxMeterTime,sqlIdxMeter,sqlDrop,dbInsert,dbCreate,dbDropReads,dbExec
.. autoclass:: SqliteMeterDB
    :members:  dbExec, renderJsonReadsSince, renderRawJsonReadsSince

Introduction
------------

.. currentmodule:: ekmmeters
.. toctree::
   :maxdepth: 1

Getting Started
^^^^^^^^^^^^^^^

For most users, the most effective way to get started is by working through the 
examples with a live Omnimeter. Most of what this API does is very straightforward, 
and the examples are written to easily adapt.

It is generally quite difficult to come to terms with a new library (and perhaps
a new language) while wrestling with serial connectivity issues.  The trial
version of EKM Dash is recommended as a way to easily insure your meters are
properly connected.

The library offers two modes of data access: via dictionaries and via simpler
assign* and extract* calls.  Unless you are writing a dedicated device agent
which must handle JSON or XML, the assign and extract methods are strongly
recommended, both for ease of use and readability.

Goals
*****

The purpose of this library is to provide a reliable and flexible interface
to EKM v3 and v4 Omnnimeters.  It is written to be compatible with existing
EKM field naming conventions and to be accessible to both the casual user --
who may not know Python well and simply wishes to script his or her meter --
and the experienced user who is creating a device agent for an enterprise
metering solution.

The library is written to completely encapsulate the required constants and
enumerations for meter control, in a form which is friendly to intellisense
style editors and Sphinx documentation.  The adopted idiom is simple
classes with static members for each categorically unique value.

PEP 8 Note
**********

An implication of the use of EKM naming is that StudlyCase,
used widely in existing EKM products, is employed in preference to all lower
case function names in PEP 8.  Function names keep this vocabulary intact
in camelCase.   In a (relatively few) cases, descriptive names or tabular
presentation was held more important than line length, but in every case 
the library uses the PyCharm/IntelliJ 120 column lint default.
These were implementation choices for an application-domain library,
and no changes are planned at this time.

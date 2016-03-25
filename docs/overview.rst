Introduction
------------

.. currentmodule:: ekmmeters
.. toctree::
   :maxdepth: 1

Getting Started
^^^^^^^^^^^^^^^

The best way to get started with the library is by trying the provided examples section.

Users writing device agents may wish to read through the unit test code as well.

It is generally quite difficult to come to terms with a new library, and perhaps
a new language, while wrestling with serial connectivity issues.  The trial
version of EKM Dash is recommended as a way to easily insure your meters are
properly connected.

The library offers two modes of data access: via dictionaries and via simpler
assign* and extract* calls.  Unless you are writing a dedicated device agent
which must handle JSON or XML, the assign and extract methods are strongly
recommended, both for ease of use and readability.

Goals
^^^^^

The purpose of this library is to provide a reliable and flexible interface
to EKM v3 and v4 Omnnimeters.  It is written to be compatible with existing
EKM field naming conventions and to be accessible to both the casual user
who may not know Python well and simply wishes to script his or her meter,
and the experienced user who is creating a device agent to manage an
attached meter.

The library is written to completely encapsulate the required constants and
enumerations for meter control, in a form which is friendly to intellisense
style editors and Sphinx documentation.  The adopted idiom is simple
classes with static members for each categorically unique value.

An implication of the use of EKM naming is that camelCase and StudlyCase,
used widely in existing EKM products, are used in preference to all lower
case function names in PEP 8.

To support users who may only be using Python for one meter-related script,
and for readability, assign* and extract* functions are provided for safe
and simple iteration and setting of serial call parameters.  Users creating
device agents which must push data over the wire can set and recall every
required buffer as a python dictionary.

Background
^^^^^^^^^^

This library began life as reference implementation for a new EKM device agent.
As such, the original code underwent many thousands of hours of test.  The changes
made to open source the library include simplified buffer access and what we hope
is enough documentation to use the API effectively.  While there are many more things
which might be desirabe -- from full PEP 8 compliance to object decorators -- we've
chosen to put test depth first.

While we expect (and welcome) bug reports, this is the terminal release unless the
2.x branch of Python increments.  The V4 and V3 Omnimeter protocols share a great deal,
and future products may or may not have their DNA.  There are no significant ommitted
serial calls, and we work in Python across OS X, Windows (including Iron Python),
and Linux.  So while small features may be added, and bugs will certainly be fixed,
this interface should remain largely unchanged.






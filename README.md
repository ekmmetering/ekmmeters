#ekmmeters 0.10

Python API for the EKM Omnimeter Serial Interface

The goal of this library is to provide a reliable and flexible interface to version 3 and version 4 EKM Omnnimeters.  The library is written to be compatible with existing EKM field naming conventions and to be accessible to both the casual and experienced user.  You should not need to have more than a few hours of Python 2.x experience to write a script for any Omnimeter command.  

More experienced Python users will find appropriate methods for writing agents to store data, manage meter settings, and act as the client in publish/subscribe systems.  The library  supports standard Python serialization with queue and multiprocessing modules, all ingoing and outgoing buffers are avaliable in JSON-friendly dictionary objects, and a smalll automated unit test framework provides simplest-possible coverage of all supported commands.  

The API was written and tested using Python 2.6 under CentOS 6.x, and using Python 2.7x, including Iron Python on .NET.  The library is a single file and pure Python.  You can install with "pip ekmmeters" or download ekmmeters.py and place it in your project directory.  There are no external dependencies beyond the pypi packages json, collections, and pyserial.

Unit tests require the unittests2 pypi package.  The documentation for readthedocs.org was built under Sphinx 1.35.  It can be built locally with the sphinx_rtd_theme pypi package installed.

There is no required third party tool set for editing the library.  However, Pycharm 5.04 was used for development and the project xml is included as a convenience in the .idea directory.  Naming conventions and idioms are designed to support intellisense-style drop-downs, and using an editor with the feature can be a good learning tool and and convenience with this  library.

The software is provided under an MIT License.  The MIT license allows you to use this library for any personal or commercial project, without an obligation to release any of your work as open source.   

(c) 2015, 2016 EKM Metering, as appropriate.

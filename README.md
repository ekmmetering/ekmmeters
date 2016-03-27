#ekmmeters 0.10

Python API for the EKM Omnimeter Serial Interface

The goal of this library is to provide a reliable and flexible interface to version 3 and version 4 EKM Omnnimeters.  The library is written to be compatible with existing EKM field naming conventions and to be accessible to both the casual and experienced user.  You should not need to have more than a few hours of Python 2.x experience to write a script for any Omnimeter command or create a short program to store your reads in a database.

More experienced Python users will find appropriate methods to support agents agents which store data locally or in the cloud, manage meter settings, and act as the client in publish/subscribe systems.  The library  supports standard Python serialization with Python 2.x multiprocessing and queueing, all ingoing and outgoing buffers are avaliable in JSON-friendly dictionary objects, and a smalll automated unit test framework provides simplest-possible coverage of all supported commands.  

The API was written and tested using Python 2.6 under CentOS 6.x, and using Python 2.7x on OSX, Windows, and Linux, including Iron Python on .NET.  The library is a single file and pure Python.  You can install with "pip ekmmeters" or download ekmmeters.py and place it in your project directory.  There are no external dependencies beyond the pypi packages json, collections, and pyserial.

Unit tests require the unittests2 pypi package, along with random and ConfigParser.  The documentation for readthedocs.org was built under Sphinx 1.35. Google style docstrings are used exclusively, and read via the Sphinx napoleon extension.  Docs can be built locally with the sphinx_rtd_theme pypi package installed.

There are three specific and chosen PEP 8 violations.  Constant and static names which refer to Omnimeter entities, in keeping with EKM naming in other systems, are in StudlyCase. Method names preserve the same naming convention in camelCase.  And -- while every attempt was made to keep column length under 80 columns, in cases where WYSIWYG naming conflicted, descriptive names won.  However, the PyCharm PEP lint setting of 120 columns is observed in every case.

There is no required third party tool set for editing the library.  However, Pycharm 5.04 was used for development and the project xml is included as a convenience in the .idea directory.  The library is designed to encapsulate all meter constants, limits, and field names. An editor with intellisense style drop downs (any such editor) may be helpful. 

The software is provided under an MIT License.  The MIT license allows you to use this library for any personal or commercial project, without an obligation to release any of your work as open source.   

(c) 2015, 2016 EKM Metering, as appropriate.

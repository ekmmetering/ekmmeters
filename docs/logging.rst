Logs and Exceptions
-------------------

.. currentmodule:: ekmmeters
.. toctree::
   :maxdepth: 1

Logging
^^^^^^^

The ekmmeters module uses module level logging via predefined callback.  It is off by default.

Simple print logging is turned on with::

    ekm_set_log(ekm_print_log)

We *strongly* recommend leaving this on while getting started.

The logging is turned off with::

    ekm_set_log(ekm_no_log)

You can send the output to file or syslog or other destination with a
custom callback.  A custom callback must be of the form::

    def my_logging_function(string_out):
        # simplest case: print or log
        print(string_out)

The callback is set -- exactly as above -- via set_log(function_name)::

    set_log(my_logging_function)

Exceptions
^^^^^^^^^^

Every logging and exception system suggests its own strategy.  In this library,
serial sets and reads, which rely on a connected meter, will
trap exceptions broadly, return False, and log the result.  Most other methods
will simply allow exceptions to percolate up, for best handling by the
caller without reinterpretation.


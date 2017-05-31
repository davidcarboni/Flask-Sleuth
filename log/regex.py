"""Regular expressions defining a common logging standard

 This file contains regex values and parsing code that define a logging standard which all components should meet,
 independent of implementation technology.

 The aim is to create a common language, with minimal variation, which can be understood by the log processing
 system(s).

"""
import re

# Example Spring Boot log line:
# 2017-05-22 09:42:55.680  WARN
# 9730 --- [           main] o.s.b.a.e.mvc.EndpointHandlerMapping     : Lorem ipsum...
#
# Example Python log line:
# 2017-05-22 09:42:55,680  WARNING
# 9730 --- [           main] o.s.b.a.e.mvc.EndpointHandlerMapping     : Lorem ipsum...

# Example Spring Boot log line with added Spring Cloud Sleuth transaction information:
# 2017-05-22 09:42:55.680  INFO [hello-world,a82ac73c9c001176,a82ac73c9c001176,false]
# 9730 --- [           main] o.s.b.a.e.mvc.EndpointHandlerMapping     : Lorem ipsum...
#
# Example Python log line with added transaction information:
# 2017-05-22 09:42:55,680  INFO [hello-world,a82ac73c9c001176,a82ac73c9c001176,false]
# 9730 --- [           main] o.s.b.a.e.mvc.EndpointHandlerMapping     : Lorem ipsum...


# 2017-05-22 09:42:55.680
date_time = '(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}[\.,]\d{3})'

# Spring:           ERROR, WARN,    INFO, DEBUG, TRACE
# Python: CRITICAL, ERROR, WARNING, INFO, DEBUG
log_level = '(CRITICAL|ERROR|WARN(ING)?|INFO|DEBUG|TRACE)'

# Transaction tracing information (optional)
transaction_info = '(\[([^,^\]]*),([^,^\]]*),([^,^\]]*),([^\]]*)\])?'

# 9730
process_id = '(\d{1,5})'

# ---
separator = '---'

# [           main]
thread_name = '\[\s*([^\]]+)\]'

# o.s.b.a.e.mvc.EndpointHandlerMapping
logger_name = '([\S]+)'

# Lorem ipsum...
log_message = '(.*)'

# All together now
regex = date_time + '\s+' + log_level + '\s+' + transaction_info + '\s*' + process_id + '\s+' + \
        separator + '\s+' + thread_name + '\s+' + logger_name + '\s+:\s+' + log_message

# Regex match group indices

# Default fields
DATE_TIME = 1
LOG_LEVEL = 2
PROCESS_ID = 9
THREAD_NAME = 10
LOGGER_NAME = 11
LOG_MESSAGE = 12

# Optional transaction information
TRANSACTION = 4
TRANSACTION_APP = 5
TRANSACTION_ID = 6
TRANSACTION_SPAN = 7
TRANSACTION_EXPORTED = 8


def parse(line):
    """
    Parses a log line using the regexices above.
    :param line: A log line to be parsed.
    :return: If no match is found, None, otherwise a dict containing the values parsed from the log line.
    """
    values = None
    matches = re.search(regex, line)
    if matches:

        # Standard values
        values = {
            'date_time': matches.group(DATE_TIME),
            'log_level': matches.group(LOG_LEVEL),
            'process_id': matches.group(PROCESS_ID),
            'thread_name': matches.group(THREAD_NAME),
            'logger_name': matches.group(LOGGER_NAME),
            'log_message': matches.group(LOG_MESSAGE)
        }

        # Optional transaction tracking information
        if matches.group(TRANSACTION):
            values["transaction"] = {
                "app": matches.group(TRANSACTION_APP),
                "id": matches.group(TRANSACTION_ID),
                "span": matches.group(TRANSACTION_SPAN),
                "exported": matches.group(TRANSACTION_EXPORTED)
            }

    return values


if __name__ == '__main__':
    # Print out the complete regex for convenience
    print(regex)

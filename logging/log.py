import os
from threading import current_thread
import datetime
import re
import json

# Example Spring Boot log line:
# 2017-05-22 09:42:55.680  INFO 9730 --- [           main] o.s.b.a.e.mvc.EndpointHandlerMapping     : Lorem ipsum...

# 2017-05-22 09:42:55.680
_date_time = '(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3})'

# INFO
_log_level = '(\w+)'

# Transaction tracing information (optional)
_transaction = '(\[([^,^\]]*),([^,^\]]*),([^,^\]]*),([^\]]*)\])?'

# 9730
_process_id = '(\d+)'

# ---
_separator = '---'

# [           main]
_thread_name = '\[\s*([^\]]+)\]'

# o.s.b.a.e.mvc.EndpointHandlerMapping
_logger_name = '([\S]+)'

# Lorem ipsum...
_log_message = '(.*)'

# All together now
regex = _date_time + '\s+' + _log_level + '\s+' + _transaction + '\s*' + _process_id + '\s+' + \
        _separator + '\s+' + _thread_name + '\s+' + _logger_name + '\s+:\s+' + _log_message

print(regex)

# Regex match groups
DATE_TIME = 1
LOG_LEVEL = 2
TRANSACTION = 3
TRANSACTION_APP = 4
TRANSACTION_ID = 5
TRANSACTION_SPAN = 6
TRANSACTION_EXPORTED = 7
PROCESS_ID = 8
THREAD_NAME = 9
LOGGER_NAME = 10
LOG_MESSAGE = 11


def error(log_level, logger_name, log_message):
    _log(log_level, logger_name, log_message, "ERROR")


def warn(log_level, logger_name, log_message):
    _log(log_level, logger_name, log_message, "WARN")


def info(log_level, logger_name, log_message):
    _log(log_level, logger_name, log_message, "INFO")


def debug(log_level, logger_name, log_message):
    _log(log_level, logger_name, log_message, "DEBUG")


def trace(log_level, logger_name, log_message):
    _log(log_level, logger_name, log_message, "TRACE")


def _field(value, width, right_justify=True):
    """Right-justifies the given value in a field of the given width, padding with spaces, or trimming, as needed."""
    # Adjust the thread name to 15 characters
    if len(value) > width:
        return value[0:width]
    else:
        if right_justify:
            return value.rjust(width)
        else:
            return value.ljust(width)


def _log(log_level, logger_name, log_message, transaction=None):
    """Generates a log message in a format close enough to Spring Boot that it will pass the regex."""
    # Truncate date-time to milliseconds to match Spring Boot format
    date_time = datetime.datetime.now().isoformat(' ', 'milliseconds')
    if not log_level:
        log_level = "INFO"
    process_id = str(os.getpid())
    thread_name = current_thread().getName()
    if not logger_name:
        logger_name = thread_name

    # Adjust field widths as needed
    log_level = _field(log_level, 5)
    thread_name = "[" + _field(thread_name, 15) + "]"
    logger_name = _field(logger_name, 40, right_justify=False)

    # Add transaction information, if present
    transaction_detail = None
    if transaction:
        transaction_fields = []
        for key in ("app", "id", "span", "exported"):
            if transaction[key]:
                transaction_fields.append(transaction[key])
            else:
                transaction_fields.append("")
        transaction_detail = "[" + ",".join(transaction_fields) + "]"

    # Assemble the set of columns to be rendered in the log message
    columns = [date_time, log_level]
    if transaction_detail:
        columns += [transaction_detail]
    columns += [process_id, _separator, thread_name, logger_name, ":", log_message]

    return " ".join(columns)


if __name__ == '__main__':
    # Test out with a few lines in tests/log.txt
    lines = [line.rstrip('\n') for line in open('tests/log.txt')]
    for line in lines:
        matches = re.search(regex, line)
        if matches:
            # print(">>> " + str(matches.groups()))

            # Expected values
            values = {
                'date_time': matches.group(DATE_TIME),
                'log_level': matches.group(LOG_LEVEL),
                'process_id': matches.group(PROCESS_ID),
                'thread_name': matches.group(THREAD_NAME),
                'logger_name': matches.group(LOGGER_NAME),
                'log_message': matches.group(LOG_MESSAGE)[:100] + "..."
            }

            # Optional transaction tracking information
            transaction = None
            if matches.group(TRANSACTION):
                values["transaction"] = {}
                values["transaction"]["app"] = matches.group(TRANSACTION_APP)
                values["transaction"]["id"] = matches.group(TRANSACTION_ID)
                values["transaction"]["span"] = matches.group(TRANSACTION_SPAN)
                values["transaction"]["exported"] = matches.group(TRANSACTION_EXPORTED)
                transaction = values["transaction"]

            print()
            print("Log line values: " + json.dumps(values))
            print("---")
            print("Original      : " + line[:170] + "...")
            reconstructed = _log(values['log_level'], values['logger_name'], values['log_message'], transaction)
            print("Reconstructed : " + reconstructed)
        else:
            print("Failed to match log line: " + str(line))

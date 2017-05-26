import unittest
import os
import re

import unittest

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()


# Example Spring Boot log line:
# 2017-05-22 09:42:55.680  INFO 9730 --- [           main] o.s.b.a.e.mvc.EndpointHandlerMapping     : Lorem ipsum...

# 2017-05-22 09:42:55.680
_date_time = '(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})'

# INFO
_log_level = '(\w+)'

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
regex = _date_time + '\s+' + _log_level + '\s+' + _process_id + '\s+' + _separator + '\s+' + \
        _thread_name + '\s+' + _logger_name + '\s*:\s+' + _log_message

# Regex match groups
DATE_TIME = 1
LOG_LEVEL = 2
PROCESS_ID = 3
THREAD_NAME = 4
LOGGER_NAME = 5
LOG_MESSAGE = 6


def match(line):
    return re.search(regex, line)


def field(value, width, right_justify=True):
    """Right-justifies the given value in a field of the given width, padding with spaces, or trimming, as needed."""
    # Adjust the thread name to 15 characters
    if len(value) > width:
        return value[0:width]
    else:
        if right_justify:
            return value.rjust(width)
        else:
            return value.ljust(width)


def message(log_level, logger_name, log_message):
    """Generates a log message in a format close enough to Spring Boot that it will pass the regex."""
    # Truncate date-time to milliseconds to match Spring Boot format
    date_time = datetime.datetime.now().isoformat(' ', 'milliseconds')
    if not log_level:
        log_level = "INFO"
    process_id = os.getpid()
    thread_name = current_thread().getName()
    if not logger_name:
        logger_name = thread_name

    # Adjust field widths as needed
    log_level = field(log_level, 5)
    thread_name = "[" + field(thread_name, 15) + "]"
    logger_name = field(logger_name, 40, right_justify=False)

    return " ".join(
        (date_time, log_level, str(process_id), _separator, thread_name, logger_name, ":", log_message))


if __name__ == '__main__':
    f = open('tests/log.txt')
    s = f.read()
    print(s)
    matches = match(s)
    print(matches.group(0))

def foo():
    # Test out with a few lines in log.txt
    lines = [line.rstrip('\n') for line in open('tests/log.txt')]
    for line in lines:
        matches = match(line)
        if matches:
            values = {
                'date_time': matches.group(DATE_TIME),
                'log_level': matches.group(LOG_LEVEL),
                'process_id': matches.group(PROCESS_ID),
                'thread_name': matches.group(THREAD_NAME),
                'logger_name': matches.group(LOGGER_NAME),
                'log_message': matches.group(LOG_MESSAGE)[:100] + "..."
            }
            print()
            print("Log line values: " + json.dumps(values))
            print("---")
            print("Original      : " + line[:170] + "...")
            reconstructed = message(values['log_level'], values['logger_name'], values['log_message'])
            print("Reconstructed : " + reconstructed[:170] + "...")
        else:
            print("Failed to match log line: " + str(line))

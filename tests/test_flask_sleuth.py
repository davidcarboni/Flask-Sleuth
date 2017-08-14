import unittest

from flask import Flask
import sleuth
import b3
from datetime import datetime
from logging import Formatter
import time
import os
from threading import current_thread


class TestStringMethods(unittest.TestCase):
    def test_should_update_record(self):
        # Given
        # A mock LogRecord
        created = time.time()
        levelname = "WARNING"
        name = "This is a logger name which is more that forty characters long"
        record = MockLogRecord(created, levelname, name)
        dt = datetime.fromtimestamp(time.time())

        # When
        # We update the record
        sleuth._update_record(record)

        # Then
        # The added fields should be as expected - and no tracing information
        # str(datetime) is "2017-08-14 17:54:04.594704" - we're expecting milliseconds, which may
        # be rounded up or dow from microseconds, so we use the millisecond value from record.asctime
        self.assertEqual(record.springtime, str(dt)[:-6] + record.asctime[-3:])
        self.assertEqual(record.levelname_spring, "WARN")
        self.assertEqual(record.process_id, str(os.getpid()))
        self.assertEqual(record.thread_name, (current_thread().getName())[:15])
        self.assertEqual(record.logger_name, record.name[:40])
        self.assertEqual(record.tracing_information, "")

    def test_should_add_tracing_information(self):
        # Given
        with Flask("tracing").app_context():
            # A mock LogRecord and B3 tracing information
            created = time.time()
            levelname = "INFO"
            name = "Logger name"
            record = MockLogRecord(created, levelname, name)
            dt = datetime.fromtimestamp(time.time())
            b3.start_span()
            values = b3.values()

            # When
            # We update the record
            sleuth._update_record(record)

            # Then
            # We should get tracing information
            self.assertTrue(record.tracing_information)
            # "[test,ba580718aefa94b9,ba580718aefa94b9,false] "
            fields = record.tracing_information.strip()[1:-1].split(",")
            self.assertEqual(fields[0], "tracing")
            self.assertEqual(fields[1], values[b3.b3_trace_id])
            self.assertEqual(fields[2], values[b3.b3_span_id])
            self.assertEqual(fields[3], "false")


class MockLogRecord:
    def __init__(self, created, levelname, name):
        # Set up the fields required by Formatter.formatTime()
        self.created = created
        self.msecs = int(str("%.3f" % self.created)[-3:])

        # Use Formatter.formatTime() to get the exact String representation of that Python uses by default
        self.asctime = Formatter().formatTime(self)

        # Other expected values
        self.levelname = levelname
        self.name = name


if __name__ == '__main__':
    unittest.main()

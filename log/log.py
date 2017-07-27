import os
from threading import current_thread
import logging
from flaskb3 import b3
from flask import Flask

# Set up the log format

LOG_FORMAT = '%(asctime)s %(levelname)+5s %(tracing_information)s' \
             '%(process_id)s --- [%(thread_name)+15s] %(logger_name)-40s : %(message)s'
logging.basicConfig(format=LOG_FORMAT)
_app_name = "Please call init(app)"


def _tracing_information(app_name):
    """Gets B3 distributed tracing information, if available, in Spring Cloud Sleuth compatible format."""

    # We'll collate trace information if the B3 headers have been collected:
    values = b3.values()
    if values[b3.b3_trace_id]:

        # Trace information would normally be sent to Zipkin if either of sampled or debug ("flags") is set to 1
        # However we're not currently using Zipkin, so it's always false
        # exported = "true" if values[b3.b3_sampled] == '1' or values[b3.b3_flags] == '1' else "false"

        return [
            app_name if app_name else " - ",
            values[b3.b3_trace_id],
            values[b3.b3_span_id],
            "false",
        ]

    return []

# Update the logging record factory:

record_factory = logging.getLogRecordFactory()


def spring_factory(*args, **kwargs):
    """Collates values needed by LOG_FORMAT to implement the logging standard.

    :return: A log record augmented with the values required by LOG_FORMAT:
     * process_id
     * thread_name
     * logger_name
     * tracing_information (if B3 values have not been collected this will be an empty string)
    """
    record = record_factory(*args, **kwargs)

    # Standard information
    record.process_id = str(os.getpid())
    record.thread_name = (current_thread().getName())[:15]
    record.logger_name = record.name[:40]

    # Optional distributed tracing information
    record.tracing_information = ""
    tracing_information = _tracing_information(_app_name)
    if tracing_information:
        record.tracing_information = "[" + ",".join(tracing_information) + "] "

    return record


logging.setLogRecordFactory(spring_factory)


def init(app):
    """Initialises logging with the name of the app"""
    global _app_name
    _app_name = app.name

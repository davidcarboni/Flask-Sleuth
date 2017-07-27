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


def extra(logger, app_name=None):
    """Generates log values needed to match the logging standard.

    This should you to call logging as follows:

     * logger.debug("Ohai Mr Lolcat", extra=extra(logger))

    :param logger: The logger you're using to generate a message. This is used for the logger name.
    :param app_name: This is optional. It should normally be set once at startup by calling init(app)
    :return: A dict of the values required by LOG_FORMAT.
    """
    values = {
        'process_id': str(os.getpid()),
        'thread_name': (current_thread().getName())[:15],
        'logger_name': logger.name[:40],
        'tracing_information': '',
    }

    # Add transaction information, if present
    tracing_information = _tracing_information(app_name or _app_name)
    if tracing_information:
        values['tracing_information'] = "[" + ",".join(tracing_information) + "] "

    return values


def init(app):
    """Initialises logging with the name of the app"""
    global _app_name
    _app_name = app.name

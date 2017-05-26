import os
from threading import current_thread
import datetime
import log.regex


def error(log_level, logger_name, log_message, transaction=None):
    # Log an error message
    _log(log_level, logger_name, log_message, "ERROR", transaction)


def warn(log_level, logger_name, log_message, transaction=None):
    # Log a warning message
    _log(log_level, logger_name, log_message, "WARN", transaction)


def info(log_level, logger_name, log_message, transaction=None):
    # Log an information message
    _log(log_level, logger_name, log_message, "INFO", transaction)


def debug(log_level, logger_name, log_message, transaction=None):
    # Log a debug message
    _log(log_level, logger_name, log_message, "DEBUG", transaction)


def trace(log_level, logger_name, log_message, transaction=None):
    # Log a trace message
    _log(log_level, logger_name, log_message, "TRACE", transaction)


def transaction_info(app_name, transaction_id, transaction_span=None, exported=False):
    """ Constructs a dict of transaction information.
    The defaults for Spring appear to be:
     * If spring.app.name is missing, " - " is used
     * If there's a transaction ID, but no span ID, the span ID is the same as the transaction ID
     * Exported defaults to false
    """
    return {
        'app': app_name if app_name else " - ",
        'id': transaction_id,
        'span': transaction_span if transaction_span else transaction_id,
        'exported': "true" if exported else "false"
    }


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
    """Generates a log message in a format to match Spring Boot / Sleuth."""
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
    columns += [process_id, log.regex.separator, thread_name, logger_name, ":", log_message]

    return " ".join(columns)

import os
from threading import current_thread
import logging
from log import regex

# Set up the log format

LOG_FORMAT = '%(asctime)s %(levelname)+5s %(transaction_detail)s' \
             '%(process_id)s --- [%(thread_name)+15s] %(logger_name)-40s : %(message)s'
logging.basicConfig(format=LOG_FORMAT)


def _exported(transaction_id, exported):
    """ Works out the correct value for the "exported" field of the transaction information.
    NB it's only populated if there's a transaction ID.
    """
    if transaction_id:
        # Ensure if the string "false" is passed in we return "false"
        if exported and exported != "false":
            return "true"
        else:
            return "false"
    return ""


def _transaction_info(transaction):
    """ Constructs a dict from the given transaction information.
    The defaults for Spring appear to be:
     * If spring.app.name is missing, " - " is used
     * If there's a transaction ID, but no span ID, the span ID is the same as the transaction ID
     * Exported defaults to false
    The keys expected in the input dict are app_name, transaction_id, transaction_span and exported.
    """

    if transaction:
        # Get raw values
        app_name = transaction.get("app")
        transaction_id = transaction.get("id")
        transaction_span = transaction.get("span")
        exported = transaction.get("exported")

        # Adjust as needed
        return {
            'app': app_name if app_name else " - ",
            'id': transaction_id,
            'span': transaction_span if transaction_span else transaction_id,
            'exported': _exported(transaction_id, exported)
        }


def _standard_info(logger=None):
    """ Constructs a dict of standard log information.
    This includes:
     * Process ID
     * Thread name
     * Logger name (if no logger is provided, this defaults to __name__)
    """

    return {
        'process_id': str(os.getpid()),
        'thread_name': (current_thread().getName())[:15],
        'logger_name': (logger.name if logger else __name__)[:40]
    }


def extra(logger=None, transaction=None):
    """Generates log values needed to match the logging standard.
    the logger name defaults to __name__ """
    info = _standard_info(logger)
    transaction_detail = _transaction_info(transaction)

    # Add transaction information, if present
    if transaction_detail:
        transaction_info = []
        for key in ("app", "id", "span", "exported"):
            value = transaction_detail.get(key)
            if value:
                transaction_info.append(value)
            else:
                transaction_info.append("")
        info['transaction_detail'] = "[" + ",".join(transaction_info) + "] "
    else:
        info['transaction_detail'] = ""

    return info

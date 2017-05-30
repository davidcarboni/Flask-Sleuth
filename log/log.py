import os
from threading import current_thread
import datetime
import logging
import json
import regex
from datetime import datetime


# Example Spring Boot log line:
# 2017-05-22 09:42:55.680  INFO
# 9730 --- [           main] o.s.b.a.e.mvc.EndpointHandlerMapping     : Lorem ipsum...

# Example log line with added Spring Cloud Sleuth:
# 2017-05-22 09:42:55.680  INFO [hello-world,a82ac73c9c001176,a82ac73c9c001176,false]
# 9730 --- [           main] o.s.b.a.e.mvc.EndpointHandlerMapping     : Lorem ipsum...


def error(logger_name, message, transaction=None):
    # Log an error message
    extra = _log_info(logger_name, transaction)
    logging.getLogger(logger_name).error(message, extra=extra)


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


def transaction_info(app_name=None, transaction_id=None, transaction_span=None, exported=False):
    """ Constructs a dict of transaction information.
    The defaults for Spring appear to be:
     * If spring.app.name is missing, " - " is used
     * If there's a transaction ID, but no span ID, the span ID is the same as the transaction ID
     * Exported defaults to false
    """
    # Work out a value for the "exported" field
    # It's only populated if there's a transaction ID
    exported_string = None
    if transaction_id:
        exported_string = "true" if exported and exported != "false" else "false"

    return {
        'app': app_name if app_name else " - ",
        'id': transaction_id,
        'span': transaction_span if transaction_span else transaction_id,
        'exported': exported_string
    }


def extra(logger, transaction=None):
    """Generates log values needed to match Spring Boot / Sleuth.
    the logger name defaults to """
    values = {}
    # Truncate date-time to milliseconds to match Spring Boot format
    # values['date_time'] = datetime.datetime.now().isoformat(' ', 'milliseconds')
    values['millisecond'] = str(datetime.now().microsecond)[0:3]
    values['process_id'] = str(os.getpid())
    values['thread_name'] = current_thread().getName()
    values['logger_name'] = logger.name

    # Add transaction information, if present
    if transaction:
        transaction_fields = []
        for key in ("app", "id", "span", "exported"):
            if key in transaction and transaction[key]:
                transaction_fields.append(transaction[key])
            else:
                transaction_fields.append("")
        values['transaction_detail'] = "[" + ",".join(transaction_fields) + "] "
    else:
        values['transaction_detail'] = ""

    return values


# Example Spring Boot log line:
# 2017-05-22 09:42:55.680  INFO
# 9730 --- [           main] o.s.b.a.e.mvc.EndpointHandlerMapping     : Lorem ipsum...

# Example log line with added Spring Cloud Sleuth:
# 2017-05-22 09:42:55.680  INFO [hello-world,a82ac73c9c001176,a82ac73c9c001176,false]
# 9730 --- [           main] o.s.b.a.e.mvc.EndpointHandlerMapping     : Lorem ipsum...

# FORMAT = '%(asctime)s.%(millisecond)s %(levelname)+5s %(transaction_detail)s' \
#          '%(process_id)s --- [%(thread_name)+15s] %(logger_name)-40s : %(message)s'
FORMAT = '%(asctime)s %(levelname)+5s %(transaction_detail)s' \
         '%(process_id)s --- [%(thread_name)+15s] %(logger_name)-40s : %(message)s'

# logging.basicConfig(format=FORMAT, level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


def foo():
    # Test out with a few lines in spring-boot.log
    lines = [line.rstrip('\n') for line in open('tests/spring-boot.log')]
    for line in lines:
        values = regex.parse(line)
        if values:
            print()
            # print("Log line values: " + json.dumps(values))
            # print("---")
            print(line[:170] + "...")

            transaction = None
            if "transaction" in values:
                tx = values["transaction"]
                transaction = transaction_info(tx["app"], tx["id"], tx["span"], tx["exported"])
            logger = logging.getLogger(values["logger_name"])
            fh = logging.FileHandler('tests/python.log')
            logger.addHandler(fh)
            extra_info = extra(logger, transaction)
            level = values["log_level"]
            if level == "ERROR":
                logger.error(values["log_message"], extra=extra_info)
            elif level == "WARN":
                logger.warning(values["log_message"], extra=extra_info)
            elif level == "INFO":
                logger.info(values["log_message"], extra=extra_info)
            elif level == "DEBUG":
                logger.debug(values["log_message"], extra=extra_info)

#           ERROR, WARN, INFO, DEBUG or TRACE
# critical, error, warn, info, debug

                # reconstructed = message(values['log_level'], values['logger_name'], values['log_message'])
                # print("Reconstructed : " + reconstructed[:170] + "...")

        else:
            print("Failed to match log line: " + str(line))


print(extra)


foo()

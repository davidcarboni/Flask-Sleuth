""" Quick-demo code to show the logging standard in action

This is intended to produce a bunch of output on the console that demonstrates how Python log lines compare to
Spring Boot log lines.

NB the example Spring Boot lines come from a file and are re-logged through the Python core logging facility, so
timestamps, process IDs and thread names will (correctly) differ.

"""
import logging
from flask import Flask, g
from log import log, regex
from flaskb3 import b3


def parsing_demo():
    # Test out with the lines from tests/spring-boot.log
    # There's an equivalent Python log in tests/python.log to prove the reverse process.
    lines = [line.rstrip('\n') for line in open('tests/spring-boot.log')]
    # lines = [line.rstrip('\n') for line in open('tests/python.log')]

    for line in lines:

        values = regex.parse(line)
        # print("Log line values: " + str(values))

        if values:
            print(line)
            logger = logging.getLogger(values.get("logger_name"))
            logger.setLevel(logging.DEBUG)

            if values.get("transaction"):
                tracing_info = values["transaction"]
                log._app_name = tracing_info["app"]
                setattr(g, b3.b3_trace_id, tracing_info["id"])
                setattr(g, b3.b3_span_id, tracing_info["span"])
                if tracing_info["exported"] == "true":
                    setattr(g, b3.b3_sampled, "1")

            extra = log.extra(logger)
            level = values.get("log_level")
            message = values["log_message"]
            if level == "ERROR":
                logger.error(message, extra=extra)
            elif level == "WARN":
                logger.warning(message, extra=extra)
            elif level == "INFO":
                logger.info(message, extra=extra)
            elif level == "DEBUG":
                logger.debug(message, extra=extra)

            print("---")


def logging_demo():
    logger = logging.getLogger("demo_logger")
    logger.setLevel(logging.DEBUG)

    logger.debug("Logging without tracing information", extra=log.extra(logger))
    b3.collect_incoming_headers({})
    logger.debug("Logging with added tracing information", extra=log.extra(logger))


if __name__ == '__main__':
    app = Flask("myapp")
    app.before_request_funcs
    log.init(app)
    with app.app_context():
        logging_demo()
        # parsing_demo()

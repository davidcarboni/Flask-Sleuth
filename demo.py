""" Quick-demo code to show the logging standard in action

This is intended to produce a bunch of output on the console that demonstrates how Python log lines compare to
Spring Boot log lines.

NB the example Spring Boot lines come from a file and are re-logged through the Python core logging facility, so
timestamps, process IDs and thread names will (correctly) differ.

"""
from log import log, regex
import os
import logging
from flask import Flask, g
from flaskb3 import b3

# Logging

debug = bool(1)
# os.getenv("FLASK_DEBUG"))
level = logging.DEBUG if debug else logging.WARNING
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# logger.warning("Level=" + logging.getLevelName(level))
# logger.warning("Level=" + logging.getLevelName(logger.level))


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

    # No B3 tracing information collected
    logger.debug("Logging without tracing information")

    # With B3 tracing information collected
    b3.collect_incoming_headers({})
    logger.warning("Logging with added tracing information")


if __name__ == '__main__':
    app = Flask("myapp")
    log.init(app)
    with app.app_context():
        logging_demo()
        # parsing_demo()

    # Port

    port = os.getenv("PORT", "5000")
    logger.info("PORT is " + str(port))
    logger.info("FLASK_DEBUG is " + str(debug))

    # Go!

    app.run(
        host="0.0.0.0",
        port=int(port),
        debug=debug,
        threaded=True
    )

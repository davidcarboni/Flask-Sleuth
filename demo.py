""" Quick-demo code to show the logging standard in action

This is intended to produce a bunch of output on the console that demonstrates how Python log lines compare to
Spring Boot log lines.

NB the example Spring Boot lines come from a file and are re-logged through the Python core logging facility, so
timestamps, process IDs and thread names will (correctly) differ.

"""
from regex import regex
import logging
import logging_standard
from flask import Flask, g
import b3

app = Flask("myapp")


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
                logging_standard._app_name = tracing_info["app"]
                setattr(g, b3.b3_trace_id, tracing_info["id"])
                setattr(g, b3.b3_span_id, tracing_info["span"])
                if tracing_info["exported"] == "true":
                    setattr(g, b3.b3_sampled, "1")

            level = values.get("log_level")
            message = values["log_message"]
            if level == "ERROR":
                logger.error(message)
            elif level == "WARN":
                logger.warning(message)
            elif level == "INFO":
                logger.info(message)
            elif level == "DEBUG":
                logger.debug(message)

            print("---")


def logging_demo():
    logger = logging.getLogger("demo_logger")
    logger.setLevel(logging.DEBUG)

    # No B3 tracing information collected
    logger.debug("Logging without tracing information")

    # With B3 tracing information collected
    b3.start_span()
    logger.warning("Logging with added tracing information")
    b3.end_span()


@app.route("/")
def span_logging():
    log = logging.getLogger(app.name)
    log.setLevel(logging.DEBUG)
    log.debug("Debug")
    log.info("Info")
    log.warning("Warning")
    log.error("Error")
    subspan()
    return "Hello, world!"


@app.route("/subspan")
def subspan():
    log = logging.getLogger(app.name)
    b3.start_subspan()
    try:
        log.debug("Subspan Debug")
        log.info("Subspan Info")
        log.warning("Subspan Warning")
        log.error("Subspan Error")
        return "Hello, subspan world!"
    finally:
        b3.end_subspan()


if __name__ == '__main__':

    logging_standard.init(app)
    with app.app_context():
        logging_demo()
        # parsing_demo()

    # Go!

    app.before_request(b3.start_span)
    app.after_request(b3.end_span)
    app.run(
        host="0.0.0.0",
        debug=True,
        threaded=True
    )

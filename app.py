""" Quick-demo code to show the logging standard in action

This is intended to produce a bunch of output on the console that demonstrates how Python log lines compare to
Spring Boot log lines.

NB the example Spring Boot lines come from a file and are re-logged through the Python core logging facility, so
timestamps, process IDs and thread names will (correctly) differ.

"""
import logging
import sleuth
from flask import Flask, g
import b3

app = Flask("myapp")


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
    with app.app_context():
        logging_demo()

    # Go!

    app.before_request(b3.start_span)
    app.after_request(b3.end_span)
    app.run(
        host="0.0.0.0",
        debug=True,
        threaded=True
    )

""" Quick-demo code to show the logging standard in action

This is intended to produce a bunch of output on the console that demonstrates how Python log lines compare to
Spring Boot log lines.

NB the example Spring Boot lines come from a file and are re-logged through the Python core logging facility, so
timestamps, process IDs and thread names will (correctly) differ.

"""
import logging
from log import log, regex


def demo():

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
            # extra = log.extra(logger, transaction)
            extra = log.extra(logger, values.get("transaction"))
            level = values.get("log_level")
            if level == "ERROR":
                logger.error(values["log_message"], extra=extra)
            elif level == "WARN":
                logger.warning(values["log_message"], extra=extra)
            elif level == "INFO":
                logger.info(values["log_message"], extra=extra)
            elif level == "DEBUG":
                logger.debug(values["log_message"], extra=extra)

            print("---")


if __name__ == '__main__':
    demo()

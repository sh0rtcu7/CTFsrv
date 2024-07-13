import logging

class Formatter(logging.Formatter):
    yellow   = "\x1b[33;20m"
    red      = "\x1b[35m"
    bold_red = "\x1b[31;1m"
    green    = "\x1b[32m"
    magenta  = "\x1b[35m"
    reset    = "\x1b[0m"
    format   = "%(message)s"

    FORMATS = {
        logging.DEBUG    : green    + format + reset,
        logging.INFO     : yellow   + format + reset,
        logging.WARNING  : magenta  + format + reset,
        logging.ERROR    : red      + format + reset,
        logging.CRITICAL : bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
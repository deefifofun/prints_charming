import logging
from .formatter import PrintsCharmingFormatter


class PrintsCharmingLogHandler(logging.Handler):
    def __init__(self, pc, formatter: logging.Formatter = None, internal_logging=False):
        super().__init__()
        self.pc = pc
        self.setFormatter(formatter or PrintsCharmingFormatter(pc=pc, internal_logging=internal_logging))

    def emit(self, record: logging.LogRecord):
        try:
            formatted_message = self.format(record)
            print(formatted_message)
        except Exception as e:
            self.handleError(record)



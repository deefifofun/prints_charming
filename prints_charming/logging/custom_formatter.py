import logging
import time
from socket import gethostname
from prints_charming import (
    PrintsCharming,
    DEFAULT_CONFIG,
    DEFAULT_COLOR_MAP,
    DEFAULT_EFFECT_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES
)



class CustomFormatter(logging.Formatter):

    def __init__(self, pc=None, datefmt=None, style='%', timestamp_style_name=None, level_styles=None, internal_logging=False):
        super().__init__(datefmt=datefmt, style=style)
        self.pc = pc or PrintsCharming(styles=DEFAULT_LOGGING_STYLES.copy())

        if internal_logging:
            self.apply_style = self.pc._apply_style_internal
        else:
            self.apply_style = self.pc.apply_style

        self.get_style_code = self.pc.get_style_code
        self.reset = self.pc.reset
        self.hostname = gethostname()
        self.timestamp_style = timestamp_style_name
        self.level_styles = level_styles or {
            logging.DEBUG: 'debug',
            logging.INFO: 'info',
            logging.WARNING: 'warning',
            logging.ERROR: 'error',
            logging.CRITICAL: 'critical'
        }


    def formatTime(self, record, datefmt=None, ms_format="{:04.0f}"):
        t = time.localtime(record.created)
        if datefmt:
            s = time.strftime(datefmt, t)
            if '%f' in datefmt:
                # Replace the microsecond directive (%f) with milliseconds
                s = s.replace('%f', ms_format.format(record.msecs))
        else:
            s = f"{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02} {t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02},{ms_format.format(record.msecs)}"
        return s


    def format(self, record: logging.LogRecord) -> str:

        log_level_style = self.level_styles.get(record.levelno, 'default')
        log_level_style_code = self.get_style_code(log_level_style)
        args_style_code = self.get_style_code('args')

        timestamp = f"{self.formatTime(record, self.datefmt)}"
        log_level_label = f"LOG[{record.levelname}]" + ' ' * (8 - len(record.levelname))

        record.msecs = "{:04.0f}".format(record.msecs)
        record.hostname = self.apply_style('hostname', self.hostname)
        record.filename = self.apply_style('filename', record.filename)
        record.name = self.apply_style('record_name', record.name)
        record.funcName = self.apply_style('method_name', record.funcName)
        record.lineno = self.apply_style('line_number', record.lineno)

        if record.args:

            # Prepare the formatted message by applying the style to each argument
            formatted_args = [f"{args_style_code}{arg}{self.reset}{log_level_style_code}" for arg in record.args]

            # Apply the formatting to the message
            record.msg = record.msg.format(*formatted_args)
            record.args = ()  # Clear args to prevent further formatting attempts

        timestamp_style = log_level_style if not self.timestamp_style else self.timestamp_style

        styled_timestamp = self.apply_style(timestamp_style, timestamp) + record.msecs
        styled_log_level_prefix = self.apply_style(log_level_style, log_level_label)
        styled_level = self.apply_style(log_level_style, record.levelname)


        # Apply log level style to the entire message
        record.msg = f"{log_level_style_code}{record.msg}{self.reset}"

        record.msg = f"{record.hostname} - {record.filename} {record.name} {record.funcName}:{record.lineno} - {record.msg}"

        log_message = f"{styled_timestamp} {styled_log_level_prefix} {record.msg}"

        return log_message



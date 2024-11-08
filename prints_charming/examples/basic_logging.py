

from typing import Any, Dict, List, Optional, Union
from prints_charming import (
    DEFAULT_COLOR_MAP,
    DEFAULT_STYLES,
    get_terminal_width,
    PrintsCharming,
)

from prints_charming.logging import setup_logger

import os
import sys
import logging
import inspect
import copy
import textwrap








def custom_excepthook_error_example():
    zero_div_error = 1 / 0


def create_logger_with_unhandled_exception_logging():
    logger = setup_logger(enable_exception_logging=True)

    logger.pc.print(logger.name, style='green')


def create_logger_with_shared_logging_pc_instance():


def create_logger_with_shared_pc_instance():
    pc = PrintsCharming()
    PrintsCharming.set_shared_instance(pc)


def create_logger_with_specific_pc_instance():
    pc = PrintsCharming()
    logger = setup_logger(pc=pc)

    pc.print(logger.name, style='green')


def create_logger_with_its_own_pc_instance():
    logger = setup_logger()

    # Access pc instance with
    pc = logger.pc

    pc.print(logger.name, style='green')



def main():

    logger = setup_logger()











if __name__ == "__main__":
    main()
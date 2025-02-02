import sys
import platform

if platform.system() == "Windows":
    import ctypes
    from ctypes import create_string_buffer
    import struct
    import os
    import shutil
    import logging
else:
    ctypes = None  # Fallback to None for non-Windows systems



class WinUtils:
    if platform.system() == "Windows":
        # Constants for handle types
        STD_INPUT_HANDLE = -10
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE = -12

        # Console mode flags
        ENABLE_PROCESSED_OUTPUT = 0x0001
        ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

        k32 = ctypes.windll.kernel32


        @classmethod
        def get_terminal_size_windows(cls):
            """
            Gets the terminal size for a Windows environment, with edge-case handling
            for redirected output and WSL environments.
            """
            try:
                # Check if output is redirected (e.g., to a file or pipe)
                if not os.isatty(sys.stdout.fileno()):
                    logging.info("Output is redirected. Falling back to default size.")
                    return 80, 24

                # Check if running in WSL
                if "microsoft-standard" in platform.uname().release.lower():
                    logging.info("Running in WSL. Falling back to shutil.get_terminal_size().")
                    size = shutil.get_terminal_size()
                    return size.columns, size.lines

                # Get handle for standard output
                h = cls.k32.GetStdHandle(cls.STD_OUTPUT_HANDLE)

                csbi = create_string_buffer(22)
                # Retrieve console screen buffer info
                if not cls.k32.GetConsoleScreenBufferInfo(h, csbi):
                    raise ctypes.WinError()

                # Unpack terminal size from the csbi buffer
                _, _, _, _, _, left, top, right, bottom, *_ = struct.unpack("hhhhHhhhhhh", csbi.raw)

                # Calculate width and height
                width = right - left + 1
                height = bottom - top + 1
                return width, height
            except Exception as e:
                print(f"Windows terminal size fetch failed: {e}")
            # Fallback if Windows API fails
            return 80, 24


        @staticmethod
        def is_ansi_supported_natively():
            """
            Check if the current version of Windows supports ANSI escape codes natively.
            Returns True if supported, False otherwise.
            """
            # Get Windows version as a tuple, e.g., (10, 0, 19041) for Windows 10
            win_version = platform.version().split(".")

            # For Windows 10, version 1511 or later supports ANSI codes
            return int(win_version[0]) >= 10 and int(win_version[2]) >= 10586


        @classmethod
        def enable_win_console_ansi_handling(cls, handle_type=None, mode=None):
            """
            Enables ANSI escape code handling for the specified console handle.

            Parameters:
            handle_type (int): The type of console handle (-10: stdin, -11: stdout, -12: stderr).
            mode (int): Custom mode flags to set. If None, the default mode enabling ANSI will be used.
            """
            try:
                handle = cls.k32.GetStdHandle(handle_type or cls.STD_OUTPUT_HANDLE)

                # Save the original console mode
                original_mode = ctypes.c_uint32()
                if not cls.k32.GetConsoleMode(handle, ctypes.byref(original_mode)):
                    logging.error("Failed to get original console mode")
                    return False

                if mode is None:
                    # Default mode enabling ANSI escape code handling
                    mode = (cls.ENABLE_PROCESSED_OUTPUT |
                            cls.ENABLE_WRAP_AT_EOL_OUTPUT |
                            cls.ENABLE_VIRTUAL_TERMINAL_PROCESSING)

                # Set the new console mode
                if not cls.k32.SetConsoleMode(handle, mode):
                    logging.error("Failed to set console mode")
                    return False

                logging.info(f"Console mode set to {mode}")
                return True
            except Exception as e:
                logging.error(f"Error enabling ANSI handling: {e}")
                return False


        @classmethod
        def restore_console_mode(cls, handle_type=None):
            """
            Restores the original console mode for the specified console handle.

            Parameters:
            handle_type (int): The type of console handle (-10: stdin, -11: stdout, -12: stderr).
            """
            try:
                # Get the console handle
                handle = cls.k32.GetStdHandle(handle_type or cls.STD_OUTPUT_HANDLE)

                # Restore the original console mode
                original_mode = ctypes.c_uint32()
                if not cls.k32.GetConsoleMode(handle, ctypes.byref(original_mode)):
                    logging.error("Failed to get original console mode")
                    return False

                if not cls.k32.SetConsoleMode(handle, original_mode.value):
                    logging.error("Failed to restore console mode")
                    return False

                logging.info("Original console mode restored")
                return True
            except Exception as e:
                logging.error(f"Error restoring console mode: {e}")
                return False


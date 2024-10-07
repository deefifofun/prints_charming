import ctypes
import logging
import platform



class WinUtils:
    # Constants for handle types
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    # Console mode flags
    ENABLE_PROCESSED_OUTPUT = 0x0001
    ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004


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


    @staticmethod
    def enable_win_console_ansi_handling(handle_type=-11, mode=None):
        """
        Enables ANSI escape code handling for the specified console handle.

        Parameters:
        handle_type (int): The type of console handle (-10: stdin, -11: stdout, -12: stderr).
        mode (int): Custom mode flags to set. If None, the default mode enabling ANSI will be used.
        """
        try:
            k32 = ctypes.windll.kernel32

            # Get the console handle
            handle = k32.GetStdHandle(handle_type)

            # Save the original console mode
            original_mode = ctypes.c_uint32()
            if not k32.GetConsoleMode(handle, ctypes.byref(original_mode)):
                logging.error("Failed to get original console mode")
                return False

            if mode is None:
                # Default mode enabling ANSI escape code handling
                mode = (WinUtils.ENABLE_PROCESSED_OUTPUT |
                        WinUtils.ENABLE_WRAP_AT_EOL_OUTPUT |
                        WinUtils.ENABLE_VIRTUAL_TERMINAL_PROCESSING)

            # Set the new console mode
            if not k32.SetConsoleMode(handle, mode):
                logging.error("Failed to set console mode")
                return False

            logging.info(f"Console mode set to {mode}")
            return True
        except Exception as e:
            logging.error(f"Error enabling ANSI handling: {e}")
            return False



    @staticmethod
    def restore_console_mode(handle_type=-11):
        """
        Restores the original console mode for the specified console handle.

        Parameters:
        handle_type (int): The type of console handle (-10: stdin, -11: stdout, -12: stderr).
        """
        try:
            k32 = ctypes.windll.kernel32

            # Get the console handle
            handle = k32.GetStdHandle(handle_type)

            # Restore the original console mode
            original_mode = ctypes.c_uint32()
            if not k32.GetConsoleMode(handle, ctypes.byref(original_mode)):
                logging.error("Failed to get original console mode")
                return False

            if not k32.SetConsoleMode(handle, original_mode.value):
                logging.error("Failed to restore console mode")
                return False

            logging.info("Original console mode restored")
            return True
        except Exception as e:
            logging.error(f"Error restoring console mode: {e}")
            return False

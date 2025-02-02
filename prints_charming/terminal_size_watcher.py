# terminal_size_watcher.py

import os
import shutil
import sys
import time
import termios
import signal
import fcntl
import struct
import threading





class TerminalSizeWatcher:
    def __init__(self, pc):
        self.pc = pc
        self.is_watching = False  # Flag to indicate if the watcher is active
        self.stop_watching_flag = False  # Flag to stop the watcher thread
        self.watcher_thread = None

        # Initialize terminal dimensions
        self.pc.terminal_width, self.pc.terminal_height = self.get_terminal_size()

        # Automatically start watching if enabled in the PrintsCharming instance
        if self.pc.enable_term_size_watcher:
            self.start()


    def get_terminal_size(self):
        if not self.pc.win_utils:
            return self.get_terminal_size_unix()
        else:
            return self.pc.win_utils.get_terminal_size_windows()


    def get_terminal_size_unix(self):
        try:
            # Try using os.get_terminal_size()
            size = os.get_terminal_size()
            return size.columns, size.lines
        except OSError:
            try:
                # Fallback to shutil.get_terminal_size()
                size = shutil.get_terminal_size()
                return size.columns, size.lines
            except OSError:
                try:
                    # Fallback to ioctl syscall
                    hw = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234')
                    height, width = struct.unpack('hh', hw)
                    return width, height
                except:
                    # Ultimate fallback
                    return 80, 24

    def update_terminal_size(self, signum=None, frame=None):
        """Update terminal size on resize."""
        self.pc.terminal_width, self.pc.terminal_height = self.get_terminal_size()
        #print(f"Terminal resized: {self.pc.terminal_width}x{self.pc.terminal_height}")


    def poll_terminal_size_windows(self):
        """Poll for terminal size changes on Windows."""
        while not self.stop_watching_flag:
            width, height = self.get_terminal_size()
            if (width, height) != (self.pc.terminal_width, self.pc.terminal_height):
                self.pc.terminal_width, self.pc.terminal_height = width, height
                print(f"Terminal resized: {self.pc.terminal_width}x{self.pc.terminal_height}")
            time.sleep(0.5)  # Adjust polling interval as needed


    def start(self):
        """
        Start the terminal size watcher.
        """
        if self.is_watching:
            return  # Already watching

        self.is_watching = True
        if self.pc.win_utils:
            # Start the polling thread for Windows
            self.stop_watching_flag = False
            self.watcher_thread = threading.Thread(target=self.poll_terminal_size_windows, daemon=True)
            self.watcher_thread.start()
        else:
            # Set up signal handling for Unix
            signal.signal(signal.SIGWINCH, self.update_terminal_size)


    def stop(self):
        """Stop watching for terminal size changes."""
        if not self.is_watching:
            return
        self.is_watching = False
        if self.pc.win_utils:
            self.stop_watching_flag = True
            if self.watcher_thread:
                self.watcher_thread.join()
        else:
            # Reset signal handling for Unix
            signal.signal(signal.SIGWINCH, signal.SIG_DFL)



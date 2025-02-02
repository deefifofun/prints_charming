
import sys
import time
import asyncio
import threading




class PBar:
    def __init__(self, pc_instance, total: int, desc: str = "", width: int = 40, style: str = "progress", mode="auto"):
        """
        A progress bar supporting synchronous, threading, and asyncio execution modes.

        :param pc_instance: Instance of PrintsCharming.
        :param total: Total number of steps.
        :param desc: Description for the progress bar.
        :param width: Width of the progress bar.
        :param style: Style to use from PrintsCharming.
        :param mode: Execution mode: "sync", "thread", "async", or "auto" (auto-detect).
        """
        self.pc = pc_instance
        self.total = total
        self.desc = desc
        self.width = width
        self.style = style
        self.current = 0
        self.start_time = None
        self._lock = threading.Lock()
        self._thread = None
        self._stop_event = threading.Event()

        # Mode selection logic
        if mode == "auto":
            self.mode = "async" if asyncio.get_event_loop().is_running() else "sync"
        else:
            self.mode = mode




    def __enter__(self):
        """Context manager support for sync/thread modes."""
        self.start()
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure the progress bar completes on exit."""
        self.finish()


    async def __aenter__(self):
        """Context manager support for async mode."""
        self.start()
        return self


    async def __aexit__(self, exc_type, exc_value, traceback):
        """Ensure the progress bar completes in async mode on exit."""
        self.finish()


    def start(self):
        """Starts the progress bar based on the chosen mode."""
        self.start_time = time.time()
        if self.mode == "thread":
            self._start_thread()
        elif self.mode == "async":
            asyncio.create_task(self._print_progress_async())  # Run async in event loop
        else:
            self._print_progress()


    def update(self, step: int = 1):
        """Updates progress in a thread-safe manner."""
        if self.mode in {"thread", "sync"}:
            with self._lock:
                self.current += step
                self._print_progress()
        elif self.mode == "async":
            asyncio.create_task(self._update_async(step))
        else:
            self.current += step
            self._print_progress()


    async def update_async(self, step: int = 1):
        """Allows async users to call update manually."""
        await self._update_async(step)


    async def _update_async(self, step: int):
        """Handles async updates safely."""
        self.current += step
        await self._print_progress_async()


    def finish(self):
        """Completes the progress bar."""
        if self.mode == "thread":
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                self._thread.join()
        elif self.mode == "async":
            asyncio.create_task(self._finish_async())
        else:
            self.current = self.total
            self._print_progress()
            print("")


    async def finish_async(self):
        """Allows async users to call finish manually."""
        await self._finish_async()


    async def _finish_async(self):
        """Handles async completion."""
        self.current = self.total
        await self._print_progress_async()
        print("")


    def _start_thread(self):
        """Starts a separate thread to update progress periodically."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._progress_loop, daemon=True)
        self._thread.start()


    def _progress_loop(self):
        """Thread function to continuously update progress."""
        while not self._stop_event.is_set():
            with self._lock:
                self._print_progress()
            time.sleep(0.1)


    def _print_progress(self):
        """Prints the progress bar synchronously."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        percent = self.current / self.total
        num_blocks = int(self.width * percent)

        filled = "█" * num_blocks
        empty = " " * (self.width - num_blocks)

        eta = ((elapsed / self.current) * (self.total - self.current)) if self.current > 0 else 0

        progress_str = (
            f"\r{self.desc}: " if self.desc else "\r"
        ) + (
            f"{self.pc.apply_style(self.style, '[')}"
            f"{self.pc.apply_style(self.style, filled)}"
            f"{self.pc.apply_style('default', empty)}"
            f"{self.pc.apply_style(self.style, ']')} "
            f"{int(percent * 100)}% | ETA: {eta:.2f}s"
        )

        sys.stdout.write(progress_str)
        sys.stdout.flush()


    async def _print_progress_async(self):
        """Handles async progress printing."""
        with self._lock:
            self._print_progress()














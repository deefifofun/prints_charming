import os
import sys
import pty
import subprocess
import threading
import time


def launch_terminal(pc_instance, name, terminal_emulator="gnome-terminal", width=80, height=24, title="New Terminal", task=None):
    """
    Launch a new terminal using a pseudo-terminal.
    """
    if pc_instance.terminal_mode != "multi":
        raise RuntimeError("Multi-terminal mode is not enabled.")

    master_fd, slave_fd = pty.openpty()
    terminal_cmd = [
        terminal_emulator,
        "--geometry", f"{width}x{height}",
        "--", "bash", "-c", "cat",
    ]
    subprocess.Popen(
        terminal_cmd,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True,
    )
    os.close(slave_fd)
    time.sleep(0.5)  # Give time for initialization

    pc_instance.terminals[name] = master_fd

    sys.stdout = os.fdopen(master_fd, "w")
    sys.stdin = os.fdopen(master_fd, "r")
    pc_instance.write("alt_buffer")
    pc_instance.write("set_window_title", title=title)

    if task:
        threading.Thread(target=task, args=(master_fd,)).start()


def restore_terminal(pc_instance, name=None):
    if name:
        _restore_single_terminal(pc_instance, name)
    else:
        for terminal_name in list(pc_instance.terminals.keys()):
            _restore_single_terminal(pc_instance, terminal_name)


def _restore_single_terminal(pc_instance, name):
    master_fd = pc_instance.terminals.get(name)
    if master_fd:
        sys.stdout = sys.__stdout__
        pc_instance.write("normal_buffer")
        os.close(master_fd)
        del pc_instance.terminals[name]


def write_multi_terminal(pc_instance, master_fd: int, *control_keys_or_text, **kwargs):
    try:
        with os.fdopen(master_fd, "w") as terminal_output:
            sys.stdout = terminal_output
            pc_instance.write(*control_keys_or_text, **kwargs)
    finally:
        sys.stdout = sys.__stdout__




















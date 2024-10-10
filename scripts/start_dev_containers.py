import threading
import subprocess
import platform
import sys
import logging

log = logging.getLogger(__name__)

from core import setup


def stream_output(pipe):
    """Continuously read output from the process stream and print it in real-time."""
    try:
        for line in iter(pipe.readline, ""):
            print(
                line, end="", flush=True
            )  # Flush immediately to ensure real-time output
    except Exception as e:
        log.error(f"Error streaming output: {e}")
    finally:
        pipe.close()  # Close the pipe when done


def execute_command(command, shell: bool = False):
    try:
        # Use Popen for real-time output streaming
        process = subprocess.Popen(
            command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffering
        )

        # Create threads to stream both stdout and stderr in real-time
        stdout_thread = threading.Thread(target=stream_output, args=(process.stdout,))
        stderr_thread = threading.Thread(target=stream_output, args=(process.stderr,))

        stdout_thread.start()
        stderr_thread.start()

        # Wait for both threads to complete
        stdout_thread.join()
        stderr_thread.join()

        # Wait for the process to complete
        process.wait()

    except subprocess.CalledProcessError as e:
        print(
            f"[ERROR] Error executing command: {command}. Details: {e}", file=sys.stderr
        )
        print(e.stderr, file=sys.stderr)


def run():
    current_os = platform.system()

    match current_os:
        case "Linux" | "Darwin":
            if current_os == "Linux":
                log.info("Starting Docker dev stack on Linux")
            elif current_os == "Darwin":
                log.info("Starting Docker dev stack on Mac")

            bash_cmd = "scripts/start_scripts/start-dev-containers.sh"
            execute_command(command=bash_cmd, shell=True)

        case "Windows":
            log.info("Starting Docker dev stack on Windows")

            powershell_cmd = [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/start_scripts/start-dev-containers.ps1",
            ]
            execute_command(command=powershell_cmd, shell=True)

        case _:
            log.error(f"Unsupported OS: {current_os}")
            exit(1)


if __name__ == "__main__":
    setup.setup_logging(level=setup.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"))
    run()

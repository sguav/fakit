import threading
import itertools
import sys
import time

class Spinner:
    """Terminal spinner in a separate thread."""
    def __init__(self, message="Working"):
        self._running = False
        self._thread = None
        self.message = message

    def start(self):
        """Start the spinner in a separate thread."""
        self._running = True
        self._thread = threading.Thread(target=self._spin)
        self._thread.start()

    def _spin(self):
        for c in itertools.cycle("|/-\\"):
            if not self._running:
                break
            sys.stdout.write(f"\r{self.message}... {c}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 5) + "\r")
        sys.stdout.flush()

    def stop(self):
        """Stop the spinner."""
        self._running = False
        if self._thread:
            self._thread.join()

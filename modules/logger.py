from datetime import datetime


class Logger:

    @staticmethod
    def _timestamp():
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def info(message):
        print(f"[{Logger._timestamp()}] {message}")

    @staticmethod
    def success(message):
        print(f"[{Logger._timestamp()}] ✓ {message}")

    @staticmethod
    def warning(message):
        print(f"[{Logger._timestamp()}] ⚠ {message}")

    @staticmethod
    def error(message):
        print(f"[{Logger._timestamp()}] ✗ {message}")

    @staticmethod
    def section(title):
        print()
        print("=" * 80)
        print(f"[{Logger._timestamp()}] {title}")
        print("=" * 80)
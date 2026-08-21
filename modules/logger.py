from datetime import datetime


class Logger:

    INFO_ONLY = True

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
    def section(message):
        if Logger.INFO_ONLY:
            return
        print()
        print("=" * 80)
        print(message)
        print("=" * 80)
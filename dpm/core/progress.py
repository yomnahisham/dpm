"""
progress.py - progress bars and colored output
"""

import sys
from typing import Optional


class Color:
    """ansi color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    @staticmethod
    def disable():
        """disable colors (for non-terminal output)"""
        Color.RESET = ''
        Color.BOLD = ''
        Color.DIM = ''
        Color.BLACK = ''
        Color.RED = ''
        Color.GREEN = ''
        Color.YELLOW = ''
        Color.BLUE = ''
        Color.MAGENTA = ''
        Color.CYAN = ''
        Color.WHITE = ''
        Color.BRIGHT_BLACK = ''
        Color.BRIGHT_RED = ''
        Color.BRIGHT_GREEN = ''
        Color.BRIGHT_YELLOW = ''
        Color.BRIGHT_BLUE = ''
        Color.BRIGHT_MAGENTA = ''
        Color.BRIGHT_CYAN = ''
        Color.BRIGHT_WHITE = ''
    
    @staticmethod
    def is_terminal() -> bool:
        """check if output is going to a terminal"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


class ProgressBar:
    """simple progress bar for showing progress"""
    
    def __init__(self, total: int, prefix: str = "", width: int = 40):
        self.total = total
        self.current = 0
        self.prefix = prefix
        self.width = width
        self._last_length = 0
    
    def update(self, current: Optional[int] = None):
        """update progress bar"""
        if current is not None:
            self.current = current
        else:
            self.current += 1
        
        if not Color.is_terminal():
            # non-terminal: just print percentage
            if self.current % max(1, self.total // 10) == 0 or self.current == self.total:
                percent = int(100 * self.current / self.total) if self.total > 0 else 0
                print(f"{self.prefix}: {percent}%", file=sys.stderr)
            return
        
        # calculate progress
        percent = self.current / self.total if self.total > 0 else 0
        filled = int(self.width * percent)
        bar = '=' * filled + '-' * (self.width - filled)
        percent_str = f"{int(100 * percent)}%"
        
        # build output
        output = f"\r{self.prefix} [{bar}] {percent_str} ({self.current}/{self.total})"
        
        # clear previous line and print new one
        sys.stdout.write('\r' + ' ' * self._last_length + '\r')
        sys.stdout.write(output)
        sys.stdout.flush()
        self._last_length = len(output)
    
    def finish(self):
        """finish progress bar"""
        if Color.is_terminal():
            sys.stdout.write('\r' + ' ' * self._last_length + '\r')
            sys.stdout.flush()
        print()  # new line


class Spinner:
    """simple spinner for indeterminate progress"""
    
    SPINNER_CHARS = ['|', '/', '-', '\\']
    
    def __init__(self, message: str = ""):
        self.message = message
        self.spinning = False
        self._spinner_index = 0
    
    def start(self):
        """start spinner"""
        self.spinning = True
        if Color.is_terminal():
            sys.stdout.write(f"\r{self.message} {self.SPINNER_CHARS[0]}")
            sys.stdout.flush()
    
    def update(self):
        """update spinner"""
        if not self.spinning or not Color.is_terminal():
            return
        
        self._spinner_index = (self._spinner_index + 1) % len(self.SPINNER_CHARS)
        sys.stdout.write(f"\r{self.message} {self.SPINNER_CHARS[self._spinner_index]}")
        sys.stdout.flush()
    
    def stop(self, success: bool = True):
        """stop spinner"""
        self.spinning = False
        if Color.is_terminal():
            sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
            sys.stdout.flush()
        
        if success:
            print(f"{self.message} {Color.GREEN}[OK]{Color.RESET}")
        else:
            print(f"{self.message} {Color.RED}[FAILED]{Color.RESET}")


def success(message: str):
    """print success message"""
    print(f"{Color.GREEN}[OK]{Color.RESET} {message}")


def error(message: str):
    """print error message"""
    print(f"{Color.RED}[ERROR]{Color.RESET} {message}")


def warning(message: str):
    """print warning message"""
    print(f"{Color.YELLOW}[WARNING]{Color.RESET} {message}")


def info(message: str):
    """print info message"""
    print(f"{Color.CYAN}[INFO]{Color.RESET} {message}")


progress.py - progress bars and colored output
"""

import sys
from typing import Optional


class Color:
    """ansi color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    @staticmethod
    def disable():
        """disable colors (for non-terminal output)"""
        Color.RESET = ''
        Color.BOLD = ''
        Color.DIM = ''
        Color.BLACK = ''
        Color.RED = ''
        Color.GREEN = ''
        Color.YELLOW = ''
        Color.BLUE = ''
        Color.MAGENTA = ''
        Color.CYAN = ''
        Color.WHITE = ''
        Color.BRIGHT_BLACK = ''
        Color.BRIGHT_RED = ''
        Color.BRIGHT_GREEN = ''
        Color.BRIGHT_YELLOW = ''
        Color.BRIGHT_BLUE = ''
        Color.BRIGHT_MAGENTA = ''
        Color.BRIGHT_CYAN = ''
        Color.BRIGHT_WHITE = ''
    
    @staticmethod
    def is_terminal() -> bool:
        """check if output is going to a terminal"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


class ProgressBar:
    """simple progress bar for showing progress"""
    
    def __init__(self, total: int, prefix: str = "", width: int = 40):
        self.total = total
        self.current = 0
        self.prefix = prefix
        self.width = width
        self._last_length = 0
    
    def update(self, current: Optional[int] = None):
        """update progress bar"""
        if current is not None:
            self.current = current
        else:
            self.current += 1
        
        if not Color.is_terminal():
            # non-terminal: just print percentage
            if self.current % max(1, self.total // 10) == 0 or self.current == self.total:
                percent = int(100 * self.current / self.total) if self.total > 0 else 0
                print(f"{self.prefix}: {percent}%", file=sys.stderr)
            return
        
        # calculate progress
        percent = self.current / self.total if self.total > 0 else 0
        filled = int(self.width * percent)
        bar = '=' * filled + '-' * (self.width - filled)
        percent_str = f"{int(100 * percent)}%"
        
        # build output
        output = f"\r{self.prefix} [{bar}] {percent_str} ({self.current}/{self.total})"
        
        # clear previous line and print new one
        sys.stdout.write('\r' + ' ' * self._last_length + '\r')
        sys.stdout.write(output)
        sys.stdout.flush()
        self._last_length = len(output)
    
    def finish(self):
        """finish progress bar"""
        if Color.is_terminal():
            sys.stdout.write('\r' + ' ' * self._last_length + '\r')
            sys.stdout.flush()
        print()  # new line


class Spinner:
    """simple spinner for indeterminate progress"""
    
    SPINNER_CHARS = ['|', '/', '-', '\\']
    
    def __init__(self, message: str = ""):
        self.message = message
        self.spinning = False
        self._spinner_index = 0
    
    def start(self):
        """start spinner"""
        self.spinning = True
        if Color.is_terminal():
            sys.stdout.write(f"\r{self.message} {self.SPINNER_CHARS[0]}")
            sys.stdout.flush()
    
    def update(self):
        """update spinner"""
        if not self.spinning or not Color.is_terminal():
            return
        
        self._spinner_index = (self._spinner_index + 1) % len(self.SPINNER_CHARS)
        sys.stdout.write(f"\r{self.message} {self.SPINNER_CHARS[self._spinner_index]}")
        sys.stdout.flush()
    
    def stop(self, success: bool = True):
        """stop spinner"""
        self.spinning = False
        if Color.is_terminal():
            sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
            sys.stdout.flush()
        
        if success:
            print(f"{self.message} {Color.GREEN}[OK]{Color.RESET}")
        else:
            print(f"{self.message} {Color.RED}[FAILED]{Color.RESET}")


def success(message: str):
    """print success message"""
    print(f"{Color.GREEN}[OK]{Color.RESET} {message}")


def error(message: str):
    """print error message"""
    print(f"{Color.RED}[ERROR]{Color.RESET} {message}")


def warning(message: str):
    """print warning message"""
    print(f"{Color.YELLOW}[WARNING]{Color.RESET} {message}")


def info(message: str):
    """print info message"""
    print(f"{Color.CYAN}[INFO]{Color.RESET} {message}")


progress.py - progress bars and colored output
"""

import sys
from typing import Optional


class Color:
    """ansi color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    @staticmethod
    def disable():
        """disable colors (for non-terminal output)"""
        Color.RESET = ''
        Color.BOLD = ''
        Color.DIM = ''
        Color.BLACK = ''
        Color.RED = ''
        Color.GREEN = ''
        Color.YELLOW = ''
        Color.BLUE = ''
        Color.MAGENTA = ''
        Color.CYAN = ''
        Color.WHITE = ''
        Color.BRIGHT_BLACK = ''
        Color.BRIGHT_RED = ''
        Color.BRIGHT_GREEN = ''
        Color.BRIGHT_YELLOW = ''
        Color.BRIGHT_BLUE = ''
        Color.BRIGHT_MAGENTA = ''
        Color.BRIGHT_CYAN = ''
        Color.BRIGHT_WHITE = ''
    
    @staticmethod
    def is_terminal() -> bool:
        """check if output is going to a terminal"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


class ProgressBar:
    """simple progress bar for showing progress"""
    
    def __init__(self, total: int, prefix: str = "", width: int = 40):
        self.total = total
        self.current = 0
        self.prefix = prefix
        self.width = width
        self._last_length = 0
    
    def update(self, current: Optional[int] = None):
        """update progress bar"""
        if current is not None:
            self.current = current
        else:
            self.current += 1
        
        if not Color.is_terminal():
            # non-terminal: just print percentage
            if self.current % max(1, self.total // 10) == 0 or self.current == self.total:
                percent = int(100 * self.current / self.total) if self.total > 0 else 0
                print(f"{self.prefix}: {percent}%", file=sys.stderr)
            return
        
        # calculate progress
        percent = self.current / self.total if self.total > 0 else 0
        filled = int(self.width * percent)
        bar = '=' * filled + '-' * (self.width - filled)
        percent_str = f"{int(100 * percent)}%"
        
        # build output
        output = f"\r{self.prefix} [{bar}] {percent_str} ({self.current}/{self.total})"
        
        # clear previous line and print new one
        sys.stdout.write('\r' + ' ' * self._last_length + '\r')
        sys.stdout.write(output)
        sys.stdout.flush()
        self._last_length = len(output)
    
    def finish(self):
        """finish progress bar"""
        if Color.is_terminal():
            sys.stdout.write('\r' + ' ' * self._last_length + '\r')
            sys.stdout.flush()
        print()  # new line


class Spinner:
    """simple spinner for indeterminate progress"""
    
    SPINNER_CHARS = ['|', '/', '-', '\\']
    
    def __init__(self, message: str = ""):
        self.message = message
        self.spinning = False
        self._spinner_index = 0
    
    def start(self):
        """start spinner"""
        self.spinning = True
        if Color.is_terminal():
            sys.stdout.write(f"\r{self.message} {self.SPINNER_CHARS[0]}")
            sys.stdout.flush()
    
    def update(self):
        """update spinner"""
        if not self.spinning or not Color.is_terminal():
            return
        
        self._spinner_index = (self._spinner_index + 1) % len(self.SPINNER_CHARS)
        sys.stdout.write(f"\r{self.message} {self.SPINNER_CHARS[self._spinner_index]}")
        sys.stdout.flush()
    
    def stop(self, success: bool = True):
        """stop spinner"""
        self.spinning = False
        if Color.is_terminal():
            sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
            sys.stdout.flush()
        
        if success:
            print(f"{self.message} {Color.GREEN}[OK]{Color.RESET}")
        else:
            print(f"{self.message} {Color.RED}[FAILED]{Color.RESET}")


def success(message: str):
    """print success message"""
    print(f"{Color.GREEN}[OK]{Color.RESET} {message}")


def error(message: str):
    """print error message"""
    print(f"{Color.RED}[ERROR]{Color.RESET} {message}")


def warning(message: str):
    """print warning message"""
    print(f"{Color.YELLOW}[WARNING]{Color.RESET} {message}")


def info(message: str):
    """print info message"""
    print(f"{Color.CYAN}[INFO]{Color.RESET} {message}")


progress.py - progress bars and colored output
"""

import sys
from typing import Optional


class Color:
    """ansi color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    @staticmethod
    def disable():
        """disable colors (for non-terminal output)"""
        Color.RESET = ''
        Color.BOLD = ''
        Color.DIM = ''
        Color.BLACK = ''
        Color.RED = ''
        Color.GREEN = ''
        Color.YELLOW = ''
        Color.BLUE = ''
        Color.MAGENTA = ''
        Color.CYAN = ''
        Color.WHITE = ''
        Color.BRIGHT_BLACK = ''
        Color.BRIGHT_RED = ''
        Color.BRIGHT_GREEN = ''
        Color.BRIGHT_YELLOW = ''
        Color.BRIGHT_BLUE = ''
        Color.BRIGHT_MAGENTA = ''
        Color.BRIGHT_CYAN = ''
        Color.BRIGHT_WHITE = ''
    
    @staticmethod
    def is_terminal() -> bool:
        """check if output is going to a terminal"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


class ProgressBar:
    """simple progress bar for showing progress"""
    
    def __init__(self, total: int, prefix: str = "", width: int = 40):
        self.total = total
        self.current = 0
        self.prefix = prefix
        self.width = width
        self._last_length = 0
    
    def update(self, current: Optional[int] = None):
        """update progress bar"""
        if current is not None:
            self.current = current
        else:
            self.current += 1
        
        if not Color.is_terminal():
            # non-terminal: just print percentage
            if self.current % max(1, self.total // 10) == 0 or self.current == self.total:
                percent = int(100 * self.current / self.total) if self.total > 0 else 0
                print(f"{self.prefix}: {percent}%", file=sys.stderr)
            return
        
        # calculate progress
        percent = self.current / self.total if self.total > 0 else 0
        filled = int(self.width * percent)
        bar = '=' * filled + '-' * (self.width - filled)
        percent_str = f"{int(100 * percent)}%"
        
        # build output
        output = f"\r{self.prefix} [{bar}] {percent_str} ({self.current}/{self.total})"
        
        # clear previous line and print new one
        sys.stdout.write('\r' + ' ' * self._last_length + '\r')
        sys.stdout.write(output)
        sys.stdout.flush()
        self._last_length = len(output)
    
    def finish(self):
        """finish progress bar"""
        if Color.is_terminal():
            sys.stdout.write('\r' + ' ' * self._last_length + '\r')
            sys.stdout.flush()
        print()  # new line


class Spinner:
    """simple spinner for indeterminate progress"""
    
    SPINNER_CHARS = ['|', '/', '-', '\\']
    
    def __init__(self, message: str = ""):
        self.message = message
        self.spinning = False
        self._spinner_index = 0
    
    def start(self):
        """start spinner"""
        self.spinning = True
        if Color.is_terminal():
            sys.stdout.write(f"\r{self.message} {self.SPINNER_CHARS[0]}")
            sys.stdout.flush()
    
    def update(self):
        """update spinner"""
        if not self.spinning or not Color.is_terminal():
            return
        
        self._spinner_index = (self._spinner_index + 1) % len(self.SPINNER_CHARS)
        sys.stdout.write(f"\r{self.message} {self.SPINNER_CHARS[self._spinner_index]}")
        sys.stdout.flush()
    
    def stop(self, success: bool = True):
        """stop spinner"""
        self.spinning = False
        if Color.is_terminal():
            sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
            sys.stdout.flush()
        
        if success:
            print(f"{self.message} {Color.GREEN}[OK]{Color.RESET}")
        else:
            print(f"{self.message} {Color.RED}[FAILED]{Color.RESET}")


def success(message: str):
    """print success message"""
    print(f"{Color.GREEN}[OK]{Color.RESET} {message}")


def error(message: str):
    """print error message"""
    print(f"{Color.RED}[ERROR]{Color.RESET} {message}")


def warning(message: str):
    """print warning message"""
    print(f"{Color.YELLOW}[WARNING]{Color.RESET} {message}")


def info(message: str):
    """print info message"""
    print(f"{Color.CYAN}[INFO]{Color.RESET} {message}")




import datetime
import sys

class Logger:
    """
    A simple logging abstraction that adds timestamps to log messages
    and supports different log levels.
    """
    # Log levels
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    
    # ANSI color codes for colored output
    COLORS = {
        'RESET': '\033[0m',
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m'     # Red
    }
    
    def __init__(self, name, min_level=INFO, use_colors=True):
        """
        Initialize the logger.
        
        Args:
            name (str): Name of the logger/module
            min_level (int): Minimum log level to display
            use_colors (bool): Whether to use colored output
        """
        self.name = name
        self.min_level = min_level
        self.use_colors = use_colors
        
    def _get_timestamp(self):
        """Get current timestamp in ISO format."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    def _get_level_name(self, level):
        """Convert level integer to string name."""
        return {
            self.DEBUG: "DEBUG",
            self.INFO: "INFO",
            self.WARNING: "WARNING",
            self.ERROR: "ERROR"
        }.get(level, "INFO")
    
    def _log(self, level, message):
        """Internal logging method."""
        if level < self.min_level:
            return
            
        level_name = self._get_level_name(level)
        timestamp = self._get_timestamp()
        
        # Format: [TIMESTAMP] [LEVEL] [MODULE] Message
        log_message = f"[{timestamp}] [{level_name}] [{self.name}] {message}"
        
        # Add colors if enabled
        if self.use_colors:
            color = self.COLORS.get(level_name, self.COLORS['RESET'])
            log_message = f"{color}{log_message}{self.COLORS['RESET']}"
            
        print(log_message, file=sys.stdout if level < self.ERROR else sys.stderr)
        sys.stdout.flush() if level < self.ERROR else sys.stderr.flush()
    
    def debug(self, message):
        """Log a debug message."""
        self._log(self.DEBUG, message)
    
    def info(self, message):
        """Log an info message."""
        self._log(self.INFO, message)
    
    def warning(self, message):
        """Log a warning message."""
        self._log(self.WARNING, message)
    
    def error(self, message):
        """Log an error message."""
        self._log(self.ERROR, message)
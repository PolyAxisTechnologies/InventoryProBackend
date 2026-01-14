import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# Create logs directory if it doesn't exist
import sys

# Create logs directory if it doesn't exist
if getattr(sys, 'frozen', False):
    # If running as bundled app, store logs in AppData
    app_data = os.getenv('APPDATA')
    LOGS_DIR = os.path.join(app_data, "InventoryPro", "logs")
else:
    # If running in dev, store in local logs folder
    LOGS_DIR = "logs"

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Get current date for log filename
current_date = datetime.now().strftime("%Y-%m-%d")
log_file = os.path.join(LOGS_DIR, f"{current_date}.log")

# Create logger
logger = logging.getLogger("inventory_app")
logger.setLevel(logging.DEBUG)

# Create formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

simple_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File handler - Daily rotating logs
file_handler = TimedRotatingFileHandler(
    log_file,
    when='midnight',
    interval=1,
    backupCount=60,  # Keep 60 days of logs
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_formatter)
file_handler.suffix = "%Y-%m-%d.log"

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(simple_formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent propagation to root logger
logger.propagate = False


def get_logger():
    """Get the configured logger instance"""
    return logger

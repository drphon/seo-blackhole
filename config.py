import logging
from pathlib import Path
import sys
from datetime import datetime
import os
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Base directories
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'output'
LOG_DIR = OUTPUT_DIR / 'logs'

# Create directories
for dir_path in [OUTPUT_DIR, LOG_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Basic configuration
CONFIG = {
    'VERSION': '1.0.0',
    'USER': os.getenv('COMPUTERNAME', 'default_user'),  # Changed from USERNAME to COMPUTERNAME
    'DEBUG': False,
    'MAX_RETRIES': 3,
    'TIMEOUT': 30,
}

# Set up console logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter(
    '%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(console_format)

# Set up file logging
file_handler = logging.FileHandler(LOG_DIR / 'debug.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_format)

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def get_logger(name):
    return logging.getLogger(name)
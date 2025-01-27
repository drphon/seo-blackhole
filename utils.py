from tqdm import tqdm
import random
import time
from datetime import datetime
from colorama import Fore, Back, Style
import requests
from typing import Optional, Tuple
from config import CONFIG, logger

class ProgressBar:
    def __init__(self, total: int, desc: str = ""):
        self.start_time = datetime.utcnow()
        self.pbar = tqdm(
            total=total,
            desc=f"{Fore.CYAN}[{self.start_time}] {desc}{Style.RESET_ALL}",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        )
    
    def update(self, n: int = 1):
        self.pbar.update(n)
    
    def close(self):
        self.pbar.close()
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        print(f"{Fore.GREEN}[{end_time}] Completed in {duration:.2f} seconds{Style.RESET_ALL}")

class DelayManager:
    def __init__(self):
        self.base_delay_range = CONFIG['DELAY_RANGE']
        self.captcha_delay_range = CONFIG['CAPTCHA_DELAY_RANGE']
        self.captcha_encountered = False
    
    def get_delay(self) -> float:
        if self.captcha_encountered:
            delay = random.uniform(*self.captcha_delay_range)
            print(f"{Fore.YELLOW}[{datetime.utcnow()}] CAPTCHA detected, increasing delay to {delay:.2f}s{Style.RESET_ALL}")
        else:
            delay = random.uniform(*self.base_delay_range)
            print(f"{Fore.BLUE}[{datetime.utcnow()}] Normal delay: {delay:.2f}s{Style.RESET_ALL}")
        return delay
    
    def reset(self):
        self.captcha_encountered = False
        print(f"{Fore.GREEN}[{datetime.utcnow()}] Delay manager reset{Style.RESET_ALL}")

class NetworkManager:
    @staticmethod
    def safe_request(url: str, method: str = 'GET', timeout: int = None, **kwargs) -> Optional[requests.Response]:
        if timeout is None:
            timeout = CONFIG['TIMEOUT']
        
        for attempt in range(CONFIG['MAX_RETRIES']):
            try:
                response = requests.request(method, url, timeout=timeout, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                print(f"{Fore.RED}[{datetime.utcnow()}] Request failed (attempt {attempt + 1}/{CONFIG['MAX_RETRIES']}): {str(e)}{Style.RESET_ALL}")
                if attempt == CONFIG['MAX_RETRIES'] - 1:
                    logger.error(f"All requests failed for URL {url}: {str(e)}")
                    return None
                time.sleep(random.uniform(1, 3))
        return None

def safe_sleep(seconds: float):
    """Safe delay with progress indication"""
    start_time = datetime.utcnow()
    print(f"{Fore.BLUE}[{start_time}] Waiting for {seconds:.1f} seconds...{Style.RESET_ALL}")
    time.sleep(seconds)
    end_time = datetime.utcnow()
    print(f"{Fore.GREEN}[{end_time}] Wait completed{Style.RESET_ALL}")

def format_size(size: int) -> str:
    """Format file size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def get_timestamp() -> str:
    """Get current timestamp in formatted string"""
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

def print_status(message: str, status: str = 'info'):
    """Print colored status message with timestamp"""
    colors = {
        'info': Fore.CYAN,
        'success': Fore.GREEN,
        'warning': Fore.YELLOW,
        'error': Fore.RED
    }
    color = colors.get(status.lower(), Fore.WHITE)
    print(f"{color}[{get_timestamp()}] {message}{Style.RESET_ALL}")
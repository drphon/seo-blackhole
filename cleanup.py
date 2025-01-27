import shutil
from pathlib import Path
from datetime import datetime
import os
from colorama import Fore, Style, init
import logging
import json

# Initialize colorama
init(autoreset=True)

def setup_logging():
    """Setup logging configuration"""
    log_file = Path(__file__).parent / 'cleanup_log.txt'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def write_summary(summary_data):
    """Write cleanup summary to JSON file"""
    summary_file = Path(__file__).parent / 'cleanup_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=4, ensure_ascii=False)

def clean_directories():
    """Clean and organize files in the project directories"""
    logger = setup_logging()
    start_time = datetime.now()
    
    try:
        base_dir = Path(__file__).parent
        temp_dir = base_dir / 'output' / 'temp'
        archive_dir = base_dir / 'output' / 'archive'
        
        # Create directories if they don't exist
        temp_dir.mkdir(parents=True, exist_ok=True)
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting cleanup process at {start_time}")
        print(f"{Fore.CYAN}Starting cleanup process...{Style.RESET_ALL}")
        
        # Statistics
        stats = {
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'files_processed': 0,
            'files_moved': 0,
            'files_kept': 0,
            'directories_processed': 0,
            'actions': []
        }
        
        # List of important file extensions to keep
        important_extensions = {'.json', '.xlsx', '.csv', '.log', '.txt'}
        
        # Process all directories recursively
        for root, dirs, files in os.walk(base_dir):
            current_dir = Path(root)
            
            # Skip git directory and virtual environment
            if '.git' in dirs:
                dirs.remove('.git')
            if 'venv' in dirs:
                dirs.remove('venv')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
                
            stats['directories_processed'] += 1
            logger.info(f"Processing directory: {current_dir}")
            
            for file in files:
                file_path = current_dir / file
                stats['files_processed'] += 1
                
                # Skip if file is in temp or archive directory
                if temp_dir in file_path.parents or archive_dir in file_path.parents:
                    continue
                
                # Skip Python files and important project files
                if file_path.suffix in ['.py', '.md'] or file in ['requirements.txt', 'keywords.txt']:
                    continue
                
                action = {
                    'file': str(file_path),
                    'action': '',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Move to appropriate directory based on extension
                if file_path.suffix in important_extensions:
                    # Keep important files in output directory
                    if 'output' not in str(file_path):
                        new_path = base_dir / 'output' / file_path.name
                        shutil.move(str(file_path), str(new_path))
                        action['action'] = f"Moved to output: {file_path.name}"
                        stats['files_moved'] += 1
                    else:
                        action['action'] = f"Kept in output: {file_path.name}"
                        stats['files_kept'] += 1
                    logger.info(f"Keeping important file: {file_path.name}")
                    print(f"{Fore.GREEN}Keeping important file: {file_path.name}{Style.RESET_ALL}")
                else:
                    # Move other files to temp directory
                    new_path = temp_dir / file_path.name
                    shutil.move(str(file_path), str(new_path))
                    action['action'] = f"Moved to temp: {file_path.name}"
                    stats['files_moved'] += 1
                    logger.info(f"Moved to temp: {file_path.name}")
                    print(f"{Fore.YELLOW}Moved to temp: {file_path.name}{Style.RESET_ALL}")
                
                stats['actions'].append(action)
        
        # Update final statistics
        end_time = datetime.now()
        stats['end_time'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
        stats['duration'] = str(end_time - start_time)
        
        # Write summary
        write_summary(stats)
        
        # Log final statistics
        logger.info("\nCleanup Summary:")
        logger.info(f"Directories processed: {stats['directories_processed']}")
        logger.info(f"Files processed: {stats['files_processed']}")
        logger.info(f"Files moved: {stats['files_moved']}")
        logger.info(f"Files kept: {stats['files_kept']}")
        logger.info(f"Duration: {stats['duration']}")
        
        print(f"\n{Fore.GREEN}Cleanup completed successfully!{Style.RESET_ALL}")
        print(f"\nDirectory Structure:")
        print(f"└── Project Directory/")
        print(f"    ├── output/")
        print(f"    │   ├── Important files (.json, .xlsx, .csv, .log, .txt)")
        print(f"    │   ├── temp/ ({stats['files_moved']} non-essential files)")
        print(f"    │   └── archive/ (For future use)")
        print(f"    ├── cleanup_log.txt (Detailed log of all actions)")
        print(f"    └── cleanup_summary.json (Statistical summary)")
        
    except Exception as e:
        error_msg = f"Error during cleanup: {str(e)}"
        logger.error(error_msg)
        print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")

if __name__ == "__main__":
    clean_directories()
    print(f"\n{Fore.CYAN}Check cleanup_log.txt for detailed information{Style.RESET_ALL}")
    input("\nPress Enter to exit...")
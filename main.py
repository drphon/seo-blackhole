#!/usr/bin/env python3
from pathlib import Path
import time
from datetime import datetime
import logging
from tqdm import tqdm
import json
from config import CONFIG, logger
from web_scraper import WebScraper

def main():
    try:
        # Print banner
        print("=" * 50)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Current Date and Time: {current_time}")
        print(f"Computer Name: {CONFIG['USER']}")  # Changed from User's Login to Computer Name
        print(f"Version: {CONFIG['VERSION']}")
        print("=" * 50)
        print()

        # Load keywords
        logger.info("Loading keywords...")
        with open('keywords.txt', 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(keywords)} keywords")

        # Initialize scraper
        logger.info("Initializing scraper...")
        scraper = WebScraper()
        
        # Process keywords
        all_results = {}
        for keyword in tqdm(keywords, desc="Processing keywords"):
            try:
                results = scraper.search_google(keyword)
                if results:
                    all_results[keyword] = results
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error processing keyword '{keyword}': {str(e)}")
                continue

        # Save results
        if all_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = Path('output') / f'results_{timestamp}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=4)
            logger.info(f"Results saved to {output_file}")
        else:
            logger.warning("No results were collected")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
    
    finally:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
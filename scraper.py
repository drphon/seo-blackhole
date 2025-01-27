from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json
import time
from datetime import datetime
from pathlib import Path

class GoogleScraper:
    def __init__(self):
        self.setup_driver()
        
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def search_and_extract(self, keyword):
        results = []
        
        try:
            # Go to Google
            self.driver.get('https://www.google.com')
            time.sleep(2)
            
            # Find search box and enter keyword
            search_box = self.wait.until(EC.presence_of_element_located((By.NAME, 'q')))
            search_box.clear()
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)
            
            # Get results from first page
            results.extend(self._extract_results())
            
            # Try to get second page results
            try:
                next_button = self.wait.until(EC.element_to_be_clickable((By.ID, 'pnnext')))
                next_button.click()
                time.sleep(2)
                results.extend(self._extract_results())
            except:
                print("Could not access second page")
                
            return results
            
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return results
    
    def _extract_results(self):
        results = []
        elements = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.g')))
        
        for element in elements:
            try:
                title = element.find_element(By.CSS_SELECTOR, 'h3').text
                link = element.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                desc = element.find_element(By.CSS_SELECTOR, 'div.VwiC3b').text
                
                if title and link:
                    results.append({
                        'title': title,
                        'link': link,
                        'description': desc,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
            except:
                continue
                
        return results
    
    def save_results(self, keyword, results):
        if not results:
            return
            
        # Create output directory
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_file = output_dir / f'results_{keyword}_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
            
        # Save as Excel
        df = pd.DataFrame(results)
        excel_file = output_dir / f'results_{keyword}_{timestamp}.xlsx'
        df.to_excel(excel_file, index=False)
        
        print(f"\nSaved results for '{keyword}':")
        print(f"JSON: {json_file}")
        print(f"Excel: {excel_file}")
        
    def close(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    # Read keywords
    with open('keywords.txt', 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(keywords)} keywords to process")
    
    # Initialize scraper
    scraper = GoogleScraper()
    
    try:
        # Process each keyword
        for keyword in keywords:
            print(f"\nProcessing: {keyword}")
            results = scraper.search_and_extract(keyword)
            print(f"Found {len(results)} results")
            scraper.save_results(keyword, results)
            time.sleep(2)  # Delay between searches
            
    finally:
        scraper.close()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
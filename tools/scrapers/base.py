from abc import ABC, abstractmethod
from typing import Dict, Optional, List
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    @abstractmethod
    def fetch(self, url: str) -> Optional[str]:
        """Fetch content from the URL."""
        pass

    @abstractmethod
    def parse(self, content: str) -> List[Dict]:
        """Parse the content and return a list of product dictionaries."""
        pass

    def save(self, products: List[Dict]):
        """Save scraped products to a CSV file."""
        if not products:
            return

        import csv
        import os
        
        filename = "scraped_data.csv"
        file_exists = os.path.isfile(filename)
        
        # Define fieldnames based on the first product (or a fixed list)
        keys = ["sku_id", "product_name", "images", "source", "price", "description", "specifications", "datasheet_url"]
        
        try:
            with open(filename, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
                
                if not file_exists:
                    writer.writeheader()
                    
                for p in products:
                    writer.writerow(p)
                    
            logger.info(f"Saved {len(products)} products to {filename}")
        except Exception as e:
            logger.error(f"Failed to save CSV: {e}")

    def run(self, start_url: str):
        """Main execution flow."""
        logger.info(f"Starting scrape from {start_url}")
        content = self.fetch(start_url)
        if content:
            products = self.parse(content)
            self.save(products)
        else:
            logger.error("Failed to fetch content.")

import time
import logging
import random
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseScraper

logger = logging.getLogger(__name__)

class SickScraper(BaseScraper):
    """
    Scraper for SICK (sick.com) using Selenium to handle dynamic content.
    Extracts product details, specifications, images, and datasheets.
    """
    def __init__(self, headless=True):
        super().__init__("https://www.sick.com")
        self.headless = headless
        self.driver = self._setup_driver()

    def _setup_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222") # Helps in some container envs
        # Explicitly set binary location for the container
        chrome_options.binary_location = "/usr/bin/chromium"
        chrome_options.add_argument("--window-size=1920,1080")
        # Anti-detection headers
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # In a real environment, you might need to use a remote driver or specify path
        # driver = webdriver.Chrome(options=chrome_options)
        # Using remote for Docker compatibility if configured, else local
        try:
            # Attempt to connect to a remote webdriver if in docker-compose network
            # driver = webdriver.Remote(command_executor='http://selenium:4444/wd/hub', options=chrome_options)
            driver = webdriver.Chrome(options=chrome_options) 
        except Exception:
             # Fallback to local execution
            driver = webdriver.Chrome(options=chrome_options)
            
        return driver

    def fetch(self, url: str) -> Optional[str]:
        """Fetch dynamic page content using Selenium"""
        try:
            logger.info(f"Navigating to {url}")
            self.driver.get(url)
            
            # Wait for main content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scroll down to trigger lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2) # Allow JS to execute
            
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def parse(self, content: str) -> List[Dict]:
        """
        In BaseScraper, parse expects to return a List[Dict] (multiple products).
        However, our logic currently extracts a SINGLE product from a product page,
        or finds links from a category page.
        
        To adapt to the BaseScraper interface:
        If the content looks like a product page, return [product].
        If it looks like a category page, we might need a different approach or 
        this method should strictly parse a product page.
        
        For now, let's assume 'content' is a product page source.
        """
        html = content
        # We don't have the URL here easily unless we store it in the class state 
        # or change BaseScraper signature. 
        # For now, let's use a dummy URL or current driver URL if available.
        url = self.driver.current_url if self.driver else "unknown"
        
        soup = BeautifulSoup(html, 'html.parser')
        product = {
            "source": "SICK",
            "url": url,
            "language": "en"
        }

        # 1. Product Name
        title_elem = soup.find('h1', class_='product-title') or soup.find('h1')
        product['product_name'] = title_elem.text.strip() if title_elem else "Unknown Product"

        # If we failed to find a title, it might be a category page or invalid
        if product['product_name'] == "Unknown Product":
             # Try to see if it's a list page
             pass 

        # 2. SKU / Part Number ... (rest of extraction logic)
        sku_elem = soup.find('span', class_='product-id') or soup.find(text=lambda t: 'Part no.' in str(t))
        product['sku_id'] = sku_elem.text.replace('Part no.:', '').strip() if sku_elem else None

        # 3. Description
        desc_elem = soup.find('div', class_='product-description')
        product['description'] = desc_elem.text.strip() if desc_elem else ""

        # 4. Specifications
        specs = {}
        spec_table = soup.find('table', class_='tech-data') 
        if spec_table:
            rows = spec_table.find_all('tr')
            for row in rows:
                cols = row.find_all(['th', 'td'])
                if len(cols) == 2:
                    key = cols[0].text.strip()
                    val = cols[1].text.strip()
                    specs[key] = val
        product['specifications'] = specs

        # 5. Images
        images = []
        img_elems = soup.find_all('img', class_='product-image')
        for img in img_elems:
            src = img.get('src')
            if src:
                if not src.startswith('http'):
                    src = "https://www.sick.com" + src
                images.append(src)
        product['images'] = images

        # 6. Datasheet
        pdf_link = soup.find('a', href=lambda h: h and '.pdf' in h and 'datasheet' in h.lower())
        if pdf_link:
            href = pdf_link['href']
            product['datasheet_url'] = "https://www.sick.com" + href if not href.startswith('http') else href
        else:
            product['datasheet_url'] = None

        return [product]

    def scrape_category(self, start_url: str, max_products=10):
        """
        Crawls the category using BFS to find products.
        Structure: Category -> ... -> Family -> Product
        """
        all_products = []
        visited = set()
        queue = [(start_url, 0)] # (url, depth)
        
        # Max depth to prevent infinite crawling
        MAX_DEPTH = 4 
        
        while queue and len(all_products) < max_products:
            current_url, depth = queue.pop(0)
            
            if current_url in visited:
                continue
            visited.add(current_url)
            
            if depth > MAX_DEPTH:
                continue

            logger.info(f"Crawling [Depth {depth}]: {current_url}")
            content = self.fetch(current_url)
            if not content:
                continue
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. Identify Links (Sub-categories/Families OR Products)
            # Use specific selectors for cards if possible, mostly for /c/ links
            card_links = soup.select('ui-category-record-card a')
            if not card_links:
                # Fallbck for lists
                card_links = soup.find_all('a', href=lambda h: h and ('/products/' in h) and ('/c/' in h or '/p/' in h))

            # Also verify if we are on a table view (product variants list)
            # Sometimes a family page lists products in a table, not cards
            table_links = soup.select('table a.product-link') # Hypothetical
            if table_links:
                 card_links.extend(table_links)

            # 2. Process Links
            found_p_links = []
            found_c_links = []

            for link in card_links:
                href = link.get('href')
                if not href: continue
                
                # Cleanup URL
                if not href.startswith('http'):
                    href = "https://www.sick.com" + href if href.startswith('/') else "https://www.sick.com/" + href
                
                # Filter out garbage
                if 'javascript:' in href or '#' in href or 'mailto:' in href:
                    continue

                if '/p/' in href:
                    found_p_links.append(href)
                elif '/c/' in href:
                    found_c_links.append(href)
            
            # 3. If we found products, scrape them!
            unique_p_links = list(set(found_p_links))
            logger.info(f"  Found {len(unique_p_links)} products and {len(found_c_links)} sub-categories")
            
            for p_url in unique_p_links:
                if len(all_products) >= max_products: break
                
                if p_url not in visited:
                    p_data = self._scrape_product_page(p_url)
                    if p_data:
                        all_products.extend(p_data)
                        visited.add(p_url)
                        time.sleep(1) 
            
            # 4. If we didn't fill our quota and have sub-categories, add them to queue
            # Prioritize crawling deeper
            # 4. If we didn't fill our quota and have sub-categories, add them to queue
            # Optimization: If a category has many sub-categories but ZERO products, 
            # and we are already deep, it's likely a navigation hub. 
            # To "focus on links with products", we can deprioritize or skip huge empty hubs at depth > 1.
            
            if len(all_products) < max_products:
                if len(unique_p_links) == 0 and len(found_c_links) > 5 and depth > 1:
                     logger.info("  Skipping deep empty category to focus on products...")
                     continue

                for c_url in found_c_links:
                    if c_url not in visited:
                        # Add to queue with incremented depth
                        queue.append((c_url, depth + 1))
            
            time.sleep(1)

        return all_products

    def _scrape_product_page(self, url: str) -> List[Dict]:
        """Helper to fetch and parse a specific product page"""
        logger.info(f"Scraping Product: {url}")
        content = self.fetch(url)
        if content:
            data = self.parse(content)
            # Validate it's a real product by checking SKU or Name validity
            if data and data[0].get('product_name') != "Unknown Product" and not data[0].get('product_name').strip() == "":
                 logger.info(f"  Success: {data[0].get('product_name')}")
                 return data
            else:
                 logger.warning(f"  Skipping {url} - Failed to parse valid product data")
        return []



    def close(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    # Test run
    logging.basicConfig(level=logging.INFO)
    scraper = SickScraper(headless=True)
    try:
        # Example category
        results = scraper.scrape_category("https://www.sick.com/us/en/products/c/g64893")
        print(f"Scraped {len(results)} products")
    finally:
        scraper.close()

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

    def scrape_category(self, category_url: str, max_pages=1):
        """
        Iterate through category pages. 
        SICK structure: Category -> Family (/c/) -> Product Variant (/p/)
        """
        all_products = []
        
        # 1. Fetch the main category page
        logger.info(f"Fetching category: {category_url}")
        content = self.fetch(category_url)
        if not content:
            return []

        soup = BeautifulSoup(content, 'html.parser')
        
        # 2. Identify links
        # We look for both /p/ (direct product) and /c/ (sub-category/family)
        # SICK usually lists Families (/c/) on high level pages
        
        # Primary selector for cards
        card_links = soup.select('ui-category-record-card a')
        if not card_links:
            # Fallback generic
            card_links = soup.find_all('a', href=lambda h: h and ('/products/' in h) and ('/c/' in h or '/p/' in h))

        product_urls = set()
        family_urls = set()

        for link in card_links:
            href = link.get('href')
            if not href: continue
            
            # Normalize URL
            if not href.startswith('http'):
                 href = "https://www.sick.com" + href if href.startswith('/') else "https://www.sick.com/" + href
            
            if '/p/' in href:
                product_urls.add(href)
            elif '/c/' in href:
                family_urls.add(href)

        logger.info(f"Found {len(product_urls)} direct products and {len(family_urls)} families/subcategories")

        # 3. If we found DIRECT products, scrape them
        for p_url in list(product_urls)[:5]: # Limit
            products = self._scrape_product_page(p_url)
            all_products.extend(products)
            if products: 
                 time.sleep(1)

        # 4. If we found FAMILIES, drill down (depth 1) to find products inside them
        # Only do this if we didn't find enough direct products, or to be thorough
        if family_urls and len(all_products) < 5:
            logger.info("Drilling down into families to find products...")
            for f_url in list(family_urls)[:3]: # Limit families to verify first
                logger.info(f"Inspecting Family: {f_url}")
                f_content = self.fetch(f_url)
                if not f_content: continue
                
                f_soup = BeautifulSoup(f_content, 'html.parser')
                # On a family page, we look specifically for /p/ links
                # determining the selector might be tricky, let's try a broad search for /p/ first
                p_links = f_soup.find_all('a', href=lambda h: h and '/p/' in h)
                
                found_new_p_urls = set()
                for pl in p_links:
                    phref = pl.get('href')
                    if not phref: continue
                    if not phref.startswith('http'):
                         phref = "https://www.sick.com" + phref if phref.startswith('/') else "https://www.sick.com/" + phref
                    found_new_p_urls.add(phref)
                
                logger.info(f"  Found {len(found_new_p_urls)} variants in family")
                
                for p_url in list(found_new_p_urls)[:2]: # Limit variants per family
                    products = self._scrape_product_page(p_url)
                    all_products.extend(products)
                    if len(all_products) >= 10: break # Overall safety limit
                    time.sleep(1)
                
                if len(all_products) >= 10: break

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

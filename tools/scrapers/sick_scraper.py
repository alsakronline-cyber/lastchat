import time
import logging
import random
import json
import hashlib
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
        chrome_options.add_argument("--remote-debugging-port=9222")
        # chrome_options.binary_location = "/usr/bin/chromium" # Do not set this for Remote WebDriver
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # Connect to Docker Selenium (localhost:4444)
            logger.info("Connecting to Remote Selenium (Docker)...")
            driver = webdriver.Remote(
                command_executor='http://localhost:4444/wd/hub',
                options=chrome_options
            )
        except Exception as e:
            logger.warning(f"Remote Selenium failed, trying local Chrome: {e}")
            driver = webdriver.Chrome(options=chrome_options)
            
        return driver

    def fetch(self, url: str) -> Optional[str]:
        """Fetch dynamic page content using Selenium"""
        try:
            logger.info(f"Navigating to {url}")
            self.driver.get(url)
            
            # Wait for main content
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scroll to trigger lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def parse(self, content: str, url: str = "", category_path: str = "") -> List[Dict]:
        """
        Parses a SICK product page.
        """
        soup = BeautifulSoup(content, 'html.parser')
        product = {
            "source": "SICK",
            "url": url,
            "language": "en",
            "category": category_path
        }

        # 1. Product Name & Family
        title_elem = soup.find('h1', class_='product-title') or soup.find('h1')
        product['product_name'] = title_elem.text.strip() if title_elem else "Unknown Product"
        
        # Family Group (e.g. from breadcrumb or title prefix)
        # Attempt to get breadcrumb
        breadcrumb_items = soup.select('.breadcrumb li')
        if breadcrumb_items and len(breadcrumb_items) > 1:
            # Usually Home > Products > Category > Family > Product
             parents = [b.get_text(strip=True) for b in breadcrumb_items]
             product['family_group'] = parents[-2] if len(parents) >= 2 else "Unknown"
             if not product['category']:
                 product['category'] = " > ".join(parents[2:-1]) # refined category path
        else:
            product['family_group'] = "Unknown"

        # 2. SKU / Part Number
        sku_elem = soup.select_one('ui-product-part-number .font-bold') or \
                   soup.select_one('.buy-box .font-bold') or \
                   soup.find('span', class_='product-id')
                   
        if sku_elem:
            product['sku_id'] = sku_elem.get_text(strip=True).replace('Part no.:', '').strip()
        
        if not product.get('sku_id'):
            # Fallback to URL parsing
            url_part = url.split('/p/')[-1].split('?')[0] if '/p/' in url else ""
            if url_part:
                product['sku_id'] = url_part
            else:
                product['sku_id'] = f"unknown-{hashlib.md5(url.encode()).hexdigest()[:8]}"

        # 3. Description
        desc_elem = soup.find('div', class_='product-description') or \
                   soup.find('div', itemprop='description') or \
                   soup.find('meta', attrs={'name': 'description'})
        
        if desc_elem:
            if desc_elem.name == 'meta':
                product['description'] = desc_elem.get('content', '').strip()
            else:
                product['description'] = desc_elem.get_text(strip=True)
        else:
            product['description'] = ""

        # 4. Specifications (Detailed)
        specs = {}
        # SICK usually has multiple tables or definition lists
        tables = soup.find_all('table')
        for table in tables:
             # Check if it looks like a spec table
             rows = table.find_all('tr')
             for row in rows:
                 cols = row.find_all(['th', 'td'])
                 if len(cols) == 2:
                     k = cols[0].get_text(strip=True)
                     v = cols[1].get_text(strip=True)
                     specs[k] = v
        
        # Also check for dl/dt/dd structure common in newer web designs
        dls = soup.find_all('dl')
        for dl in dls:
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            if len(dts) == len(dds):
                for k, v in zip(dts, dds):
                    specs[k.get_text(strip=True)] = v.get_text(strip=True)

        product['specifications'] = specs

        # 5. Images
        images = []
        # Main gallery
        img_elems = soup.select('.product-gallery img') or soup.find_all('img', class_='product-image')
        for img in img_elems:
            src = img.get('src') or img.get('data-src')
            if src:
                if not src.startswith('http'):
                    src = "https://www.sick.com" + src
                images.append(src)
        product['images'] = list(set(images)) # Unique

        # 6. Datasheet / PDF
        # Look specifically for datasheet links
        # 6. Documents (Datasheets, CAD, etc.)
        documents = []
        # Find all PDF links or download links
        # SICK usually puts them in a specific 'Downloads' section or under 'Technical data'
        doc_links = soup.select('a[href$=".pdf"]')
        for link in doc_links:
            href = link.get('href')
            if not href: continue
            
            # Normalize
            full_url = "https://www.sick.com" + href if href.startswith('/') else href
            
            # Title
            title = link.get_text(strip=True) or link.get('title') or "Document"
            
            # Categorize document
            doc_type = "other"
            lower_href = href.lower()
            lower_title = title.lower()
            
            if 'datasheet' in lower_href or 'data sheet' in lower_title:
                doc_type = "datasheet"
            elif 'manual' in lower_href or 'operating instructions' in lower_title:
                 doc_type = "manual"
            elif 'cad' in lower_href:
                 doc_type = "cad"
                 
            documents.append({
                "title": title,
                "url": full_url,
                "type": doc_type
            })
            
        product['documents'] = documents
        
        # Backwards compatibility
        ds = next((d for d in documents if d['type'] == 'datasheet'), None)
        product['datasheet_url'] = ds['url'] if ds else None

        # 7. Technical Drawings / Diagrams
        # Often mixed with images, but sometimes separate. 
        # Check for images with specific classes or alt text indicating a drawing
        technical_drawings = []
        
        # Re-scan images for specific markers
        all_imgs = soup.find_all('img')
        for img in all_imgs:
            src = img.get('src') or img.get('data-src')
            if not src: continue
            
            alt = (img.get('alt') or "").lower()
            src_lower = src.lower()
            
            if 'dimension' in alt or 'drawing' in alt or 'diagram' in alt or 'connection' in alt:
                if not src.startswith('http'):
                    src = "https://www.sick.com" + src
                technical_drawings.append(src)
                
        product['technical_drawings'] = list(set(technical_drawings))
        
        # 8. Custom Data
        # Any other metadata we can find, e.g., features lists
        custom_data = {}
        features_list = soup.select('.product-features li')
        if features_list:
            custom_data['features'] = [f.get_text(strip=True) for f in features_list]
            
        product['custom_data'] = custom_data

        return [product]

    def scrape_category(self, start_url: str, max_products=20):
        """
        Crawls the category using BFS to find products.
        """
        all_products = []
        visited = set()
        queue = [(start_url, 0)] # (url, depth)
        MAX_DEPTH = 3
        
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
            
            # Determine if this is a Product Page or Category Page
            # A simple heuristic: check for "Add to cart" or specific product ID elements
            # Or reliance on URL patterns provided by the loop logic below.
            
            # 1. Identify Links
            links = []
            
            # Category/Product Cards
            card_links = soup.select('a') # refined below
            
            found_p_links = []
            found_c_links = []
            
            for link in card_links:
                href = link.get('href')
                if not href: continue
                
                # Normalize
                if not href.startswith('http'):
                    href = "https://www.sick.com" + href if href.startswith('/') else "https://www.sick.com/" + href
                
                # Exclusions
                if any(x in href for x in ['javascript:', 'mailto:', '#', 'login', 'register']):
                    continue
                
                # SICK URL Patterns
                # Product: /p/p123456
                # Category: /c/g123456
                
                if '/p/' in href:
                    found_p_links.append(href)
                elif '/products/' in href or '/catalog/' in href or '/c/' in href:
                    # Avoid back-tracking to high level pages usually shorter than current
                    if len(href) > len("https://www.sick.com/us/en"): 
                        found_c_links.append(href)

            # Unique
            unique_p_links = list(set(found_p_links))
            unique_c_links = list(set(found_c_links))
            
            logger.info(f"  Found {len(unique_p_links)} products and {len(unique_c_links)} sub-links")

            # Scrape products found on THIS page
            for p_url in unique_p_links:
                if len(all_products) >= max_products: break
                if p_url not in visited:
                    # Pass context if possible, but for now just URL
                    p_data = self._scrape_product_page(p_url)
                    if p_data:
                        all_products.extend(p_data)
                        visited.add(p_url)
            
            # Add sub-categories to queue
            # Prioritize product-looking links? No, BFS is fine.
            if len(all_products) < max_products:
                for c_url in unique_c_links:
                    if c_url not in visited:
                        queue.append((c_url, depth + 1))
            
            time.sleep(1)

        return all_products

    def _scrape_product_page(self, url: str) -> List[Dict]:
        """Helper to fetch and parse a specific product page"""
        logger.info(f"Scraping Product: {url}")
        content = self.fetch(url)
        if content:
            # We can try to infer category from breadcrumbs inside parse
            data = self.parse(content, url=url)
            if data and data[0].get('product_name') != "Unknown Product":
                 logger.info(f"  Success: {data[0].get('product_name')}")
                 return data
        return []

    def close(self):
        if self.driver:
            self.driver.quit()

    def save_products(self, products: List[Dict]):
        """Save products to PostgreSQL database"""
        import os
        from sqlalchemy import create_engine, text
        
        DB_USER = os.getenv("POSTGRES_USER", "postgres")
        DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secure_password")
        DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
        DB_PORT = os.getenv("POSTGRES_PORT", "5432")
        DB_NAME = os.getenv("POSTGRES_DB", "automation_engine")
        
        # Prioritize DATABASE_URL if set (e.g. in Docker)
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
             DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                for p in products:
                    stmt = text("""
                        INSERT INTO products (
                            sku_id, product_name, category, family_group, 
                            description, specifications, images, 
                            technical_drawings, documents, custom_data,
                            datasheet_url
                        )
                        VALUES (
                            :sku_id, :product_name, :category, :family_group,
                            :description, :specifications, :images, 
                            :technical_drawings, :documents, :custom_data,
                            :datasheet_url
                        )
                        ON CONFLICT (sku_id) DO UPDATE SET
                            product_name = EXCLUDED.product_name,
                            category = EXCLUDED.category,
                            family_group = EXCLUDED.family_group,
                            description = EXCLUDED.description,
                            specifications = EXCLUDED.specifications,
                            images = EXCLUDED.images,
                            technical_drawings = EXCLUDED.technical_drawings,
                            documents = EXCLUDED.documents,
                            custom_data = EXCLUDED.custom_data,
                            datasheet_url = EXCLUDED.datasheet_url,
                            updated_at = NOW()
                    """)
                    
                    conn.execute(stmt, {
                        "sku_id": p.get("sku_id"),
                        "product_name": p.get("product_name"),
                        "category": p.get("category"),
                        "family_group": p.get("family_group"),
                        "description": p.get("description"),
                        "specifications": json.dumps(p.get("specifications", {})),
                        "images": json.dumps(p.get("images", [])),
                        "technical_drawings": json.dumps(p.get("technical_drawings", [])),
                        "documents": json.dumps(p.get("documents", [])),
                        "custom_data": json.dumps(p.get("custom_data", {})),
                        "datasheet_url": p.get("datasheet_url")
                    })
                    conn.commit()
            logger.info(f"Saved {len(products)} products to DB.")
        except Exception as e:
            logger.error(f"Failed to save to DB: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = SickScraper(headless=True)
    try:
        # Example: Fiber optic cables
        results = scraper.scrape_category("https://www.sick.com/us/en/catalog/products/detection-sensors/fiber-optic-sensors/fiber-optic-cables/c/g606165?tab=selection", max_products=5)
        print(f"Scraped {len(results)} products")
        if results:
            scraper.save_products(results)
    finally:
        scraper.close()

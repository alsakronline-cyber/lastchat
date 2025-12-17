import time
import logging
import random
import json
import hashlib
import os
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
        # chrome_options.add_argument("--remote-debugging-port=9222") # Often causes issues in remote/headless
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # Connect to Docker Selenium (service name 'selenium' from docker-compose)
            selenium_host = os.getenv("SELENIUM_HOST", "selenium")
            logger.info(f"Connecting to Remote Selenium at http://{selenium_host}:4444/wd/hub ...")
            driver = webdriver.Remote(
                command_executor=f'http://{selenium_host}:4444/wd/hub',
                options=chrome_options
            )
        except Exception as e:
            logger.warning(f"Remote Selenium failed, trying local Chrome: {e}")
            driver = webdriver.Chrome(options=chrome_options)
            
        return driver

    def fetch(self, url: str) -> Optional[str]:
        """Fetch dynamic page content using Selenium with Retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Navigating to {url} (Attempt {attempt+1}/{max_retries})")
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
                logger.warning(f"Error fetching {url}: {e}")
                time.sleep(2 * (attempt + 1)) # Backoff
                
        logger.error(f"Failed to fetch {url} after {max_retries} attempts.")
        return None

    def scrape_category(self, start_url: str, max_products=100, resume=False):
        """
        Crawls the category page with Resume capability.
        """
        all_products = []
        visited_urls = set()
        
        # Load checkpoint if resuming
        checkpoint_file = "scraped_urls.txt"
        if resume and os.path.exists(checkpoint_file):
            with open(checkpoint_file, "r") as f:
                visited_urls = set(line.strip() for line in f if line.strip())
            logger.info(f"Resumed: Loaded {len(visited_urls)} already scraped URLs.")
        
        logger.info(f"Navigating to {start_url}")
        self.driver.get(start_url)
        time.sleep(3)
        
        products_collected = 0
        while products_collected < max_products:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 1. Find Links
            page_links = soup.find_all('a', href=True)
            candidate_urls = []
            for link in page_links:
                href = link['href']
                if '/p/' in href:
                     if not href.startswith('http'):
                         href = "https://www.sick.com" + href if href.startswith('/') else "https://www.sick.com/" + href
                     candidate_urls.append(href)
                     
            unique_candidates = list(set(candidate_urls))
            logger.info(f"Found {len(unique_candidates)} visible products on page.")
            
            # 2. Process Candidates
            new_products_found = False
            for p_url in unique_candidates:
                if products_collected >= max_products:
                    break
                
                if p_url in visited_urls:
                    continue
                
                # Process
                visited_urls.add(p_url)
                
                # Open in new tab
                self.driver.execute_script(f"window.open('{p_url}', '_blank');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
                try:
                    p_data = self._scrape_product_page(p_url)
                    if p_data:
                        all_products.extend(p_data)
                        products_collected += 1
                        new_products_found = True
                        
                        # Save checkpoint immediately
                        with open(checkpoint_file, "a") as f:
                            f.write(p_url + "\n")
                except Exception as e:
                    logger.error(f"Error processing {p_url}: {e}")
                finally:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

            if products_collected >= max_products:
                break
            
            # 3. Load More / Pagination logic
            try:
                load_more_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Load more') or contains(text(), 'Show more')] | //a[contains(@class, 'load-more')]")
                if load_more_btn and load_more_btn.is_displayed():
                    logger.info("Clicking 'Load More'...")
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_btn)
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", load_more_btn)
                    time.sleep(3)
                else:
                    logger.info("No 'Load More' button found. End of list?")
                    break
            except Exception:
                # Scroll fallback
                logger.info("Scrolling down to trigger potential lazy load...")
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height and not new_products_found:
                    logger.info("Reached bottom and no new products found.")
                    break

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

    def parse(self, content: str, url: str = "", category_path: str = "") -> List[Dict]:
        """
        Parses a SICK product page (supports Shadow DOM / Web Components structure).
        """
        soup = BeautifulSoup(content, 'html.parser')
        product = {
            "source": "SICK",
            "url": url,
            "language": "en",
            "category": category_path
        }

        # 1. Product Name
        # Try Web Component Headline first
        title_elem = soup.select_one('ui-headline h1.headline span.title') or \
                     soup.find('h1', class_='product-title') or \
                     soup.find('h1')
        product['product_name'] = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
        
        # 2. Family & Category (Breadcrumbs)
        # Handle <syn-breadcrumb-item> structure
        breadcrumb_items = soup.find_all('syn-breadcrumb-item')
        if breadcrumb_items:
            # Extract text from the item, ignoring hidden separators
            parents = []
            for b in breadcrumb_items:
                # Text is usually direct or in an anchor
                text = b.get_text(strip=True)
                # Cleanup: sometimes contains "Home" or separators
                if text and "chevron" not in text.lower():
                    parents.append(text)
            
            # Usually: Home, Products, [Category...], Family, Product
            if len(parents) >= 2:
                product['family_group'] = parents[-2]
                if not product['category']:
                    product['category'] = " > ".join(parents[1:-1])
        else:
            # Fallback to old structure
            breadcrumb_items = soup.select('.breadcrumb li')
            if breadcrumb_items and len(breadcrumb_items) > 1:
                 parents = [b.get_text(strip=True) for b in breadcrumb_items]
                 product['family_group'] = parents[-2] if len(parents) >= 2 else "Unknown"
                 if not product['category']:
                     product['category'] = " > ".join(parents[2:-1])
            else:
                product['family_group'] = "Unknown"

        # 3. SKU / Part Number
        sku_elem = soup.select_one('ui-product-part-number .font-bold') or \
                   soup.select_one('.buy-box .font-bold') or \
                   soup.find('span', class_='product-id')
                   
        if sku_elem:
            product['sku_id'] = sku_elem.get_text(strip=True).replace('Part no.:', '').strip()
        
        if not product.get('sku_id'):
            url_part = url.split('/p/')[-1].split('?')[0] if '/p/' in url else ""
            if url_part:
                product['sku_id'] = url_part
            else:
                product['sku_id'] = f"unknown-{hashlib.md5(url.encode()).hexdigest()[:8]}"

        # 4. Description
        desc_elem = soup.find('div', class_='product-description') or \
                   soup.find('div', itemprop='description') or \
                   soup.find('meta', attrs={'name': 'description'})
        
        # In the new UI, description might be the Category link text inside headline?
        # e.g. "Fiber-optic sensors: Fiber-optic cables"
        if not desc_elem:
             desc_link = soup.select_one('ui-headline a span.category')
             if desc_link:
                 product['description'] = desc_link.get_text(strip=True)
             else:
                 product['description'] = ""
        else:
            if desc_elem.name == 'meta':
                product['description'] = desc_elem.get('content', '').strip()
            else:
                product['description'] = desc_elem.get_text(strip=True)

        # 5. Specifications
        specs = {}
        # New UI: div.tech-table table
        tables = soup.select('.tech-table table') or soup.find_all('table')
        for table in tables:
             rows = table.find_all('tr')
             for row in rows:
                 cols = row.find_all(['th', 'td'])
                 if len(cols) == 2:
                     k = cols[0].get_text(strip=True)
                     v = cols[1].get_text(strip=True)
                     if k and v:
                        specs[k] = v
        product['specifications'] = specs

        # 6. Images & Drawings
        images = []
        technical_drawings = []
        
        # Use a broad search for images in relevant sections
        all_imgs = soup.find_all('img')
        for img in all_imgs:
            src = img.get('src') or img.get('data-src')
            if not src: continue
            
            # Normalize URL
            if not src.startswith('http'):
                src = "https://www.sick.com" + src
                
            alt = (img.get('alt') or "").lower()
            title = (img.get('title') or "").lower()
            
            # Classification
            if 'dimension' in alt or 'drawing' in alt or 'diagram' in alt:
                technical_drawings.append(src)
            elif 'product' in alt or 'product' in title or 'gallery' in img.find_parent(class_=True, recursive=True).__str__():
                 images.append(src)
            elif 'im00' in src.lower(): # SICK Image format often IM00xxxxx
                 images.append(src)
                 
        product['images'] = list(set(images))
        product['technical_drawings'] = list(set(technical_drawings))

        # 7. Documents
        documents = []
        # Check standard PDF links
        doc_links = soup.select('a[href$=".pdf"]')
        for link in doc_links:
            href = link.get('href')
            full_url = "https://www.sick.com" + href if href.startswith('/') else href
            title = link.get_text(strip=True) or "Document"
            
            doc_type = "other"
            if 'datasheet' in title.lower(): doc_type = "datasheet"
            
            documents.append({"title": title, "url": full_url, "type": doc_type})
            
        # Check for UI Split Button (Datasheet)
        # Since we can't easily get the link from a button without JS execution, 
        # we might rely on constructing it or checking if it was captured.
        # For now, if documents is empty, we might leave it.
        # Often scraping text "Product data sheet" nearby might hint availability.
        
        product['documents'] = documents
        ds = next((d for d in documents if d['type'] == 'datasheet'), None)
        product['datasheet_url'] = ds['url'] if ds else None

        # 8. Custom Data
        custom_data = {}
        features_list = soup.select('.product-features li')
        if features_list:
            custom_data['features'] = [f.get_text(strip=True) for f in features_list]
        product['custom_data'] = custom_data

        return [product]

    def close(self):
        if self.driver:
            self.driver.quit()

    def save_products(self, products: List[Dict]):
        """Save products to PostgreSQL database"""
        from sqlalchemy import create_engine, text
        
        DB_USER = os.getenv("POSTGRES_USER", "postgres")
        DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secure_password")
        DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
        DB_PORT = os.getenv("POSTGRES_PORT", "5432")
        DB_NAME = os.getenv("POSTGRES_DB", "automation_engine")
        
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape SICK products.")
    parser.add_argument("--url", default="https://www.sick.com/us/en/catalog/products/detection-sensors/fiber-optic-sensors/fiber-optic-cables/c/g606165?tab=selection", help="SICK category URL to scrape")
    parser.add_argument("--limit", type=int, default=5, help="Max products to scrape")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (default: True)")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Run in visible mode")
    parser.add_argument("--resume", action="store_true", help="Resume from scraped_urls.txt checkpoint")
    parser.set_defaults(headless=True)
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    logger.info(f"Starting scraper with args: {args}")
    
    scraper = SickScraper(headless=args.headless)
    try:
        results = scraper.scrape_category(args.url, max_products=args.limit, resume=args.resume)
        print(f"Scraped {len(results)} products")
        if results:
            scraper.save_products(results)
    finally:
        scraper.close()

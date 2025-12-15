import time
import schedule
import logging
import importlib
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from tools.scrapers.sick_scraper import SickScraper
# Import other scrapers here when ready
# from tools.scrapers.abb_scraper import AbbScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ScraperScheduler")

def run_sick_scraper():
    logger.info("Starting scheduled SICK Scraper job...")
    try:
        scraper = SickScraper(headless=True)
        # Define target categories 
        categories = ["https://www.sick.com/us/en/products/c/g64893"] # Example
        for cat in categories:
            products = scraper.scrape_category(cat)
            logger.info(f"Successfully scraped {len(products)} products from {cat}")
            # TODO: Add ingestion step here
            # ingest_products(products)
        scraper.close()
        logger.info("SICK Scraper job completed.")
    except Exception as e:
        logger.error(f"SICK Scraper job failed: {e}")

def run_full_sync():
    logger.info("Starting Full Sync...")
    run_sick_scraper()
    # run_abb_scraper()
    # run_siemens_scraper()

# Schedule jobs
# Run every Monday at 02:00
schedule.every().monday.at("02:00").do(run_full_sync)

# Also run once on startup for verification if env var set
if os.getenv("RUN_ON_STARTUP") == "true":
    run_full_sync()

if __name__ == "__main__":
    logger.info("Scheduler started. Waiting for jobs...")
    while True:
        schedule.run_pending()
        time.sleep(60)

import argparse
from .sick_scraper import SickScraper
import logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Product Scrapers")
    parser.add_argument("--site", type=str, choices=["sick"], required=True, help="Site to scrape")
    parser.add_argument("--url", type=str, help="Starting URL")

    args = parser.parse_args()

    if args.site == "sick":
        scraper = SickScraper()
        start_url = args.url if args.url else "https://www.sick.com/us/en/"
        scraper.run(start_url)

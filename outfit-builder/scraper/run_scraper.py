import subprocess
import schedule
import time
from datetime import datetime

def run_spiders():
    """Run all spiders sequentially"""
    print(f"{datetime.now()}: Starting spiders...")
    
    spiders = ['hm', 'amazon', 'nordstrom']
    
    for spider in spiders:
        try:
            print(f"Running {spider} spider...")
            subprocess.run([
                'scrapy', 'crawl', spider,
                '-s', 'LOG_LEVEL=INFO'
            ], check=True)
            print(f"{spider} spider completed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error running {spider}: {e}")

def update_prices():
    """Update prices only for existing products"""
    subprocess.run([
        'scrapy', 'crawl', 'price_updater'
    ])

# Schedule daily updates
schedule.every().day.at("02:00").do(run_spiders)
schedule.every().day.at("14:00").do(update_prices)

if __name__ == "__main__":
    # Run immediately on startup
    run_spiders()
    
    # Keep running scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(60)
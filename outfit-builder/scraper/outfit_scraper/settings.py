BOT_NAME = 'outfit_scraper'

SPIDER_MODULES = ['outfit_scraper.spiders']
NEWSPIDER_MODULE = 'outfit_scraper.spiders'

# Obey robots.txt
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True

# Enable and configure middlewares
DOWNLOADER_MIDDLEWARES = {
    'outfit_scraper.middlewares.RotateUserAgentMiddleware': 400,
    'outfit_scraper.middlewares.RandomDelayMiddleware': 500,
    'outfit_scraper.middlewares.CustomRetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
}

# Enable Playwright for JavaScript-heavy sites
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Configure item pipelines
ITEM_PIPELINES = {
    'outfit_scraper.pipelines.DatabasePipeline': 300,
    'outfit_scraper.pipelines.DuplicatesPipeline': 100,
}

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [403, 429, 500, 502, 503, 504]

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Database settings
DATABASE_URL = 'sqlite:///outfit_builder.db'
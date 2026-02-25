import scrapy
import re
import json
import random
from scrapy_playwright.page import PageMethod

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['amazon.com']
    
    def start_requests(self):
        categories = ['Tops', 'Bottoms', 'Shoes', 'Accessories']
        search_queries = {
            'Tops': 'women+shirts+tops',
            'Bottoms': 'women+pants+jeans',
            'Shoes': 'women+sneakers+shoes',
            'Accessories': 'women+accessories+hats+scarves'
        }
        
        for category in categories:
            search_url = f"https://www.amazon.com/s?k={search_queries[category]}"
            
            yield scrapy.Request(
                url=search_url,
                callback=self.parse_search,
                meta={
                    'category': category,
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', 'div[data-component-type="s-search-result"]'),
                        PageMethod('evaluate', 'window.scrollBy(0, document.body.scrollHeight)'),
                        PageMethod('wait_for_timeout', 2000)
                    ]
                },
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
    
    async def parse_search(self, response):
        """Parse search results page"""
        category = response.meta['category']
        page = response.meta['playwright_page']
        
        # Extract product links
        product_links = response.css('a.a-link-normal.s-no-outline::attr(href)').getall()
        
        for link in product_links[:25]:
            yield scrapy.Request(
                url=response.urljoin(link),
                callback=self.parse_product,
                meta={
                    'category': category,
                    'playwright': True,
                    'playwright_include_page': True
                }
            )
        
        await page.close()
    
    def parse_product(self, response):
        """Parse individual product page"""
        category = response.meta['category']
        
        # Extract product data
        name = response.css('span#productTitle::text').get()
        if name:
            name = name.strip()
        
        price = response.css('span.a-price span.a-offscreen::text').get()
        if not price:
            price = response.css('span.a-price-whole::text').get()
        
        # Clean price
        if price:
            price = re.sub(r'[^\d.]', '', price)
        
        # Extract description
        description = response.css('div#productDescription p::text').get()
        if not description:
            description = response.css('div#feature-bullets ul li span::text').getall()
            description = ' '.join(description)
        
        # Extract images
        images = response.css('img#landingImage::attr(src)').getall()
        
        # Extract brand
        brand = response.css('a#bylineInfo::text').get()
        if brand:
            brand = brand.replace('Visit the ', '').replace(' Store', '').strip()
        
        google_category = f"Apparel & Accessories > Clothing > {category}"
        
        # Generate product ID
        asin = re.search(r'/dp/([A-Z0-9]{10})', response.url)
        product_id = f"AMZ_{asin.group(1)}" if asin else f"AMZ_{random.randint(100000, 999999)}"
        
        yield ProductItem(
            product_id=product_id,
            name=name or 'Unknown',
            brand=brand or 'Amazon',
            price=float(price) if price else 0,
            currency='USD',
            color='Unknown',  # Would need NLP to extract
            description=description or '',
            image_url=images[0] if images else '',
            product_url=response.url,
            category=google_category,
            sub_category=category,
            attributes=json.dumps({'images': images}),
            in_stock=True
        )
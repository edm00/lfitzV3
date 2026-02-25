import scrapy
import json
import re
from scrapy.loader import ItemLoader
from outfit_scraper.items import ProductItem
import random

class HmSpider(scrapy.Spider):
    name = 'hm'
    allowed_domains = ['www2.hm.com']
    
    # Start URLs for different categories
    start_urls = {
        'Tops': 'https://www2.hm.com/en_us/women/products/tops.html',
        'Bottoms': 'https://www2.hm.com/en_us/women/products/jeans.html',
        'Shoes': 'https://www2.hm.com/en_us/women/products/shoes.html',
        'Accessories': 'https://www2.hm.com/en_us/women/products/accessories.html'
    }
    
    def start_requests(self):
        for category, url in self.start_urls.items():
            yield scrapy.Request(
                url=url,
                callback=self.parse_category,
                meta={'category': category},
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Referer': 'https://www2.hm.com/'
                }
            )
    
    def parse_category(self, response):
        """Parse category page and extract product links"""
        category = response.meta['category']
        
        # Extract product links
        product_links = response.css('a.product-item-link::attr(href)').getall()
        
        for link in product_links[:25]:  # Limit to 25 per category
            yield scrapy.Request(
                url=response.urljoin(link),
                callback=self.parse_product,
                meta={'category': category},
                headers={
                    'Referer': response.url
                }
            )
        
        # Handle pagination
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page and len(product_links) < 100:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse_category,
                meta={'category': category}
            )
    
    def parse_product(self, response):
        """Parse individual product page"""
        category = response.meta['category']
        
        # Extract product data
        name = response.css('h1.product-name::text').get()
        price = response.css('span.price::text').get()
        description = response.css('div.product-description p::text').get()
        
        # Clean price
        if price:
            price = re.sub(r'[^\d.]', '', price)
        
        # Extract colors
        colors = response.css('a.color-option::attr(title)').getall()
        
        # Extract images
        images = response.css('img.product-image::attr(src)').getall()
        
        # Determine sub-category based on Google taxonomy
        google_category = f"Apparel & Accessories > Clothing > {category}"
        
        # Create product item
        loader = ItemLoader(item=ProductItem(), response=response)
        loader.add_value('product_id', f"HM_{response.url.split('/')[-2]}")
        loader.add_value('name', name)
        loader.add_value('brand', 'H&M')
        loader.add_value('price', float(price) if price else 0)
        loader.add_value('currency', 'USD')
        loader.add_value('color', colors[0] if colors else 'Unknown')
        loader.add_value('description', description or '')
        loader.add_value('image_url', images[0] if images else '')
        loader.add_value('product_url', response.url)
        loader.add_value('category', google_category)
        loader.add_value('sub_category', category)
        loader.add_value('attributes', json.dumps({
            'colors': colors,
            'images': images,
            'materials': response.css('span.material::text').getall()
        }))
        loader.add_value('in_stock', True)
        
        yield loader.load_item()
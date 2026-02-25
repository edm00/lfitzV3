import scrapy
import json
import re

class NordstromSpider(scrapy.Spider):
    name = 'nordstrom'
    allowed_domains = ['nordstrom.com']
    
    category_urls = {
        'Tops': 'https://www.nordstrom.com/browse/women/clothing/tops',
        'Bottoms': 'https://www.nordstrom.com/browse/women/clothing/pants',
        'Shoes': 'https://www.nordstrom.com/browse/women/shoes',
        'Accessories': 'https://www.nordstrom.com/browse/women/accessories'
    }
    
    def start_requests(self):
        for category, url in self.category_urls.items():
            yield scrapy.Request(
                url=url,
                callback=self.parse_category,
                meta={'category': category}
            )
    
    def parse_category(self, response):
        """Parse category page with infinite scroll handling"""
        category = response.meta['category']
        
        # Extract product data from script tags
        script_data = response.css('script[type="application/ld+json"]::text').get()
        if script_data:
            try:
                data = json.loads(script_data)
                products = data.get('itemListElement', [])
                
                for product in products[:25]:
                    yield scrapy.Request(
                        url=product.get('url'),
                        callback=self.parse_product,
                        meta={'category': category}
                    )
            except:
                pass
        
        # Fallback to HTML parsing
        product_links = response.css('a.product-card-link::attr(href)').getall()
        for link in product_links[:25]:
            yield scrapy.Request(
                url=response.urljoin(link),
                callback=self.parse_product,
                meta={'category': category}
            )
    
    def parse_product(self, response):
        """Parse individual product page"""
        category = response.meta['category']
        
        name = response.css('h1[itemprop="name"]::text').get()
        price = response.css('span[itemprop="price"]::attr(content)').get()
        
        # Extract product data from JSON-LD
        json_data = response.css('script[type="application/ld+json"]::text').get()
        if json_data:
            try:
                data = json.loads(json_data)
                description = data.get('description', '')
                images = data.get('image', [])
                brand = data.get('brand', {}).get('name', 'Nordstrom')
                
                yield ProductItem(
                    product_id=f"NOR_{response.url.split('/')[-2]}",
                    name=name or data.get('name', ''),
                    brand=brand,
                    price=float(price) if price else 0,
                    currency='USD',
                    color='Unknown',
                    description=description,
                    image_url=images[0] if isinstance(images, list) else images,
                    product_url=response.url,
                    category=f"Apparel & Accessories > Clothing > {category}",
                    sub_category=category,
                    attributes=json.dumps({'images': images}),
                    in_stock=True
                )
            except:
                pass
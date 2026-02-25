import scrapy

class ProductItem(scrapy.Item):
    product_id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    color = scrapy.Field()
    description = scrapy.Field()
    image_url = scrapy.Field()
    product_url = scrapy.Field()
    category = scrapy.Field()
    sub_category = scrapy.Field()
    attributes = scrapy.Field()
    in_stock = scrapy.Field()
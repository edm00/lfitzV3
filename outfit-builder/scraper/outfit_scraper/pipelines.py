from sqlalchemy.orm import sessionmaker
from database.init_db import engine, Product, PriceHistory
from datetime import datetime
import json

class DatabasePipeline:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
    
    def process_item(self, item, spider):
        session = self.Session()
        
        try:
            # Check if product exists
            product = session.query(Product).filter_by(product_id=item['product_id']).first()
            
            if product:
                # Update existing product
                product.price = item['price']
                product.in_stock = item['in_stock']
                product.last_updated = datetime.utcnow()
                
                # Add price history
                price_history = PriceHistory(
                    product_id=item['product_id'],
                    price=item['price']
                )
                session.add(price_history)
            else:
                # Create new product
                product = Product(
                    product_id=item['product_id'],
                    name=item['name'],
                    brand=item['brand'],
                    price=item['price'],
                    currency=item['currency'],
                    color=item['color'],
                    description=item['description'],
                    image_url=item['image_url'],
                    product_url=item['product_url'],
                    category=item['category'],
                    sub_category=item['sub_category'],
                    attributes=item.get('attributes', '{}'),
                    tags=json.dumps([]),
                    in_stock=item.get('in_stock', True)
                )
                session.add(product)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            spider.logger.error(f"Database error: {e}")
        finally:
            session.close()
        
        return item

class DuplicatesPipeline:
    def __init__(self):
        self.ids_seen = set()
    
    def process_item(self, item, spider):
        if item['product_id'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item['product_id']}")
        else:
            self.ids_seen.add(item['product_id'])
            return item
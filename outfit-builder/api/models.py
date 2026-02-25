# Database models for the outfit builder API

class Outfit:
    def __init__(self, id, name, items, created_at):
        self.id = id
        self.name = name
        self.items = items
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'items': self.items,
            'created_at': self.created_at
        }


class ClothingItem:
    def __init__(self, id, title, price, url, category, size, color):
        self.id = id
        self.title = title
        self.price = price
        self.url = url
        self.category = category
        self.size = size
        self.color = color

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'url': self.url,
            'category': self.category,
            'size': self.size,
            'color': self.color
        }

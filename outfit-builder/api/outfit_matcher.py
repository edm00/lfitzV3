import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import json
import re
from collections import defaultdict

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

class OutfitMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.category_keywords = {
            'Tops': ['shirt', 'blouse', 'top', 'sweater', 'hoodie', 'jacket', 't-shirt'],
            'Bottoms': ['pants', 'jeans', 'skirt', 'shorts', 'leggings', 'trousers'],
            'Shoes': ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flats'],
            'Accessories': ['hat', 'scarf', 'bag', 'watch', 'jewelry', 'belt']
        }
        
        # Vibe-based keyword mapping
        self.vibe_keywords = {
            'date night': ['elegant', 'sexy', 'romantic', 'sophisticated', 'classy', 'evening'],
            'casual': ['comfortable', 'relaxed', 'everyday', 'basic', 'simple'],
            'business': ['professional', 'formal', 'suit', 'blazer', 'office'],
            '90s outfits': ['vintage', 'retro', 'grunge', 'denim', 'plaid', 'crop top'],
            'summer vibes': ['summer', 'beach', 'vacation', 'light', 'bright', 'floral'],
            'winter cozy': ['warm', 'cozy', 'wool', 'knit', 'sweater', 'boots'],
            'athleisure': ['sporty', 'athletic', 'gym', 'workout', 'running', 'yoga'],
            'festival': ['boho', 'colorful', 'fun', 'edgy', 'statement']
        }
    
    def expand_query_with_wordnet(self, query):
        """Expand query using WordNet synonyms"""
        words = word_tokenize(query.lower())
        expanded_terms = set(words)
        
        for word in words:
            synsets = wordnet.synsets(word)
            for syn in synsets[:2]:  # Limit to first 2 synsets
                for lemma in syn.lemmas()[:3]:  # Limit to first 3 lemmas
                    expanded_terms.add(lemma.name().replace('_', ' '))
        
        return ' '.join(expanded_terms)
    
    def calculate_vibe_score(self, product, vibe):
        """Calculate how well a product matches a vibe"""
        score = 0
        text = f"{product.name} {product.description}".lower()
        
        # Get keywords for this vibe
        vibe_words = self.vibe_keywords.get(vibe.lower(), [])
        
        # Check for exact matches
        for word in vibe_words:
            if word in text:
                score += 2
        
        # Check for synonyms/related terms
        for word in vibe_words:
            synsets = wordnet.synsets(word)
            for syn in synsets[:1]:
                for lemma in syn.lemmas()[:2]:
                    if lemma.name().lower() in text:
                        score += 1
        
        # Boost score for matching category-appropriate items
        category = product.sub_category
        if category == 'Accessories' and any(word in vibe_words for word in ['jewelry', 'bag', 'hat']):
            score += 3
        
        return score
    
    def semantic_similarity(self, query, product_text):
        """Calculate semantic similarity between query and product"""
        # Combine query and product text
        texts = [query, product_text]
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return similarity
    
    def find_matching_outfits(self, products, query, n_outfits=5):
        """Find matching outfits for a query"""
        
        # Expand query
        expanded_query = self.expand_query_with_wordnet(query)
        
        # Categorize products
        categorized = defaultdict(list)
        for product in products:
            categorized[product.sub_category].append(product)
        
        # Score each product
        scored_products = defaultdict(list)
        for category, items in categorized.items():
            for product in items:
                # Combine multiple scoring methods
                vibe_score = self.calculate_vibe_score(product, query)
                text = f"{product.name} {product.description}".lower()
                semantic_score = self.semantic_similarity(expanded_query, text)
                
                # Weighted score (vibe: 0.6, semantic: 0.4)
                total_score = (vibe_score * 0.6) + (semantic_score * 0.4)
                
                scored_products[category].append((product, total_score))
            
            # Sort by score
            scored_products[category].sort(key=lambda x: x[1], reverse=True)
        
        # Generate outfit combinations
        outfits = []
        for i in range(min(n_outfits, 5)):
            outfit = {}
            for category in ['Tops', 'Bottoms', 'Shoes', 'Accessories']:
                if scored_products[category] and i < len(scored_products[category]):
                    outfit[category.lower()] = scored_products[category][i][0]
                else:
                    outfit[category.lower()] = None
            
            if all(outfit.values()):  # Only add if all categories present
                outfits.append(outfit)
        
        return outfits
    
    def check_aesthetic_compatibility(self, outfit):
        """Check if outfit pieces work well together (simplified version)"""
        compatibility_score = 0
        
        # Color compatibility (simplified - would use actual color extraction)
        colors = []
        for item in outfit.values():
            if item and hasattr(item, 'color'):
                colors.append(item.color.lower())
        
        # Simple color matching rules
        color_combinations = {
            ('black', 'white'): 5,
            ('navy', 'white'): 4,
            ('black', 'denim'): 3,
        }
        
        for color1 in colors:
            for color2 in colors:
                if color1 != color2:
                    combo = tuple(sorted([color1, color2]))
                    if combo in color_combinations:
                        compatibility_score += color_combinations[combo]
        
        return compatibility_score
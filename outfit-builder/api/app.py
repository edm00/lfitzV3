from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import sessionmaker
from database.init_db import engine, Product
from api.outfit_matcher import OutfitMatcher
import json
from typing import Optional, List
import uvicorn

app = FastAPI(title="Outfit Builder API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database session
SessionLocal = sessionmaker(bind=engine)

# Initialize matcher
matcher = OutfitMatcher()

@app.get("/")
async def root():
    return {"message": "Outfit Builder API", "version": "1.0"}

@app.get("/api/search")
async def search_outfits(
    query: str = Query(..., description="Search query or vibe"),
    limit: int = Query(5, description="Number of outfits to return")
):
    """Search for outfits matching a vibe"""
    session = SessionLocal()
    
    try:
        # Get all products from database
        products = session.query(Product).filter(Product.in_stock == True).all()
        
        if not products:
            return {"outfits": [], "message": "No products found"}
        
        # Find matching outfits
        outfits = matcher.find_matching_outfits(products, query, limit)
        
        # Format response
        result = []
        for outfit in outfits:
            formatted_outfit = {}
            for category, product in outfit.items():
                if product:
                    formatted_outfit[category] = {
                        "id": product.product_id,
                        "name": product.name,
                        "brand": product.brand,
                        "price": product.price,
                        "color": product.color,
                        "image_url": product.image_url,
                        "product_url": product.product_url,
                        "category": product.category
                    }
                else:
                    formatted_outfit[category] = None
            
            # Add compatibility score
            compatibility = matcher.check_aesthetic_compatibility(formatted_outfit)
            formatted_outfit["compatibility_score"] = compatibility
            
            result.append(formatted_outfit)
        
        return {
            "query": query,
            "outfits": result,
            "count": len(result)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    limit: int = 100
):
    """Get products with optional category filter"""
    session = SessionLocal()
    
    try:
        query = session.query(Product).filter(Product.in_stock == True)
        
        if category:
            query = query.filter(Product.sub_category == category)
        
        products = query.limit(limit).all()
        
        return {
            "products": [
                {
                    "id": p.product_id,
                    "name": p.name,
                    "brand": p.brand,
                    "price": p.price,
                    "color": p.color,
                    "image_url": p.image_url,
                    "category": p.sub_category
                }
                for p in products
            ],
            "count": len(products)
        }
    
    finally:
        session.close()

@app.get("/api/categories")
async def get_categories():
    """Get available categories"""
    return {
        "categories": ["Tops", "Bottoms", "Shoes", "Accessories"]
    }

@app.post("/api/refresh-prices")
async def refresh_prices():
    """Trigger price refresh (would call scraper in production)"""
    # In production, this would trigger the scraper
    return {"message": "Price refresh initiated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
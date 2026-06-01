from fastapi import APIRouter, Query
from models.products import Product
from config.database import products
from schema.productschema import productlist_serial
from schema.productschema import productindividual_serial
from bson import ObjectId
from typing import Optional
import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

productrouter = APIRouter()

# ── Groq config ───────────────────────────────────────────────────────────────
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"   # free, fast, very capable


def serialize_mongo(doc):
    doc["_id"] = str(doc["_id"])
    return doc


# ── Existing routes (100% unchanged) ─────────────────────────────────────────

@productrouter.get("/products/productlist")
async def get_products():
    products1 = productlist_serial(products.find())
    return {'error': '', 'message': products1}


@productrouter.get("/products/singleproductlist/{id}")
async def get_singleproduct(id: str):
    product1 = productindividual_serial(products.find_one({"_id": ObjectId(id)}))
    return {'error': '', 'message': product1}


@productrouter.post("/products/addproduct")
async def post_product(product: Product):
    products.insert_one(dict(product))
    return {'error': '', 'message': product}


@productrouter.delete("/products/deleteproduct/{id}")
async def delete_product(id: str):
    products.find_one_and_delete({"_id": ObjectId(id)})
    return {'error': '', 'message': 'User deleted sucessfully'}


@productrouter.put("/products/updateproduct/{id}")
async def update_product(id: str, product: Product):
    products.find_one_and_update({"_id": ObjectId(id)}, {"$set": dict(product)})


@productrouter.get("/products/findproducts/{category}")
async def find_products(category: str):
    products1 = productlist_serial(products.find({"category": category}))
    return {'error': '', 'message': products1}


@productrouter.get("/products/searchproducts/{input}")
async def search_products(input: str):
    products1 = productlist_serial(products.find({"productname": {"$regex": input, "$options": "i"}}))
    return {'error': '', 'message': products1}


@productrouter.get("/products/sidesearchproducts")
async def side_search_products(
    category: Optional[str] = Query(None),
    secondarycategory: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    price: Optional[str] = Query(None),
):
    query = {}

    if category and category.strip():
        query["category"] = category

    if secondarycategory and secondarycategory.strip().lower() != "none":
        query["secondarycategory"] = {"$regex": secondarycategory, "$options": "i"}

    if brand and brand.strip().lower() != "none":
        query["brand"] = {"$regex": brand, "$options": "i"}

    if price and price.strip().lower() != "none":
        query["price"] = {"$lt": float(price)}

    result = list(products.find(query))
    result = [serialize_mongo(doc) for doc in result]

    return {"error": "", "message": result}


# ── NEW: AI Smart Search ──────────────────────────────────────────────────────
#
# How it works (no schema changes, no embeddings, no vector DB):
#   1. Fetch all products from MongoDB as-is
#   2. Build a compact text summary of each product (no imageurl)
#   3. Send summary + user query to Groq (llama-3.3-70b-versatile, FREE)
#   4. Groq reads the catalog and returns only matching product _id values
#   5. We look up those full products and return them
#
# For large catalogs: MongoDB pre-filter narrows candidates before Groq,
# keeping it fast and within token limits.
# ─────────────────────────────────────────────────────────────────────────────

def build_product_summary(product: dict) -> str:
    """Compact one-line product summary for Groq. Excludes imageurl."""
    return (
        f"[{product['_id']}] "
        f"{product.get('productname', '')} | "
        f"{product.get('brand', '')} | "
        f"{product.get('category', '')}/{product.get('secondarycategory', '')} | "
        f"₹{product.get('price', '0')} | "
        f"⭐{product.get('rating', '0')} | "
        f"{str(product.get('description', ''))[:80]}"
    )


def pre_filter_products(query: str) -> list:
    """
    Broad MongoDB pre-filter: match any meaningful word in the query against
    productname, description, category, brand. Falls back to all products
    if fewer than 5 results come back (ensures Groq has enough context).
    """
    # Extract words longer than 2 chars, take first 8
    words = [w for w in re.split(r"\s+", query.strip()) if len(w) > 2][:8]

    if not words:
        return list(products.find())

    or_conditions = []
    for word in words:
        pattern = {"$regex": word, "$options": "i"}
        or_conditions.extend([
            {"productname":        pattern},
            {"description":        pattern},
            {"category":           pattern},
            {"secondarycategory":  pattern},
            {"brand":              pattern},
        ])

    candidates = list(products.find({"$or": or_conditions}))

    # If pre-filter is too narrow, use everything so Groq has enough context
    if len(candidates) < 5:
        candidates = list(products.find())

    return candidates


async def ask_groq(query: str, catalog_text: str) -> list[str]:
    """
    Call Groq with the product catalog and user query.
    Returns a list of _id strings for matching products.
    """
    prompt = f"""You are a smart product search engine for an e-commerce store.

A user searched for: "{query}"

Here is the product catalog (format: [id] name | brand | category/subcategory | price | rating | description):
{catalog_text}

Your job:
- Understand what the user wants (price range, category, brand, rating, product type, etc.)
- Return ONLY the IDs of products that genuinely match the user's query
- Be smart: "cheap"/"budget" = low price, "premium"/"best" = high rating
- "under ₹2000" → only return products with price below 2000
- "good rating"/"highly rated" → only products with rating 4.0 or above
- Return maximum 20 best-matching IDs, sorted by relevance
- Return ONLY a raw JSON array of ID strings, nothing else. Example: ["id1","id2","id3"]
- If nothing matches, return: []"""

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type":  "application/json",
    }
    body = {
        "model":       GROQ_MODEL,
        "temperature": 0,
        "max_tokens":  1000,
        "messages": [
            {
                "role":    "system",
                "content": "You are a product search engine. Respond ONLY with a raw JSON array of product ID strings. No explanation, no markdown, no extra text.",
            },
            {
                "role":    "user",
                "content": prompt,
            },
        ],
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(GROQ_API_URL, headers=headers, json=body)
        resp.raise_for_status()

    raw = resp.json()["choices"][0]["message"]["content"]
    raw = raw.replace("```json", "").replace("```", "").strip()

    import json
    return json.loads(raw)  # list of id strings


@productrouter.get("/products/aisearch/{query}")
async def ai_search_products(query: str):
    """
    AI-powered natural language product search using Groq.
    No schema changes. No embeddings. No vector DB.
    Groq reads your existing products and decides what matches.

    Example queries:
      - "Sony earphones under ₹2000"
      - "men's clothing with good rating"
      - "budget electronics below 1500"
      - "highly rated women's shoes"
    """
    query = query.strip()
    if not query:
        return {"error": "Empty query", "message": []}

    # ── Step 1: MongoDB pre-filter (broad, narrows the candidate pool) ────────
    candidates = pre_filter_products(query)
    print(f"AI Search | query='{query}' | candidates={len(candidates)}")

    if not candidates:
        return {"error": "", "message": [], "mode": "ai"}

    # ── Step 2: Serialize for Groq (strip _id, keep it readable) ─────────────
    serialized = [serialize_mongo(dict(doc)) for doc in candidates]

    # Build compact catalog text
    catalog_text = "\n".join(build_product_summary(p) for p in serialized)

    # ── Step 3: Ask Groq which products match ─────────────────────────────────
    try:
        matched_ids = await ask_groq(query, catalog_text)
        print(f"AI Search | Groq matched {len(matched_ids)} products")
    except Exception as e:
        print(f"AI Search | Groq error: {e} — falling back to pre-filter results")
        # Graceful fallback: return the pre-filtered products as-is
        return {"error": "", "message": serialized[:20], "mode": "fallback"}

    if not matched_ids:
        return {"error": "", "message": [], "mode": "ai"}

    # ── Step 4: Return full products in Groq's ranked order ──────────────────
    product_map = {p["_id"]: p for p in serialized}
    matched = [product_map[id_] for id_ in matched_ids if id_ in product_map]

    return {"error": "", "message": matched, "mode": "ai"}

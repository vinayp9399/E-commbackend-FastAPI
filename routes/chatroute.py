from fastapi import APIRouter
from pydantic import BaseModel
from config.database import products
from schema.productschema import productlist_serial
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

chatrouter = APIRouter()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"


# ── Request / Response models ─────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str       # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]   # full conversation history from frontend


# ── Helper: build product catalog summary for system prompt ──────────────────

def get_product_catalog_summary() -> str:
    """
    Fetches all products from MongoDB and builds a compact catalog string.
    Groq uses this to answer questions about available products.
    """
    all_products = productlist_serial(products.find())

    if not all_products:
        return "No products are currently available in the store."

    lines = []
    for p in all_products:
        line = (
            f"- {p.get('productname', 'N/A')} "
            f"| Brand: {p.get('brand', 'N/A')} "
            f"| Category: {p.get('category', 'N/A')}/{p.get('secondarycategory', 'N/A')} "
            f"| Price: ₹{p.get('price', 'N/A')} "
            f"| Rating: ⭐{p.get('rating', 'N/A')} "
            f"| {str(p.get('description', ''))[:60]}"
        )
        lines.append(line)

    return "\n".join(lines)


def build_system_prompt() -> str:
    catalog = get_product_catalog_summary()
    return f"""You are a friendly and helpful shopping assistant for BigCart, an e-commerce store.

You help customers with:
- Finding products that match their needs and budget
- Answering questions about product categories, brands, and prices
- Explaining how to use the website (search, filters, cart, wishlist, login)
- Giving honest recommendations based on ratings and value

Here is the current product catalog:
{catalog}

Guidelines:
- Be warm, concise, and conversational
- When recommending products, mention the name, price, and rating
- If asked about something not in the catalog, say it's not currently available
- For website help: users can search by name or use ✦ AI Search for natural language queries, filter by category/brand/price on the left sidebar, add to cart or wishlist from product cards
- Never make up products or prices that aren't in the catalog above
- Keep responses short (2–4 sentences max) unless listing multiple products"""


# ── Chat endpoint ─────────────────────────────────────────────────────────────

@chatrouter.post("/chat")
async def chat(request: ChatRequest):
    """
    Multi-turn AI chatbot endpoint.
    Accepts the full conversation history and returns the assistant's next reply.
    Groq reads the live product catalog from MongoDB on every request.
    """
    try:
        # Build messages array: system prompt + full conversation history
        system_prompt = build_system_prompt()

        groq_messages = [{"role": "system", "content": system_prompt}]
        for msg in request.messages:
            groq_messages.append({"role": msg.role, "content": msg.content})

        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type":  "application/json",
        }
        body = {
            "model":       GROQ_MODEL,
            "temperature": 0.7,
            "max_tokens":  512,
            "messages":    groq_messages,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(GROQ_API_URL, headers=headers, json=body)
            resp.raise_for_status()

        reply = resp.json()["choices"][0]["message"]["content"]
        return {"error": "", "reply": reply}

    except Exception as e:
        print(f"Chat error: {e}")
        return {
            "error": str(e),
            "reply": "Sorry, I'm having trouble right now. Please try again in a moment."
        }

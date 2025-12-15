from fastapi import APIRouter, Query
from models.products import Product
from config.database import products
from schema.productschema import productlist_serial
from schema.productschema import productindividual_serial
from bson import ObjectId
from typing import Optional

productrouter = APIRouter()

def serialize_mongo(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@productrouter.get("/products/productlist")
async def get_products():
    products1 = productlist_serial(products.find())
    return {'error':'','message':products1}

@productrouter.get("/products/singleproductlist/{id}")
async def get_singleproduct(id:str):
    product1 = productindividual_serial(products.find_one({"_id": ObjectId(id)}))
    return {'error':'','message':product1}

@productrouter.post("/products/addproduct")
async def post_product(product:Product):
    products.insert_one(dict(product))
    return {'error':'','message':product}

@productrouter.delete("/products/deleteproduct/{id}")
async def delete_product(id:str):
    products.find_one_and_delete({"_id": ObjectId(id)})
    return {'error':'','message':'User deleted sucessfully'}

@productrouter.put("/products/updateproduct/{id}")
async def update_product(id:str, product:Product):
    products.find_one_and_update({"_id": ObjectId(id)}, {"$set":dict(product)})

@productrouter.get("/products/findproducts/{category}")
async def find_products(category:str):
    products1 = productlist_serial(products.find({"category": category}))
    return {'error':'','message':products1}

@productrouter.get("/products/searchproducts/{input}")
async def search_products(input:str):
    products1 = productlist_serial(products.find({"productname":{"$regex": input, "$options": "i"}}))
    return {'error':'','message':products1}

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
def productindividual_serial(product) -> dict:
    return{
        "_id": str(product["_id"]),
        "productname": product["productname"],
        "description": product["description"],
        "price": product["price"],
        "quantity": product["quantity"],
        "rating": product["rating"],
        "imageurl": product["imageurl"],
        "category": product["category"],
        "secondarycategory": product["secondarycategory"],
        "brand": product.get("brand", None)
    }

def productlist_serial(products) -> list:
    return[productindividual_serial(product) for product in products]
def cartindividual_serial(cart) -> dict:
    return{
        "_id": str(cart["_id"]),
        "userid": cart["userid"],
        "productname": cart["productname"],
        "description": cart["description"],
        "price": cart["price"],
        "quantity": cart["quantity"],
        "rating": cart["rating"],
        "imageurl": cart["imageurl"],
        "category": cart["category"],
    }

def cartlist_serial(carts) -> list:
    return[cartindividual_serial(cart) for cart in carts]




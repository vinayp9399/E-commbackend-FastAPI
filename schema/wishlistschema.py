def wishlistindividual_serial(wishlist) -> dict:
    return{
        "_id": str(wishlist["_id"]),
        "userid": wishlist["userid"],
        "productname": wishlist["productname"],
        "description": wishlist["description"],
        "price": wishlist["price"],
        "quantity": wishlist["quantity"],
        "rating": wishlist["rating"],
        "imageurl": wishlist["imageurl"],
        "category": wishlist["category"],
    }

def wishlistlist_serial(wishlists) -> list:
    return[wishlistindividual_serial(wishlist) for wishlist in wishlists]
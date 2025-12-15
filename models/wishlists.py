from pydantic import BaseModel

class Wishlist(BaseModel):
    userid:str
    productname:str
    description:str
    price:str
    quantity:str
    rating:str
    imageurl:str
    category:str

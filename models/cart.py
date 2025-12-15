from pydantic import BaseModel

class Cart(BaseModel):
    userid:str
    productname:str
    description:str
    price:str
    quantity:str
    rating:str
    imageurl:str
    category:str

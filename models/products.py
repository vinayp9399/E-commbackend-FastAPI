from pydantic import BaseModel

class Product(BaseModel):
    productname:str
    description:str
    price:str
    quantity:str
    rating:str
    imageurl:str
    category:str
    secondarycategory:str
    brand:str
from fastapi import APIRouter
from models.cart import Cart
from config.database import carts
from schema.cartschema import cartlist_serial
from schema.cartschema import cartindividual_serial
from bson import ObjectId

cartrouter = APIRouter()

@cartrouter.get("/cart/cartlist/{userid}")
async def get_carts(userid:str):
    carts1 = cartlist_serial(carts.find({"userid": userid}))
    return {'error':'','message':carts1}

@cartrouter.get("/cart/singlecartlist/{id}")
async def get_singlecart(id:str):
    cart1 = cartindividual_serial(carts.find_one({"_id": ObjectId(id)}))
    return {'error':'','message':cart1}

@cartrouter.get("/cart/findcart/{category}")
async def find_carts(category:str):
    carts1 = cartlist_serial(carts.find({"category": category}))
    return {'error':'','message':carts1}

@cartrouter.post("/cart/addcart")
async def post_cart(cart:Cart):
    carts.insert_one(dict(cart))
    return {'error':'','message':cart}

@cartrouter.delete("/cart/deletecart/{id}")
async def delete_cart(id:str):
    carts.find_one_and_delete({"_id": ObjectId(id)})
    return {'error':'','message':'cart item deleted sucessfully'}

@cartrouter.put("/cart/updatecart/{id}")
async def update_cart(id:str, cart:Cart):
    carts.find_one_and_update({"_id": ObjectId(id)}, {"$set":dict(cart)})




# router.get('/cartlist/(:userid)',cartcontroller.cartlist);
# router.get('/singlecartlist/(:id)',cartcontroller.singlecartlist);
# router.get('/findcart/(:category)',cartcontroller.findcart);
# router.post('/addcart',cartcontroller.addcart);
# router.delete('/deletecart/(:id)',cartcontroller.deletecart);
# router.put('/updatecart/(:id)',cartcontroller.updatecart);
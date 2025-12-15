from fastapi import APIRouter
from models.wishlists import Wishlist
from config.database import wishlists
from schema.wishlistschema import wishlistlist_serial
from schema.wishlistschema import wishlistindividual_serial
from bson import ObjectId

wishlistrouter = APIRouter()

@wishlistrouter.get("/wishlist/wishlist/{userid}")
async def get_wishlists(userid:str):
    wishlists1 = wishlistlist_serial(wishlists.find({"userid": userid}))
    return {'error':'','message':wishlists1}

@wishlistrouter.get("/wishlist/singlewish/{id}")
async def get_singlewishlist(id:str):
    wishlist1 = wishlistindividual_serial(wishlists.find_one({"_id": ObjectId(id)}))
    return {'error':'','message':wishlist1}

@wishlistrouter.get("/wishlist/findwish/{category}")
async def find_wishlists(category:str):
    wishlists1 = wishlistlist_serial(wishlists.find({"category": category}))
    return {'error':'','message':wishlists1}

@wishlistrouter.post("/wishlist/addwish")
async def post_wishlist(wishlist:Wishlist):
    wishlists.insert_one(dict(wishlist))
    return {'error':'','message':wishlist}

@wishlistrouter.delete("/wishlist/deletewish/{id}")
async def delete_wishlist(id:str):
    wishlists.find_one_and_delete({"_id": ObjectId(id)})
    return {'error':'','message':'wishlist item deleted sucessfully'}

@wishlistrouter.put("/wishlist/updatewish/{id}")
async def update_wishlist(id:str, wishlist:Wishlist):
    wishlists.find_one_and_update({"_id": ObjectId(id)}, {"$set":dict(wishlist)})

    



# router.get('/wishlist/(:userid)',wishlistcontroller.wishlist);
# router.get('/singlewish/(:id)',wishlistcontroller.singlewish);
# router.get('/findwish/(:category)',wishlistcontroller.findwish);
# router.post('/addwish',wishlistcontroller.addwish);
# router.delete('/deletewish/(:id)',wishlistcontroller.deletewish);
# router.put('/updatewish/(:id)',wishlistcontroller.updatewish);
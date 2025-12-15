from fastapi import APIRouter
from models.users import User
from config.database import users
from schema.userschema import userlist_serial
from schema.userschema import userindividual_serial
from bson import ObjectId

userrouter = APIRouter()

@userrouter.get("/users/userlist")
async def get_users():
    users1 = userlist_serial(users.find())
    return {'error':'','message':users1}

@userrouter.get("/users/singleuserlist/{id}")
async def get_singleuser(id:str):
    user1 = userindividual_serial(users.find_one({"_id": ObjectId(id)}))
    return {'error':'','message':user1}

@userrouter.post("/users/registration")
async def post_user(user:User):
    users.insert_one(dict(user))
    return {'error':'','message':user}

@userrouter.delete("/users/deleteuser/{id}")
async def delete_user(id:str):
    users.find_one_and_delete({"_id": ObjectId(id)})
    return {'error':'','message':'User deleted sucessfully'}

@userrouter.post("/users/login")
async def login_user(user:User):
    user12 = userindividual_serial(users.find_one({"email": user.email}))
    password = user.password
    if not user12:
        return {'error':'','message':'email or password does not match'}
    elif(password != user12["password"]):
        return {'error':'','message':'email or password does not match'}
    else:
        return {'error':'','message':user12}

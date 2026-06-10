from fastapi import APIRouter, Depends
from models.users import User
from config.database import users
from schema.userschema import userlist_serial, userindividual_serial
from bson import ObjectId
from jose import jwt
import os
from dotenv import load_dotenv
from middleware.auth import verify_token

load_dotenv()

userrouter = APIRouter()

# Public routes
@userrouter.post("/users/registration")
async def post_user(user: User):
    users.insert_one(dict(user))
    return {'error': '', 'message': user}

@userrouter.post("/users/login")
async def login_user(user: User):
    user12 = userindividual_serial(users.find_one({"email": user.email}))
    if not user12:
        return {'error': '', 'message': 'email or password does not match'}
    elif user.password != user12["password"]:
        return {'error': '', 'message': 'email or password does not match'}
    else:
        access_token = jwt.encode({"id": user12["_id"], "name": user12["firstname"]}, os.getenv("jwtsecretkey"), algorithm="HS256")
        refresh_token = jwt.encode({"id": user12["_id"], "name": user12["firstname"]}, os.getenv("jwtrefreshtokenkey"), algorithm="HS256")
        return {'error': '', 'message': user12, 'token': access_token, 'refreshToken': refresh_token}

@userrouter.post("/users/refresh")
async def refresh_token(body: dict):
    refresh_token = body.get("refreshToken")
    if not refresh_token:
        return {'message': 'refresh token not available'}
    try:
        payload = jwt.decode(refresh_token, os.getenv("jwtrefreshtokenkey"), algorithms=["HS256"])
        new_access_token = jwt.encode({"id": payload["id"], "name": payload["name"]}, os.getenv("jwtsecretkey"), algorithm="HS256")
        return {'token': new_access_token}
    except Exception:
        return {'message': 'refresh token invalid or expired'}

# Protected routes
@userrouter.get("/users/userlist")
async def get_users(user=Depends(verify_token)):
    users1 = userlist_serial(users.find())
    return {'error': '', 'message': users1}

@userrouter.get("/users/singleuserlist/{id}")
async def get_singleuser(id: str, user=Depends(verify_token)):
    user1 = userindividual_serial(users.find_one({"_id": ObjectId(id)}))
    return {'error': '', 'message': user1}

@userrouter.delete("/users/deleteuser/{id}")
async def delete_user(id: str, user=Depends(verify_token)):
    users.find_one_and_delete({"_id": ObjectId(id)})
    return {'error': '', 'message': 'User deleted successfully'}

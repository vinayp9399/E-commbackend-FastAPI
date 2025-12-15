def userindividual_serial(user) -> dict:
    return{
        "_id": str(user["_id"]),
        "firstname": user["firstname"],
        "lastname": user["lastname"],
        "email": user["email"],
        "phoneno": user["phoneno"],
        "password": user["password"],
    }

def userlist_serial(users) -> list:
    return[userindividual_serial(user) for user in users]
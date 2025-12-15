from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    firstname: Optional[str]="None"
    lastname:Optional[str]="None"
    email:str
    phoneno:Optional[str]="None"
    password:str





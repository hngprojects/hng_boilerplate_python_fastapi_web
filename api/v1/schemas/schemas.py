from typing import Optional
from pydantic import BaseModel,EmailStr
from datetime import datetime
from uuid import UUID

from sqlalchemy import text


class createUser(BaseModel):
    username: str
    email: EmailStr
    password:str
    first_name:str
    last_name:str
    is_admin:bool

    class Config:
        from_attributes=True


class user_output(BaseModel):
    id:UUID
    username: str
    email: EmailStr
    is_admin:bool
    class Config:
        from_attributes=True



###############      organisation                  ##########################

# request body
class createOrg(BaseModel):
    name: str 
    description:str

#org response
class org_output(BaseModel):
    id:UUID
    name: str
    description: str
    # created_at:datetime
    class Config:
        from_attributes=True


class PreferenceBase(BaseModel):
    key: str
    value: str

class PreferenceCreate(PreferenceBase):
    pass

class PreferenceUpdate(PreferenceBase):
    pass

class PreferenceResponse(PreferenceBase):
    id: UUID
    organization_id: UUID

    class Config:
        from_attributes=True


class user_login(BaseModel):
    email: EmailStr
    password: str    
    class Config:
        from_attributes=True
        
class Token(BaseModel):
    access_token: str
    password: str    
class TokenData(BaseModel):
    #id: Optional[str]=None
    id: str


class PreferenceBase(BaseModel):
    name: str
    value: str

class PreferenceCreate(PreferenceBase):
    pass

class PreferenceUpdate(PreferenceBase):
    pass

class Preference_output(PreferenceBase):
    id: UUID
    name:str
    value:str
    org_id: UUID
    class Config:
        from_attributes=True


from pydantic import BaseModel

class ProductSchema(BaseModel):
    name:str
    description:str
    price:int
    org_id:int
    tags:str
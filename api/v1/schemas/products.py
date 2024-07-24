from pydantic import BaseModel

class ProductSchema(BaseModel):
    name:str
    description:str
    price:int
    tags:str


class DemoModel(BaseModel):
    number: str
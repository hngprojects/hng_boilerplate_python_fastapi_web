from pydantic import BaseModel

class PlanCreate(BaseModel):
    plan_name: str
    amount: int

class Plan(BaseModel):
    id: int
    plan_name: str
    amount: int

    class Config:
        orm_mode = True

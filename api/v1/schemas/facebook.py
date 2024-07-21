from pydantic import BaseModel


class userToken(BaseModel):
    access_token: str

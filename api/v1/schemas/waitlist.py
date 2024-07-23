from typing import List
from pydantic import BaseModel

class WaitlistUserResponse(BaseModel):
	message: str
	status_code: int
	data: List[str]
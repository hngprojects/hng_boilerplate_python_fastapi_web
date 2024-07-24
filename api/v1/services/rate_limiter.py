from fastapi import Depends, Request
from api.db.database import get_db
# from api.utils.dependencies import get_current_user
from api.v1.services.user import user_service
from time import time
from api.v1.models.rate_limiter import RateLimit
from sqlalchemy.orm import Session
from api.utils.json_response import JsonResponseDict


# Rate limit configuration
RATE_LIMIT = 100  # requests
RATE_LIMIT_PERIOD = 600  # seconds (10 minutes)


def rate_limiter(request: Request, db: Session = Depends(get_db), current_user: str = Depends(user_service.get_current_user)):
    client_ip = request.client.host
    current_time = time()
    
    rate_limit_entry = db.query(RateLimit).filter(RateLimit.client_ip == client_ip).first()
    
    if not rate_limit_entry:
        rate_limit_entry = RateLimit(client_ip=client_ip, count=0, start_time=current_time)
        db.add(rate_limit_entry)
        db.commit()
        db.refresh(rate_limit_entry)

    if current_time - rate_limit_entry.start_time > RATE_LIMIT_PERIOD:
        rate_limit_entry.count = 0
        rate_limit_entry.start_time = current_time
        db.commit()
    
    rate_limit_entry.count += 1
    
    if rate_limit_entry.count > RATE_LIMIT:
        raise JsonResponseDict(status_code=429, message="Too many requests")

    db.commit()

    return current_user
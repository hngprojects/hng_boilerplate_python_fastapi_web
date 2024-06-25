from fastapi import HTTPException

class CustomException(HTTPException):
    
    @staticmethod
    def PermissionError():
        raise HTTPException(status_code=403, detail="User has no permission to perform this action")
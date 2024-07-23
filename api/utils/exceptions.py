# from fastapi import HTTPException, Request
# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import JSONResponse
# from main import app

# @app.exception_handler(HTTPException)
# async def http_exception(request: Request, exc: HTTPException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "success": False,
#             "status_code": exc.status_code,
#             "message": exc.detail
#         }
#     )

# @app.exception_handler(RequestValidationError)
# async def validation_exception(request: Request, exc: RequestValidationError):
#     return JSONResponse(
#         status_code=422,
#         content={
#             "success": False,
#             "status_code": 422,
#             "message": "Invalid input",
#             "errors": exc.errors()
#         }
#     )

# @app.exception_handler(Exception)
# async def exception(request: Request, exc: Exception):
#     return JSONResponse(
#         status_code=500,
#         content={
#             "success": False,
#             "status_code": 500,
#             "message": "An unexpected error occurred"
#         }
#     )

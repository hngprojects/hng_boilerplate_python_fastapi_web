from fastapi import APIRouter
from utils import JsonResponse

greetings_router = APIRouter(prefix="/greetings", tags=["greetings"])


@greetings_router.get("/english")
async def english_greeting():
    """Greet the user in English"""
    return JsonResponse(
        message="successful",
        data={"greeting": "Good Morning, how are you?"}
    )


@greetings_router.get("/french")
async def english_greeting():
    """Greet the user in French"""
    return JsonResponse(
        message="successful",
        data={"greeting": "Bonjour, comment ca va?"}
    )
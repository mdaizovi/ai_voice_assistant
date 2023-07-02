from fastapi import APIRouter
from api.endpoints import whatsapp_message

api_router = APIRouter()
api_router.include_router(whatsapp_message.router)
from fastapi import APIRouter
from app.api.routes import tickets_api

api_router = APIRouter()
api_router.include_router(tickets_api.router, prefix="/tickets", tags=["Tickets"])

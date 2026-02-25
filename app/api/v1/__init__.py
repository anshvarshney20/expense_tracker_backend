from fastapi import APIRouter
from app.api.v1 import auth, expenses, pots, ai, marketing

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(pots.router, prefix="/pots", tags=["pots"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(marketing.router, prefix="/marketing", tags=["marketing"])

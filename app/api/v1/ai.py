from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api import deps
from app.models.user import User
from app.schemas.responses import SuccessResponse
from app.services.ai import AIService, AIAnalysisResponse
from app.services.expense import ExpenseService

router = APIRouter()

@router.post("/analyze", response_model=SuccessResponse[AIAnalysisResponse])
async def analyze_spending(
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # Fetch recent expenses for analysis
    expense_service = ExpenseService(db)
    expenses = await expense_service.get_expenses(user_id=current_user.id, limit=50)
    
    # Prepare data for AI
    expenses_data = [
        {
            "title": e.title,
            "amount": float(e.amount),
            "category": e.category,
            "date": str(e.date),
            "is_avoidable": e.is_avoidable
        }
        for e in expenses
    ]
    
    ai_service = AIService()
    analysis = await ai_service.analyze_expenses(expenses_data)
    
    return SuccessResponse(data=analysis)

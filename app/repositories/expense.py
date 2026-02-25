import uuid
from datetime import date, datetime
from typing import Sequence
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.expense import Expense
from app.repositories.base import BaseRepository

class ExpenseRepository(BaseRepository[Expense]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(Expense, db)

    async def get_multi_by_user(
        self,
        *,
        user_id: uuid.UUID,
        category: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Expense]:
        query = {"user_id": str(user_id)}
        
        if category:
            query["category"] = category
            
        date_filter = {}
        if start_date:
            # MongoDB handles dates, but pydantic/motor might need conversion
            date_filter["$gte"] = datetime.combine(start_date, datetime.min.time())
        if end_date:
            date_filter["$lte"] = datetime.combine(end_date, datetime.max.time())
            
        if date_filter:
            query["date"] = date_filter
            
        cursor = self.collection.find(query).sort("date", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [Expense(**doc) for doc in docs]

    async def get_monthly_summary(
        self, user_id: uuid.UUID, year: int, month: int
    ) -> dict:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        user_id_str = str(user_id)
        
        # Aggregation for summary
        pipeline = [
            {
                "$match": {
                    "user_id": user_id_str,
                    "date": {"$gte": start_date, "$lt": end_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1},
                    "categories": {"$push": {"category": "$category", "amount": "$amount"}}
                }
            }
        ]
        
        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        
        if not result:
            # Check lifetime total even if no monthly data
            lifetime_cursor = self.collection.aggregate([
                {"$match": {"user_id": user_id_str}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ])
            lifetime_res = await lifetime_cursor.to_list(length=1)
            lifetime_total = lifetime_res[0]["total"] if lifetime_res else 0
            
            return {
                "total_amount": 0,
                "count": 0,
                "lifetime_total": lifetime_total,
                "category_breakdown": {}
            }
            
        summary = result[0]
        
        # Calculate lifetime total
        lifetime_cursor = self.collection.aggregate([
            {"$match": {"user_id": user_id_str}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])
        lifetime_res = await lifetime_cursor.to_list(length=1)
        lifetime_total = lifetime_res[0]["total"] if lifetime_res else 0
        
        # Calculate category breakdown from the aggregated categories
        breakdown = {}
        for entry in summary.get("categories", []):
            cat = entry["category"]
            amt = entry["amount"]
            breakdown[cat] = breakdown.get(cat, 0) + amt
            
        return {
            "total_amount": summary["total"],
            "count": summary["count"],
            "lifetime_total": lifetime_total,
            "category_breakdown": breakdown
        }

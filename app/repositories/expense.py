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
        avoidable: bool | None = None,
        search_query: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "date",
        sort_order: int = -1,
    ) -> tuple[Sequence[Expense], int, float]:
        query = {"user_id": str(user_id)}
        
        if category:
            query["category"] = category
            
        if avoidable is not None:
            query["is_avoidable"] = avoidable
            
        if search_query:
            query["title"] = {"$regex": search_query, "$options": "i"}
            
        date_filter = {}
        if start_date:
            date_filter["$gte"] = datetime.combine(start_date, datetime.min.time())
        if end_date:
            date_filter["$lte"] = datetime.combine(end_date, datetime.max.time())
            
        if date_filter:
            query["date"] = date_filter
            
        # Use aggregation to get both data and filtered totals in one trip
        pipeline = [
            {"$match": query},
            {
                "$facet": {
                    "data": [
                        {"$sort": {sort_by: sort_order}},
                        {"$skip": skip},
                        {"$limit": limit}
                    ],
                    "stats": [
                        {
                            "$group": {
                                "_id": None,
                                "total_count": {"$sum": 1},
                                "total_amount": {"$sum": "$amount"},
                                "total_avoidable_amount": {
                                    "$sum": {
                                        "$cond": [{"$eq": ["$is_avoidable", True]}, "$amount", 0]
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        ]
        
        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        
        facet_result = result[0]
        expenses = [Expense(**doc) for doc in facet_result["data"]]
        stats = facet_result["stats"][0] if facet_result["stats"] else {
            "total_count": 0, 
            "total_amount": 0.0,
            "total_avoidable_amount": 0.0
        }
        
        return expenses, stats["total_count"], float(stats["total_amount"]), float(stats["total_avoidable_amount"])

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

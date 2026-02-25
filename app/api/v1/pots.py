import uuid
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api import deps
from app.models.user import User
from app.schemas.pot import PotCreate, PotUpdate, PotInDB
from app.schemas.responses import SuccessResponse
from app.services.pot import PotService

router = APIRouter()

@router.post("", response_model=SuccessResponse[PotInDB])
async def create_pot(
    pot_in: PotCreate,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = PotService(db)
    pot = await service.create_pot(current_user.id, pot_in)
    
    # Calculate progress for response
    progress = service.calculate_progress(pot)
    
    # Construct dict manually - only including fields defined in the schema
    pot_data = pot.model_dump()
    pot_data.update(progress)
    
    return SuccessResponse(data=PotInDB(**pot_data))

@router.get("", response_model=SuccessResponse[list[PotInDB]])
async def list_pots(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = PotService(db)
    pots = await service.get_pots(current_user.id, skip, limit)
    
    res_data = []
    for pot in pots:
        progress = service.calculate_progress(pot)
        pot_data = pot.model_dump()
        pot_data.update(progress)
        res_data.append(PotInDB(**pot_data))
        
    return SuccessResponse(data=res_data)

@router.get("/{pot_id}", response_model=SuccessResponse[PotInDB])
async def get_pot(
    pot_id: uuid.UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = PotService(db)
    pot = await service.get_pot(pot_id, current_user.id)
    progress = service.calculate_progress(pot)
    
    pot_data = pot.model_dump()
    pot_data.update(progress)
    return SuccessResponse(data=PotInDB(**pot_data))

@router.patch("/{pot_id}", response_model=SuccessResponse[PotInDB])
async def update_pot(
    pot_id: uuid.UUID,
    pot_in: PotUpdate,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = PotService(db)
    pot = await service.update_pot(pot_id, current_user.id, pot_in)
    progress = service.calculate_progress(pot)
    
    pot_data = pot.model_dump()
    pot_data.update(progress)
    return SuccessResponse(data=PotInDB(**pot_data))

@router.delete("/{pot_id}", response_model=SuccessResponse[None])
async def delete_pot(
    pot_id: uuid.UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = PotService(db)
    await service.delete_pot(pot_id, current_user.id)
    return SuccessResponse(message="Pot deleted successfully")

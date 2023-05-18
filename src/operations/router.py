from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.operations.models import Operation
from src.operations.schemas import OperationCreate

from src.auth.base_config import current_active_user

router = APIRouter(
    dependencies=[Depends(current_active_user)],
    prefix="/operations",
    tags=["Operation"],
)


@router.get("")
async def get_specific_operations(
    operation_type: str,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        query = select(Operation).where(Operation.type == operation_type)
        result = await session.execute(query)
        return {"status": "success", "data": result.mappings().all(), "details": None}
    except Exception:
        raise HTTPException(
            status_code=500, detail={"status": "error", "data": None, "details": None}
        )


@router.post("")
async def add_specific_operations(
    new_operation: OperationCreate, session: AsyncSession = Depends(get_async_session)
):
    stmt = insert(Operation).values(**new_operation.dict())
    await session.execute(stmt)
    await session.commit()
    return {"status": "201 success"}


@router.get("/main")
async def main(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(1))
    return result.mappings().all()

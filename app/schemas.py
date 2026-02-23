from pydantic import BaseModel
from datetime import date
from typing import Optional

class ExpenseBase(BaseModel):
    title: str
    amount: float
    category: str
    description: Optional[str] = None
    payment_method: Optional[str] = "Cash"
    date: date

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(ExpenseBase):
    title: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    payment_method: Optional[str] = None
    date: Optional[date] = None

class ExpenseResponse(ExpenseBase):
    id: int

    class Config:
        from_attributes = True

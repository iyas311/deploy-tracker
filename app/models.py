from sqlalchemy import Column, Integer, String, Float, Date, Text
from .database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    payment_method = Column(String(50), nullable=True, default="Cash")
    date = Column(Date, nullable=False)

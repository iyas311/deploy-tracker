from sqlalchemy import Column, Integer, String, Decimal, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

class Summary(Base):
    __tablename__ = "summary"

    id = Column(Integer, primary_key=True, index=True)
    total_spent = Column(Decimal(10, 2))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    categories = relationship("CategorySummary", back_populates="summary")

class CategorySummary(Base):
    __tablename__ = "category_summary"

    id = Column(Integer, primary_key=True, index=True)
    summary_id = Column(Integer, ForeignKey("summary.id"))
    category = Column(String(100))
    amount = Column(Decimal(10, 2))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    summary = relationship("Summary", back_populates="categories")

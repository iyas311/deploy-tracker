from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas

def get_expense(db: Session, expense_id: int):
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()

def get_expenses(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(models.Expense)
    if search:
        query = query.filter(
            (models.Expense.title.ilike(f"%{search}%")) | 
            (models.Expense.category.ilike(f"%{search}%"))
        )
    return query.order_by(models.Expense.date.desc()).offset(skip).limit(limit).all()

def create_expense(db: Session, expense: schemas.ExpenseCreate):
    db_expense = models.Expense(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def update_expense(db: Session, expense_id: int, expense: schemas.ExpenseUpdate):
    db_expense = get_expense(db, expense_id)
    if db_expense:
        for key, value in expense.dict(exclude_unset=True).items():
            setattr(db_expense, key, value)
        db.commit()
        db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int):
    db_expense = get_expense(db, expense_id)
    if db_expense:
        db.delete(db_expense)
        db.commit()
    return db_expense

def get_total_amount(db: Session):
    return db.query(func.sum(models.Expense.amount)).scalar() or 0.0

def get_category_report(db: Session):
    # Using SQL GROUP BY via SQLAlchemy
    return db.query(
        models.Expense.category,
        func.sum(models.Expense.amount).label("total_amount")
    ).group_by(models.Expense.category).all()

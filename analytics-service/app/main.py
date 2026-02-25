import os
import requests
from typing import List, Dict
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal

from . import models, database

# Load environment variables (already done in database.py but just for clarity)
EXPENSE_SERVICE_URL = os.getenv("EXPENSE_SERVICE_URL", "http://localhost:8000")

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Analytics Service")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "analytics-service", "timestamp": datetime.now().isoformat()}

@app.post("/analytics/generate", status_code=201)
def generate_analytics(db: Session = Depends(get_db)):
    # 1. Fetch expenses from Expense Service
    try:
        response = requests.get(f"{EXPENSE_SERVICE_URL}/api/expenses", timeout=5)
        response.raise_for_status()
        expenses = response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch data from Expense Service: {str(e)}")

    if not expenses:
        return {"message": "No expenses found to analyze."}

    # 2. Calculate analytics
    total_spent = Decimal('0.00')
    category_breakdown: Dict[str, Decimal] = {}

    for expense in expenses:
        amount = Decimal(str(expense.get('amount', 0)))
        category = expense.get('category', 'Uncategorized')
        
        total_spent += amount
        category_breakdown[category] = category_breakdown.get(category, Decimal('0.00')) + amount

    # 3. Store results in analytics_db
    try:
        new_summary = models.Summary(total_spent=total_spent)
        db.add(new_summary)
        db.flush()  # To get the ID

        for category, amount in category_breakdown.items():
            db.add(models.CategorySummary(
                summary_id=new_summary.id,
                category=category,
                amount=amount
            ))
        
        db.commit()
        return {
            "message": "Analytics generated successfully",
            "summary_id": new_summary.id,
            "total_spent": float(total_spent)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/analytics/latest")
def get_latest_analytics(db: Session = Depends(get_db)):
    latest_summary = db.query(models.Summary).order_by(models.Summary.created_at.desc()).first()
    
    if not latest_summary:
        raise HTTPException(status_code=404, detail="No analytics records found.")

    categories = db.query(models.CategorySummary).filter(
        models.CategorySummary.summary_id == latest_summary.id
    ).all()

    return {
        "id": latest_summary.id,
        "total_spent": float(latest_summary.total_spent),
        "created_at": latest_summary.created_at,
        "category_breakdown": [
            {"category": c.category, "amount": float(c.amount)} for c in categories
        ]
    }

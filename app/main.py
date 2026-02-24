from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import models, crud, schemas, database

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Minimal Expense API")

# Allow the frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. RETRIEVE DATA
@app.get("/api/expenses", response_model=List[schemas.ExpenseResponse])
def read_expenses(db: Session = Depends(get_db)):
    return crud.get_expenses(db)

# 2. ADD DATA
@app.post("/api/expenses", response_model=schemas.ExpenseResponse, status_code=201)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_expense(db, expense)

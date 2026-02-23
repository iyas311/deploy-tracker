from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date as date_obj
import json
from . import models, crud, schemas, database

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Expense Tracker")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, search: str = None, db: Session = Depends(get_db)):
    expenses = crud.get_expenses(db, search=search)
    total_amount = crud.get_total_amount(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "expenses": expenses,
        "total_amount": total_amount,
        "now_date": date_obj.today().isoformat()
    })

@app.post("/add")
def add_expense(
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    payment_method: str = Form("Cash"),
    description: str = Form(None),
    date: str = Form(...),
    db: Session = Depends(get_db)
):
    expense_data = schemas.ExpenseCreate(
        title=title,
        amount=amount,
        category=category,
        payment_method=payment_method,
        description=description,
        date=date_obj.fromisoformat(date)
    )
    crud.create_expense(db, expense_data)
    return RedirectResponse(url="/", status_code=303)

@app.get("/delete/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    crud.delete_expense(db, expense_id)
    return RedirectResponse(url="/", status_code=303)

@app.get("/edit/{expense_id}", response_class=HTMLResponse)
def edit_expense_form(request: Request, expense_id: int, db: Session = Depends(get_db)):
    expense = crud.get_expense(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return templates.TemplateResponse("edit.html", {"request": request, "expense": expense})

@app.post("/edit/{expense_id}")
def update_expense(
    expense_id: int,
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    payment_method: str = Form("Cash"),
    description: str = Form(None),
    date: str = Form(...),
    db: Session = Depends(get_db)
):
    expense_data = schemas.ExpenseUpdate(
        title=title,
        amount=amount,
        category=category,
        payment_method=payment_method,
        description=description,
        date=date_obj.fromisoformat(date)
    )
    crud.update_expense(db, expense_id, expense_data)
    return RedirectResponse(url="/", status_code=303)

@app.get("/report", response_class=HTMLResponse)
def get_report(request: Request, db: Session = Depends(get_db)):
    report_data = crud.get_category_report(db)
    # Prepare data for Chart.js
    labels = [r[0] for r in report_data]
    values = [r[1] for r in report_data]
    return templates.TemplateResponse("report.html", {
        "request": request,
        "labels_json": json.dumps(labels),
        "values_json": json.dumps(values),
        "report_data": report_data
    })

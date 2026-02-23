# How to Run Locally

### 1. Prerequisites
- Python 3.8+
- MySQL Server installed and running

### 2. Setup Database
Create a database named `expense_tracker` in MySQL:
```sql
CREATE DATABASE expense_tracker;
```

### 3. Configure Connection
Update the `SQLALCHEMY_DATABASE_URL` in `app/database.py` with your MySQL credentials:
```python
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://your_user:your_password@localhost/expense_tracker"
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
uvicorn app.main:app --reload
```
Visit `http://127.0.0.1:8000` in your browser.

---

# AWS EC2 Deployment Guide

### 1. Launch EC2 Instance
- Use Ubuntu 22.04 LTS.
- Security Groups: Open ports 80 (HTTP) and 22 (SSH).

### 2. Connect via SSH
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 3. Install System Dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-venv mysql-server -y
```

### 4. Setup MySQL on EC2
```bash
sudo mysql
CREATE DATABASE expense_tracker;
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON expense_tracker.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Deploy Code
- Clone your repository or upload files.
- Create a virtual environment and install requirements.

### 6. Run with Gunicorn & Uvicorn
Use `gunicorn` with `uvicorn` workers for production:
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:80
```
For a robust setup, use **Nginx** as a reverse proxy and **systemd** to keep the service running.

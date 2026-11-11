## How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/ruchadange1/sanjivani-sj-14-rationsahayak.git
cd sanjivani-sj-14-rationsahayak
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

For Windows:

```bash
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run FastAPI Application

```bash
python -m uvicorn app.main:app --reload
```

### 6. Open API Documentation

http://127.0.0.1:8000/docs

### 7. Check Application Health

http://127.0.0.1:8000/health

### 8. Run Data Exploration

```bash
python analysis/explore.py
```
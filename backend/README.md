# Mandi Bhav Bot - Backend (FastAPI + PostgreSQL + AIML)

This is the backend service for **Mandi Bhav Bot** (Cropora AI), providing:
1. **PostgreSQL Database** for agricultural market intelligence (Commodities, Mandis, Price Records, Query Logs, Forecast Records).
2. **NLP Query Understanding** (extracting crop, mandi, and intent from Hindi, English, and Hinglish queries).
3. **Time-Series ML Forecasting** (ARIMA and exponential baseline for 7-day future price predictions with confidence intervals).
4. **REST APIs** for the Flutter Web and mobile client.

---

## 🗄️ PostgreSQL Setup

### 1. Configure Connection String
Create or edit `.env` in `backend/`:
```env
# PostgreSQL connection string
# Format: postgresql+psycopg://<user>:<password>@<host>:<port>/<database_name>
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/mandi_bhav_db

HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 2. Create the Database in PostgreSQL
Using `psql` or pgAdmin:
```sql
CREATE DATABASE mandi_bhav_db;
```

### 3. Initialize & Seed PostgreSQL Tables
Run the initialization script from the project root:
```bash
python -m backend.app.init_db
```
This automatically creates the following tables:
- `commodities` (Tomato, Potato, Onion)
- `mandis` (Lucknow, Kanpur, Agra)
- `price_records` (30 days of Agmarknet historical daily records)
- `query_logs` (User query history and parsing accuracy)
- `forecast_records` (Generated AI predictions)

---

## 🚀 Running the Backend

### Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Start the FastAPI Server
```bash
uvicorn backend.app.main:app --reload --port 8000
```

The interactive API documentation is accessible at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check & PostgreSQL connection status |
| `GET` | `/api/commodities` | List supported commodities |
| `GET` | `/api/mandis` | List supported mandis |
| `GET` | `/api/prices/latest?commodity=Tomato&mandi=Lucknow` | Get latest price record (Min, Max, Modal) |
| `GET` | `/api/prices/history?commodity=Tomato&mandi=Lucknow&days=7` | 7-day price history & trend calculation |
| `GET` | `/api/forecast?commodity=Tomato&mandi=Lucknow&days=7` | 7-day ARIMA forecast with confidence bounds |
| `POST` | `/api/query` | Natural language query (e.g. `{"query": "Tamatar ka bhav Lucknow mandi mein?"}`) |

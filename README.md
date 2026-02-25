# AI-Powered Goal-Based Expense Intelligence Backend

A strictly validated, fully type-safe, Clean Architecture FastAPI backend.

## Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0 (Async)
- **Validation**: Pydantic v2 (Strict Mode)
- **Database**: PostgreSQL
- **Auth**: JWT (Access + Refresh) in HTTP-only Cookies
- **AI**: Gemini Pro Skeleton
- **Infrastructure**: Docker & Docker Compose

## Getting Started

### 1. Setup Environment
```bash
cp .env.example .env
# Edit .env and set SECRET_KEY and DATABASE_URL
```

### 2. Run with Docker
```bash
docker-compose up --build
```

### 3. Local Development
```bash
# Create venv
python -m venv env
source env/bin/activate  # or .\env\Scripts\activate

# Install deps
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## API Response Contract
All responses follow this envelope:
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "message": "Operation successful"
}
```

## Next.js Integration Example (Axios)
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  withCredentials: true, // Crucial for HTTP-only cookies
});

// Login Example
const login = async (email, password) => {
  const { data } = await api.post('/auth/login', { email, password });
  return data.data; // UserInDB object
};

// Fetch Expenses
const getExpenses = async () => {
  const { data } = await api.get('/expenses');
  return data.data; // List of ExpenseInDB
};
```

## Modules
- **AUTH**: Register, Login (Cookies), Refresh, Logout, Me.
- **EXPENSES**: CRUD with categories, emotions, and monthly summaries.
- **POTS**: Savings goals with progress and priority.
- **AI**: Intelligent spending analysis (Gemini Pro).

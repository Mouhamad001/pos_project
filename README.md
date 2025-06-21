# POS System

A modern Point of Sale (POS) system built with FastAPI and React.

## Features

- User authentication with JWT tokens
- Product management
- Customer management
- Sales management
- Real-time stock updates
- Responsive design

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

## Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with the following content:
```
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=sqlite:///./pos_system.db
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
```

4. Run the backend server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create a `.env` file in the frontend directory with the following content:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

3. Run the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`

## API Documentation

Once the backend server is running, you can access:
- Swagger UI documentation at `http://localhost:8000/docs`
- ReDoc documentation at `http://localhost:8000/redoc`

## Development

### Backend

The backend is built with:
- FastAPI
- SQLAlchemy
- Pydantic
- JWT authentication

### Frontend

The frontend is built with:
- React
- TypeScript
- Material-UI
- React Router
- Axios

## License

MIT 
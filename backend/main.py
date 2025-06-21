from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import Dict
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from database import init_db
from routers import auth, products, customers, sales, invoices, reports
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="POS System API",
    description="API for Point of Sale System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handling middleware
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(sales.router, prefix="/sales", tags=["Sales"])
app.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])

# Serve Frontend
STATIC_FILES_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(STATIC_FILES_DIR, "static")),
    name="static"
)

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    index_path = os.path.join(STATIC_FILES_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not built. Run `npm run build` in the frontend directory."}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {
        "message": "Welcome to POS System API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
try:
    from fastapi import FastAPI
    print("FastAPI imported successfully")
    
    from .database import init_db
    print("Database module imported successfully")
    
    from .models import User
    print("Models module imported successfully")
    
    from .auth import get_password_hash
    print("Auth module imported successfully")
    
    from .routers import auth, products, customers, sales, invoices, reports
    print("All routers imported successfully")
    
    print("All imports successful!")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc() 
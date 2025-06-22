from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class TokenRefresh(BaseModel):
    refresh_token: str

# Product schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    stock: int = Field(..., ge=0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Customer schemas
class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            import re
            pattern = r'^\+?1?\d{9,15}$'
            if not re.match(pattern, v):
                raise ValueError('Invalid phone number format')
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            import re
            pattern = r'^\+?1?\d{9,15}$'
            if not re.match(pattern, v):
                raise ValueError('Invalid phone number format')
        return v

class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Sale schemas
class SaleItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class SaleItemCreate(SaleItemBase):
    pass

class SaleItem(SaleItemBase):
    id: int
    sale_id: int
    price: Decimal
    created_at: datetime
    product: Product

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    customer_id: Optional[int] = None
    items: List[SaleItemCreate]

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int
    user_id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[SaleItem]

    class Config:
        from_attributes = True

class SalesFilterParams(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    customer_id: Optional[int] = None
    product_id: Optional[int] = None

# Invoice schemas
class InvoiceItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal
    discount: Decimal = Field(default=0, ge=0)

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItem(InvoiceItemBase):
    id: int
    invoice_id: int
    created_at: datetime
    product: Product

    class Config:
        from_attributes = True

class InvoiceBase(BaseModel):
    sale_id: int
    customer_id: Optional[int] = None
    tax_amount: Decimal = Field(default=0, ge=0)
    discount_amount: Decimal = Field(default=0, ge=0)
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    items: List[InvoiceItemCreate]

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int
    invoice_number: str
    user_id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[InvoiceItem]
    customer: Optional[Customer] = None
    user: User

    class Config:
        from_attributes = True 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Any
from ..database import get_db
from .. import models
from .. import schemas
from ..auth import get_current_active_user
from decimal import Decimal
import uuid
from datetime import datetime

router = APIRouter()

def generate_invoice_number():
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"

@router.get("/", response_model=List[schemas.Invoice])
def get_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    try:
        invoices = db.query(models.Invoice).options(
            joinedload(models.Invoice.items).joinedload(models.InvoiceItem.product),
            joinedload(models.Invoice.customer),
            joinedload(models.Invoice.user)
        ).offset(skip).limit(limit).all()
        return invoices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving invoices"
        )

@router.post("/", response_model=schemas.Invoice, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice: schemas.InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    try:
        # Validate sale exists
        sale = db.query(models.Sale).filter(models.Sale.id == invoice.sale_id).first()
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )

        # Validate customer if provided
        if invoice.customer_id:
            customer = db.query(models.Customer).filter(models.Customer.id == invoice.customer_id).first()
            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found"
                )

        # Calculate total amount
        total_amount = Decimal('0')
        for item in invoice.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {item.product_id} not found"
                )
            
            item_total = Decimal(str(item.unit_price)) * item.quantity
            item_discount = Decimal(str(item.discount))
            total_amount += item_total - item_discount

        # Add tax and discount
        total_amount += Decimal(str(invoice.tax_amount))
        total_amount -= Decimal(str(invoice.discount_amount))

        # Create invoice
        db_invoice = models.Invoice(
            invoice_number=generate_invoice_number(),
            sale_id=invoice.sale_id,
            customer_id=invoice.customer_id,
            user_id=current_user.id,
            total_amount=float(total_amount),
            tax_amount=float(invoice.tax_amount),
            discount_amount=float(invoice.discount_amount),
            payment_method=invoice.payment_method,
            notes=invoice.notes,
            status="pending"
        )
        db.add(db_invoice)
        db.flush()

        # Create invoice items
        for item in invoice.items:
            invoice_item = models.InvoiceItem(
                invoice_id=db_invoice.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                discount=float(item.discount)
            )
            db.add(invoice_item)

        db.commit()
        
        # Reload the invoice with all related data
        db_invoice = db.query(models.Invoice).options(
            joinedload(models.Invoice.items).joinedload(models.InvoiceItem.product),
            joinedload(models.Invoice.customer),
            joinedload(models.Invoice.user)
        ).filter(models.Invoice.id == db_invoice.id).first()
        
        return db_invoice
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating invoice"
        )

@router.get("/{invoice_id}", response_model=schemas.Invoice)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(models.Invoice).options(
            joinedload(models.Invoice.items).joinedload(models.InvoiceItem.product),
            joinedload(models.Invoice.customer),
            joinedload(models.Invoice.user)
        ).filter(models.Invoice.id == invoice_id).first()
        
        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving invoice"
        )

@router.put("/{invoice_id}/status", response_model=schemas.Invoice)
def update_invoice_status(
    invoice_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        if status not in ["pending", "paid", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )
        
        invoice.status = status
        db.commit()
        db.refresh(invoice)
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating invoice status"
        ) 
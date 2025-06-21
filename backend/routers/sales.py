from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Any, Optional
from database import get_db
import models
import schemas
from auth import get_current_user
from decimal import Decimal
from utils.export import export_sales_to_csv
from datetime import datetime
from fastapi.responses import StreamingResponse
from io import StringIO

router = APIRouter()

@router.get("/", response_model=List[schemas.Sale])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    filters: schemas.SalesFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        query = db.query(models.Sale).options(
            joinedload(models.Sale.items).joinedload(models.SaleItem.product)
        )

        if filters.start_date:
            query = query.filter(models.Sale.created_at >= filters.start_date)
        if filters.end_date:
            query = query.filter(models.Sale.created_at <= filters.end_date)
        if filters.customer_id:
            query = query.filter(models.Sale.customer_id == filters.customer_id)
        if filters.product_id:
            query = query.join(models.Sale.items).filter(models.SaleItem.product_id == filters.product_id)

        sales = query.offset(skip).limit(limit).all()
        return sales
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving sales"
        )

@router.post("/", response_model=schemas.Sale, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale: schemas.SaleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # Validate customer exists if provided
        if sale.customer_id:
            customer = db.query(models.Customer).filter(models.Customer.id == sale.customer_id).first()
            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found"
                )

        # Validate items
        if not sale.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sale must have at least one item"
            )

        # Calculate total and validate products
        total_amount = Decimal('0')
        for item in sale.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {item.product_id} not found"
                )
            
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {product.name}"
                )
            
            total_amount += Decimal(str(product.price)) * item.quantity

        # Create sale
        db_sale = models.Sale(
            customer_id=sale.customer_id,
            user_id=current_user.id,
            total_amount=float(total_amount)
        )
        db.add(db_sale)
        db.flush()  # Get the sale ID

        # Create sale items and update stock
        for item in sale.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            sale_item = models.SaleItem(
                sale_id=db_sale.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=product.price
            )
            db.add(sale_item)
            
            # Update product stock
            product.stock -= item.quantity

        db.commit()
        
        # Reload the sale with all related data
        db_sale = db.query(models.Sale).options(
            joinedload(models.Sale.items).joinedload(models.SaleItem.product)
        ).filter(models.Sale.id == db_sale.id).first()
        
        return db_sale
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating sale"
        )

@router.get("/{sale_id}", response_model=schemas.Sale)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
        if sale is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving sale"
        )

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
        if sale is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )

        # Restore product stock
        for item in sale.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity

        db.delete(sale)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting sale"
        )

@router.put("/{sale_id}/status", response_model=schemas.Sale)
def update_sale_status(
    sale_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    db_sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if db_sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    if status not in ["completed", "pending", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    db_sale.status = status
    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.get("/export/csv")
def export_sales_csv(
    filters: schemas.SalesFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        csv_data = export_sales_to_csv(db, filters.start_date, filters.end_date, filters.customer_id, filters.product_id)
        output = StringIO(csv_data)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=sales_export.csv"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting sales data"
        ) 
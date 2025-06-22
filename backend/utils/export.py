import csv
from io import StringIO
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from .. import models

def export_to_csv(data: List[Dict[str, Any]], headers: List[str]) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()

def export_sales_to_csv(db: Session, 
                        start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None,
                        customer_id: Optional[int] = None,
                        product_id: Optional[int] = None) -> str:
    query = db.query(models.Sale)
    
    if start_date:
        query = query.filter(models.Sale.created_at >= start_date)
    if end_date:
        query = query.filter(models.Sale.created_at <= end_date)
    if customer_id:
        query = query.filter(models.Sale.customer_id == customer_id)
    if product_id:
        query = query.join(models.Sale.items).filter(models.SaleItem.product_id == product_id)

    sales = query.all()
    
    data = []
    for sale in sales:
        sale_data = {
            'Sale ID': sale.id,
            'Date': sale.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Customer': sale.customer.name if sale.customer else 'N/A',
            'Total Amount': f"${sale.total_amount:.2f}",
            'Items': ', '.join([f"{item.product.name} x{item.quantity}" for item in sale.items])
        }
        data.append(sale_data)
    
    headers = ['Sale ID', 'Date', 'Customer', 'Total Amount', 'Items']
    return export_to_csv(data, headers)

def export_invoices_to_csv(db: Session, start_date: datetime = None, end_date: datetime = None) -> str:
    query = db.query(models.Invoice)
    
    if start_date:
        query = query.filter(models.Invoice.created_at >= start_date)
    if end_date:
        query = query.filter(models.Invoice.created_at <= end_date)
    
    invoices = query.all()
    
    data = []
    for invoice in invoices:
        invoice_data = {
            'Invoice Number': invoice.invoice_number,
            'Date': invoice.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Customer': invoice.customer.name if invoice.customer else 'N/A',
            'Total Amount': f"${invoice.total_amount:.2f}",
            'Tax Amount': f"${invoice.tax_amount:.2f}",
            'Discount Amount': f"${invoice.discount_amount:.2f}",
            'Status': invoice.status,
            'Payment Method': invoice.payment_method or 'N/A'
        }
        data.append(invoice_data)
    
    headers = ['Invoice Number', 'Date', 'Customer', 'Total Amount', 'Tax Amount', 
              'Discount Amount', 'Status', 'Payment Method']
    return export_to_csv(data, headers)

def export_inventory_to_csv(db: Session) -> str:
    products = db.query(models.Product).all()
    
    data = []
    for product in products:
        product_data = {
            'Product ID': product.id,
            'Name': product.name,
            'Description': product.description or 'N/A',
            'Price': f"${product.price:.2f}",
            'Stock': product.stock,
            'Last Updated': product.updated_at.strftime('%Y-%m-%d %H:%M:%S') if product.updated_at else 'N/A'
        }
        data.append(product_data)
    
    headers = ['Product ID', 'Name', 'Description', 'Price', 'Stock', 'Last Updated']
    return export_to_csv(data, headers) 
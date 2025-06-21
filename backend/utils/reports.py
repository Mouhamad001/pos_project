from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
import models
from typing import Dict, Any, List
import json
import os
from pathlib import Path

REPORTS_DIR = Path("reports")

def ensure_reports_directory():
    REPORTS_DIR.mkdir(exist_ok=True)

def save_report(data: Dict[str, Any], report_type: str, period: str):
    ensure_reports_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{report_type}_{period}_{timestamp}.json"
    filepath = REPORTS_DIR / filename
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    return filepath

def generate_sales_report(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    # Get total sales
    total_sales = db.query(func.sum(models.Sale.total_amount)).filter(
        models.Sale.created_at.between(start_date, end_date)
    ).scalar() or 0
    
    # Get number of transactions
    num_transactions = db.query(func.count(models.Sale.id)).filter(
        models.Sale.created_at.between(start_date, end_date)
    ).scalar() or 0
    
    # Get top selling products
    top_products = db.query(
        models.Product.name,
        func.sum(models.SaleItem.quantity).label('total_quantity'),
        func.sum(models.SaleItem.quantity * models.SaleItem.price).label('total_revenue')
    ).join(models.SaleItem).join(models.Sale).filter(
        models.Sale.created_at.between(start_date, end_date)
    ).group_by(models.Product.id).order_by(func.sum(models.SaleItem.quantity).desc()).limit(10).all()
    
    # Get sales by day
    daily_sales = db.query(
        func.date(models.Sale.created_at).label('date'),
        func.sum(models.Sale.total_amount).label('total')
    ).filter(
        models.Sale.created_at.between(start_date, end_date)
    ).group_by(func.date(models.Sale.created_at)).all()
    
    report_data = {
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'summary': {
            'total_sales': float(total_sales),
            'num_transactions': num_transactions,
            'average_transaction': float(total_sales / num_transactions) if num_transactions > 0 else 0
        },
        'top_products': [
            {
                'name': product.name,
                'quantity_sold': product.total_quantity,
                'revenue': float(product.total_revenue)
            }
            for product in top_products
        ],
        'daily_sales': [
            {
                'date': str(sale.date),
                'total': float(sale.total)
            }
            for sale in daily_sales
        ]
    }
    
    return report_data

def generate_weekly_report(db: Session) -> Dict[str, Any]:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    report_data = generate_sales_report(db, start_date, end_date)
    save_report(report_data, 'weekly_sales', 'weekly')
    return report_data

def generate_monthly_report(db: Session) -> Dict[str, Any]:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    report_data = generate_sales_report(db, start_date, end_date)
    save_report(report_data, 'monthly_sales', 'monthly')
    return report_data

def get_latest_report(report_type: str, period: str) -> Dict[str, Any]:
    ensure_reports_directory()
    pattern = f"{report_type}_{period}_*.json"
    report_files = sorted(REPORTS_DIR.glob(pattern), reverse=True)
    
    if not report_files:
        return None
    
    with open(report_files[0], 'r') as f:
        return json.load(f) 
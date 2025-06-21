from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
from utils.reports import generate_weekly_report, generate_monthly_report, get_latest_report
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
import json

router = APIRouter()

@router.get("/weekly")
def get_weekly_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        report_data = generate_weekly_report(db)
        return JSONResponse(content=report_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating weekly report"
        )

@router.get("/monthly")
def get_monthly_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        report_data = generate_monthly_report(db)
        return JSONResponse(content=report_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating monthly report"
        )

@router.get("/latest/{report_type}/{period}")
def get_latest_report_endpoint(
    report_type: str,
    period: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        report_data = get_latest_report(report_type, period)
        if not report_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {period} {report_type} report found"
            )
        return JSONResponse(content=report_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving report"
        ) 
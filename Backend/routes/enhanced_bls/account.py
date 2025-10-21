from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from loguru import logger
from pydantic import BaseModel
from datetime import datetime

from database.config import get_db

# Simple request model for basic account creation
class SimpleAccountRequest(BaseModel):
    email: str
    first_name: Optional[str] = "Test"
    last_name: Optional[str] = "User"
    password: Optional[str] = "TestPassword123"

router = APIRouter()

@router.post("/create-real-account")
async def create_real_bls_account(
    account_data: SimpleAccountRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    # Import locally to avoid circular imports
    from main import BLSAccountCreate
    from services.enhanced_bls_service import enhanced_bls_service
    
    try:
        logger.info(f"Creating real BLS account for: {account_data.email}")
        
        # Convert simple request to full BLSAccountCreate object
        full_account_data = BLSAccountCreate(
            first_name=account_data.first_name,
            last_name=account_data.last_name,
            family_name=account_data.last_name,
            date_of_birth=datetime(1990, 1, 1),  # Default date
            gender="Male",
            marital_status="Single",
            passport_number="A12345678",  # Default passport
            passport_type="Ordinary",
            passport_issue_date=datetime(2020, 1, 1),
            passport_expiry_date=datetime(2030, 1, 1),
            passport_issue_place="Algiers",
            passport_issue_country="Algeria",
            email=account_data.email,
            mobile="0555123456",  # Default mobile
            phone_country_code="+213",
            birth_country="Algeria",
            country_of_residence="Algeria",
            number_of_members=1,
            relationship="Self",
            primary_applicant=True,
            password=account_data.password
        )
        
        result = await enhanced_bls_service.create_real_bls_account(full_account_data, db)
        if result.success:
            return {
                "success": True,
                "message": result.message or "BLS account created successfully",
                "account_id": result.account_id,
                "email": account_data.email,
                "status": result.status or "completed",
                "captcha_id": result.captcha_id,
                "captcha_data_param": result.captcha_data_param
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to create BLS account: {result.error_message}")
    except Exception as e:
        logger.error(f"Error creating real BLS account: {e}")
        raise HTTPException(status_code=500, detail=str(e))



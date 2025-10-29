from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from loguru import logger
from pydantic import BaseModel
from datetime import datetime

from database.config import get_db
from models.database import Account

# Request models for account management
class AccountCreateRequest(BaseModel):
    # Personal Information (BLS format)
    sur_name: Optional[str] = None  # BLS: SurName (Family Name) - optional
    first_name: str  # BLS: FirstName (Given Name) - required
    last_name: str  # BLS: LastName - required
    family_name: Optional[str] = None  # Legacy field
    date_of_birth: str  # YYYY-MM-DD format
    gender: str = "Male"
    marital_status: str = "Single"
    
    # Passport Information (BLS format)
    passport_number: str
    passport_type: str = "Ordinary"
    passport_issue_date: str  # YYYY-MM-DD format
    passport_expiry_date: str  # YYYY-MM-DD format
    passport_issue_place: str  # BLS: Required!
    passport_issue_country: Optional[str] = None
    
    # Contact Information
    email: str
    mobile: str
    phone_country_code: str = "+213"
    
    # Location Information
    birth_country: Optional[str] = None
    country_of_residence: Optional[str] = None
    
    # Additional Information
    number_of_members: int = 1
    relationship: str = "Self"
    primary_applicant: bool = True
    
    # Credentials
    password: str

class AccountUpdateRequest(BaseModel):
    # Personal Information (BLS format)
    sur_name: Optional[str] = None  # BLS: SurName
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    family_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    
    # Passport Information
    passport_number: Optional[str] = None
    passport_type: Optional[str] = None
    passport_issue_date: Optional[str] = None
    passport_expiry_date: Optional[str] = None
    passport_issue_place: Optional[str] = None
    passport_issue_country: Optional[str] = None
    
    # Contact Information
    email: Optional[str] = None
    mobile: Optional[str] = None
    phone_country_code: Optional[str] = None
    birth_country: Optional[str] = None
    country_of_residence: Optional[str] = None
    number_of_members: Optional[int] = None
    relationship: Optional[str] = None
    primary_applicant: Optional[bool] = None
    password: Optional[str] = None
    is_enabled: Optional[bool] = None

class BLSAccountCreateRequest(BaseModel):
    account_ids: List[int]

class AccountResponse(BaseModel):
    id: int
    # Personal Information (BLS format)
    sur_name: Optional[str]  # BLS: SurName
    first_name: str
    last_name: str
    family_name: Optional[str]
    date_of_birth: str
    gender: str
    marital_status: str
    # Passport Information
    passport_number: str
    passport_type: str
    passport_issue_date: str
    passport_expiry_date: str
    passport_issue_place: Optional[str]
    passport_issue_country: Optional[str]
    # Contact Information
    email: str
    mobile: str
    phone_country_code: str
    # Location Information
    birth_country: Optional[str]
    country_of_residence: Optional[str]
    # Additional Information
    number_of_members: int
    relationship: str
    primary_applicant: bool
    # Status
    status: str
    bls_status: str
    bls_username: Optional[str]
    bls_created_at: Optional[datetime]
    bls_error_message: Optional[str]
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    processing_attempts: int
    last_processing_attempt: Optional[datetime]

    class Config:
        from_attributes = True

router = APIRouter()

@router.post("/create", response_model=AccountResponse)
async def create_account(
    account_data: AccountCreateRequest,
    db: Session = Depends(get_db)
) -> AccountResponse:
    """Create a new account (without BLS creation)"""
    try:
        logger.info(f"Creating account for: {account_data.email}")
        
        # Check if email already exists
        existing_account = db.query(Account).filter(Account.email == account_data.email).first()
        if existing_account:
            raise HTTPException(status_code=400, detail="Account with this email already exists")
        
        # Check if passport number already exists
        existing_passport = db.query(Account).filter(Account.passport_number == account_data.passport_number).first()
        if existing_passport:
            raise HTTPException(status_code=400, detail="Account with this passport number already exists")
        
        # Create new account (BLS format)
        new_account = Account(
            sur_name=account_data.sur_name,  # BLS: SurName
            first_name=account_data.first_name,
            last_name=account_data.last_name,
            family_name=account_data.family_name,
            date_of_birth=account_data.date_of_birth,
            gender=account_data.gender,
            marital_status=account_data.marital_status,
            passport_number=account_data.passport_number,
            passport_type=account_data.passport_type,
            passport_issue_date=account_data.passport_issue_date,
            passport_expiry_date=account_data.passport_expiry_date,
            passport_issue_place=account_data.passport_issue_place,
            passport_issue_country=account_data.passport_issue_country,
            email=account_data.email,
            mobile=account_data.mobile,
            phone_country_code=account_data.phone_country_code,
            birth_country=account_data.birth_country,
            country_of_residence=account_data.country_of_residence,
            number_of_members=account_data.number_of_members,
            relationship=account_data.relationship,
            primary_applicant=account_data.primary_applicant,
            password=account_data.password,
            status="created",
            bls_status="not_created"
        )
        
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        
        logger.info(f"Account created successfully with ID: {new_account.id}")
        return AccountResponse.from_orm(new_account)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    bls_status: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[AccountResponse]:
    """Get all accounts with optional filtering"""
    try:
        query = db.query(Account)
        
        if status:
            query = query.filter(Account.status == status)
        if bls_status:
            query = query.filter(Account.bls_status == bls_status)
        
        accounts = query.offset(skip).limit(limit).all()
        return [AccountResponse.from_orm(account) for account in accounts]
        
    except Exception as e:
        logger.error(f"Error getting accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: Session = Depends(get_db)
) -> AccountResponse:
    """Get a specific account by ID"""
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return AccountResponse.from_orm(account)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting account {account_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_data: AccountUpdateRequest,
    db: Session = Depends(get_db)
) -> AccountResponse:
    """Update an existing account"""
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Update only provided fields
        update_data = account_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)
        
        account.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(account)
        
        logger.info(f"Account {account_id} updated successfully")
        return AccountResponse.from_orm(account)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account {account_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Delete an account"""
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        db.delete(account)
        db.commit()
        
        logger.info(f"Account {account_id} deleted successfully")
        return {"success": True, "message": "Account deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account {account_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-bls")
async def create_bls_accounts(
    request: BLSAccountCreateRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create BLS accounts for multiple existing accounts"""
    try:
        logger.info(f"Creating BLS accounts for {len(request.account_ids)} accounts")
        
        # Import the multi-account BLS service
        from services.multi_account_bls_service import multi_account_bls_service
        
        # Get accounts to process
        accounts = db.query(Account).filter(
            Account.id.in_(request.account_ids),
            Account.bls_status == "not_created"
        ).all()
        
        if not accounts:
            raise HTTPException(status_code=400, detail="No valid accounts found for BLS creation")
        
        # Update status to creating
        for account in accounts:
            account.bls_status = "creating"
            account.status = "bls_creating"
            account.last_processing_attempt = datetime.utcnow()
            account.processing_attempts += 1
        
        db.commit()
        
        # Start BLS creation process concurrently
        result = await multi_account_bls_service.create_bls_accounts_concurrent(
            request.account_ids, db
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting BLS account creation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retry-failed-bls")
async def retry_failed_bls_accounts(
    request: Optional[BLSAccountCreateRequest] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Retry BLS creation for failed accounts"""
    try:
        from services.multi_account_bls_service import multi_account_bls_service
        
        account_ids = request.account_ids if request else None
        result = await multi_account_bls_service.retry_failed_accounts(account_ids, db)
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrying failed BLS accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processing-status")
async def get_processing_status(
    account_ids: Optional[str] = None,  # Comma-separated account IDs
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get processing status for accounts"""
    try:
        from services.multi_account_bls_service import multi_account_bls_service
        
        if account_ids:
            account_ids_list = [int(id.strip()) for id in account_ids.split(",")]
        else:
            # Get all accounts
            accounts = db.query(Account).all()
            account_ids_list = [account.id for account in accounts]
        
        result = await multi_account_bls_service.get_processing_status(account_ids_list, db)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_account_stats(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get account statistics summary"""
    try:
        total_accounts = db.query(Account).count()
        created_accounts = db.query(Account).filter(Account.status == "created").count()
        bls_creating = db.query(Account).filter(Account.bls_status == "creating").count()
        bls_created = db.query(Account).filter(Account.bls_status == "created").count()
        bls_failed = db.query(Account).filter(Account.bls_status == "failed").count()
        
        return {
            "total_accounts": total_accounts,
            "created_accounts": created_accounts,
            "bls_creating": bls_creating,
            "bls_created": bls_created,
            "bls_failed": bls_failed,
            "bls_not_created": total_accounts - bls_creating - bls_created - bls_failed
        }
        
    except Exception as e:
        logger.error(f"Error getting account stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

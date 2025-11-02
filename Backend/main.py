"""
Booking Visa Bot Backend
Modern Python backend with FastAPI and SQLite for Tesla config management
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
import asyncio
from loguru import logger

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✅ Loaded environment variables from .env file")
except ImportError:
    logger.warning("⚠️ python-dotenv not installed, skipping .env loading")

# Optional imports for enhanced features
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logger.warning("aiohttp not available. Enhanced BLS features will be limited.")

# Database setup
DATABASE_URL = "sqlite:///./tesla_config.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class TeslaConfig(Base):
    __tablename__ = "tesla_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text, nullable=True)
    api_key = Column(String(255), nullable=True)
    base_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Tesla-specific fields
    bls_website_url = Column(String(255), default="https://algeria.blsspainglobal.com")
    proxy_enabled = Column(Boolean, default=True)
    captcha_service_url = Column(String(255), default="https://api.nocaptcha.io")
    aws_waf_bypass_enabled = Column(Boolean, default=True)
    
    # Advanced settings
    max_retry_attempts = Column(Integer, default=3)
    request_timeout = Column(Integer, default=30)
    user_agent = Column(String(500), default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

class Proxy(Base):
    __tablename__ = "proxies"
    
    id = Column(Integer, primary_key=True, index=True)
    host = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(100), nullable=True)
    password = Column(String(100), nullable=True)
    country = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    validation_status = Column(String(50), default="pending")
    last_validated = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BLSAccount(Base):
    __tablename__ = "bls_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    family_name = Column(String(100), nullable=True)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(10), default="Male")
    marital_status = Column(String(20), default="Single")
    
    # Passport Information
    passport_number = Column(String(50), nullable=False, unique=True)
    passport_type = Column(String(20), default="Ordinary")
    passport_issue_date = Column(DateTime, nullable=False)
    passport_expiry_date = Column(DateTime, nullable=False)
    passport_issue_place = Column(String(100), nullable=True)
    passport_issue_country = Column(String(100), nullable=True)
    
    # Contact Information
    email = Column(String(255), nullable=False, unique=True)
    mobile = Column(String(20), nullable=False)
    phone_country_code = Column(String(10), default="+213")
    
    # Location Information
    birth_country = Column(String(100), nullable=True)
    country_of_residence = Column(String(100), nullable=True)
    
    # Additional Information
    number_of_members = Column(Integer, default=1)
    relationship = Column(String(20), default="Self")
    primary_applicant = Column(Boolean, default=True)
    
    # Account Credentials
    password = Column(String(255), nullable=False)
    
    # Account Status
    status = Column(String(20), default="inactive")  # inactive, active, suspended, banned
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    # BLS-specific fields
    bls_username = Column(String(255), nullable=True)
    bls_password = Column(String(255), nullable=True)
    proxy_id = Column(Integer, nullable=True)
    login_attempts = Column(Integer, default=0)
    last_login_attempt = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    last_error = Column(Text, nullable=True)
    last_activity = Column(DateTime, nullable=True)

# Pydantic Models
class TeslaConfigBase(BaseModel):
    name: str
    description: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_active: bool = True
    bls_website_url: str = "https://algeria.blsspainglobal.com"
    proxy_enabled: bool = True
    captcha_service_url: str = "https://api.nocaptcha.io"
    aws_waf_bypass_enabled: bool = True
    max_retry_attempts: int = 3
    request_timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

class TeslaConfigCreate(TeslaConfigBase):
    pass

class TeslaConfigUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_active: Optional[bool] = None
    bls_website_url: Optional[str] = None
    proxy_enabled: Optional[bool] = None
    captcha_service_url: Optional[str] = None
    aws_waf_bypass_enabled: Optional[bool] = None
    max_retry_attempts: Optional[int] = None
    request_timeout: Optional[int] = None
    user_agent: Optional[str] = None

class TeslaConfigResponse(TeslaConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProxyBase(BaseModel):
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    is_active: bool = True

class ProxyCreate(BaseModel):
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    country: str = "DZ"

class ProxyResponse(ProxyBase):
    id: int
    validation_status: str
    last_validated: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# BLS Account Pydantic Models
class BLSAccountBase(BaseModel):
    # Personal Information
    first_name: str
    last_name: str
    family_name: Optional[str] = None
    date_of_birth: datetime
    gender: str = "Male"
    marital_status: str = "Single"
    
    # Passport Information
    passport_number: str
    passport_type: str = "Ordinary"
    passport_issue_date: datetime
    passport_expiry_date: datetime
    passport_issue_place: Optional[str] = None
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
    
    # Account Credentials
    password: str

class BLSAccountCreate(BLSAccountBase):
    pass

class BLSAccountCreationResult(BaseModel):
    success: bool
    status: Optional[str] = None
    account_id: Optional[str] = None
    email: Optional[str] = None
    message: Optional[str] = None
    error_message: Optional[str] = None
    captcha_id: Optional[str] = None
    captcha_data_param: Optional[str] = None

class BLSAccountUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    family_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    passport_number: Optional[str] = None
    passport_type: Optional[str] = None
    passport_issue_date: Optional[datetime] = None
    passport_expiry_date: Optional[datetime] = None
    passport_issue_place: Optional[str] = None
    passport_issue_country: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    phone_country_code: Optional[str] = None
    birth_country: Optional[str] = None
    country_of_residence: Optional[str] = None
    number_of_members: Optional[int] = None
    relationship: Optional[str] = None
    primary_applicant: Optional[bool] = None
    password: Optional[str] = None
    status: Optional[str] = None
    is_enabled: Optional[bool] = None

class BLSAccountResponse(BLSAccountBase):
    id: int
    status: str
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    bls_username: Optional[str] = None
    proxy_id: Optional[int] = None
    login_attempts: int
    last_login_attempt: Optional[datetime] = None
    error_message: Optional[str] = None
    last_error: Optional[str] = None
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="Booking Visa Bot Backend",
    description="Modern Python backend for Tesla config management with AWS WAF bypass",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
try:
    from routes.enhanced_bls import router as enhanced_bls_router
    app.include_router(enhanced_bls_router)
    logger.info("✅ Enhanced BLS routes included")
except ImportError as e:
    logger.warning(f"⚠️ Could not import enhanced BLS routes: {e}")

# Tesla Config CRUD Operations
@app.post("/api/tesla-configs/", response_model=TeslaConfigResponse)
def create_tesla_config(config: TeslaConfigCreate, db: Session = Depends(get_db)):
    """Create a new Tesla configuration"""
    logger.info(f"Creating Tesla config: {config.name}")
    
    # Check if config with same name exists
    existing = db.query(TeslaConfig).filter(TeslaConfig.name == config.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Config with this name already exists")
    
    db_config = TeslaConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    logger.info(f"✅ Created Tesla config: {db_config.id}")
    return db_config

@app.get("/api/tesla-configs/", response_model=List[TeslaConfigResponse])
def get_tesla_configs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all Tesla configurations"""
    logger.info(f"Fetching Tesla configs (skip={skip}, limit={limit})")
    
    configs = db.query(TeslaConfig).offset(skip).limit(limit).all()
    logger.info(f"✅ Found {len(configs)} Tesla configs")
    return configs

@app.get("/api/tesla-configs/{config_id}", response_model=TeslaConfigResponse)
def get_tesla_config(config_id: int, db: Session = Depends(get_db)):
    """Get a specific Tesla configuration"""
    logger.info(f"Fetching Tesla config: {config_id}")
    
    config = db.query(TeslaConfig).filter(TeslaConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Tesla config not found")
    
    logger.info(f"✅ Found Tesla config: {config.name}")
    return config

@app.put("/api/tesla-configs/{config_id}", response_model=TeslaConfigResponse)
def update_tesla_config(config_id: int, config_update: TeslaConfigUpdate, db: Session = Depends(get_db)):
    """Update a Tesla configuration"""
    logger.info(f"Updating Tesla config: {config_id}")
    
    config = db.query(TeslaConfig).filter(TeslaConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Tesla config not found")
    
    # Update only provided fields
    update_data = config_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(config)
    
    logger.info(f"✅ Updated Tesla config: {config.name}")
    return config

@app.delete("/api/tesla-configs/{config_id}")
def delete_tesla_config(config_id: int, db: Session = Depends(get_db)):
    """Delete a Tesla configuration"""
    logger.info(f"Deleting Tesla config: {config_id}")
    
    config = db.query(TeslaConfig).filter(TeslaConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Tesla config not found")
    
    db.delete(config)
    db.commit()
    
    logger.info(f"✅ Deleted Tesla config: {config.name}")
    return {"message": "Tesla config deleted successfully"}

# Proxy CRUD Operations
@app.post("/api/proxies/", response_model=ProxyResponse)
def create_proxy(proxy: ProxyCreate, db: Session = Depends(get_db)):
    """Create a new proxy"""
    logger.info(f"Creating proxy: {proxy.host}:{proxy.port}")
    
    db_proxy = Proxy(**proxy.dict())
    db.add(db_proxy)
    db.commit()
    db.refresh(db_proxy)
    
    logger.info(f"✅ Created proxy: {db_proxy.id}")
    return db_proxy

@app.get("/api/proxies/", response_model=List[ProxyResponse])
def get_proxies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all proxies"""
    logger.info(f"Fetching proxies (skip={skip}, limit={limit})")
    
    proxies = db.query(Proxy).offset(skip).limit(limit).all()
    logger.info(f"✅ Found {len(proxies)} proxies")
    return proxies

@app.get("/api/proxies/{proxy_id}", response_model=ProxyResponse)
def get_proxy(proxy_id: int, db: Session = Depends(get_db)):
    """Get a specific proxy"""
    logger.info(f"Fetching proxy: {proxy_id}")
    
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    
    logger.info(f"✅ Found proxy: {proxy.host}:{proxy.port}")
    return proxy

@app.put("/api/proxies/{proxy_id}", response_model=ProxyResponse)
def update_proxy(proxy_id: int, proxy_update: ProxyCreate, db: Session = Depends(get_db)):
    """Update a proxy"""
    logger.info(f"Updating proxy: {proxy_id}")
    
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    
    # Update fields
    for field, value in proxy_update.dict().items():
        setattr(proxy, field, value)
    
    db.commit()
    db.refresh(proxy)
    
    logger.info(f"✅ Updated proxy: {proxy.host}:{proxy.port}")
    return proxy

@app.delete("/api/proxies/{proxy_id}")
def delete_proxy(proxy_id: int, db: Session = Depends(get_db)):
    """Delete a proxy"""
    logger.info(f"Deleting proxy: {proxy_id}")
    
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    
    db.delete(proxy)
    db.commit()
    
    logger.info(f"✅ Deleted proxy: {proxy.host}:{proxy.port}")
    return {"message": "Proxy deleted successfully"}

# Health check endpoint
@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Booking Visa Bot Backend",
        "version": "1.0.0"
    }

# AWS WAF Bypass endpoints
@app.post("/api/waf-bypass/test")
def test_waf_bypass(request: dict, db: Session = Depends(get_db)):
    """Test AWS WAF bypass functionality"""
    logger.info(f"Testing AWS WAF bypass for: {request.get('url')}")
    
    try:
        from services.aws_waf_service import get_aws_waf_service
        aws_waf_service = get_aws_waf_service()
        
        if not aws_waf_service.is_available():
            raise HTTPException(status_code=503, detail="AWS WAF bypass service not available")
        
        url = request.get('url')
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        result = aws_waf_service.bypass_aws_waf(url)
        
        if result and result['bypassed']:
            return {
                "status_code": result['status_code'],
                "content_length": len(result['content']),
                "solve_time": result.get('solve_time', 0),
                "token": result.get('token', '')[:50] + '...' if result.get('token') else None,
                "bypassed": True
            }
        else:
            return {
                "status_code": result.get('status_code', 0) if result else 0,
                "content_length": len(result.get('content', '')) if result else 0,
                "solve_time": 0,
                "token": None,
                "bypassed": False
            }
            
    except Exception as e:
        logger.error(f"AWS WAF bypass test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# BLS Account endpoints
@app.post("/api/bls-accounts/", response_model=BLSAccountResponse)
def create_bls_account(account: BLSAccountCreate, db: Session = Depends(get_db)):
    """Create a new BLS account"""
    logger.info(f"Creating BLS account for: {account.first_name} {account.last_name}")
    
    # Check if email already exists
    existing_email = db.query(BLSAccount).filter(BLSAccount.email == account.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Check if passport number already exists
    existing_passport = db.query(BLSAccount).filter(BLSAccount.passport_number == account.passport_number).first()
    if existing_passport:
        raise HTTPException(status_code=400, detail="Passport number already exists")
    
    # Validate mobile number (BLS specific)
    if account.mobile.startswith('0'):
        raise HTTPException(status_code=400, detail="Mobile Number Should Not Start With Zero")
    
    if not account.mobile.isdigit() or len(account.mobile) < 8 or len(account.mobile) > 10:
        raise HTTPException(status_code=400, detail="Mobile number must be 8-10 digits")
    
    # Validate passport number (BLS specific)
    if not account.passport_number or len(account.passport_number) < 9:
        raise HTTPException(status_code=400, detail="Passport Number should Start with 2 Alphabet followed with minimum 7 digit")
    
    # Create account
    db_account = BLSAccount(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    logger.info(f"✅ Created BLS account: {db_account.id}")
    return db_account

@app.get("/api/bls-accounts/", response_model=List[BLSAccountResponse])
def get_bls_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all BLS accounts"""
    logger.info(f"Fetching BLS accounts (skip={skip}, limit={limit})")
    
    accounts = db.query(BLSAccount).offset(skip).limit(limit).all()
    logger.info(f"✅ Found {len(accounts)} BLS accounts")
    return accounts

@app.get("/api/bls-accounts/{account_id}", response_model=BLSAccountResponse)
def get_bls_account(account_id: int, db: Session = Depends(get_db)):
    """Get a specific BLS account"""
    logger.info(f"Fetching BLS account: {account_id}")
    
    account = db.query(BLSAccount).filter(BLSAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="BLS account not found")
    
    logger.info(f"✅ Found BLS account: {account.first_name} {account.last_name}")
    return account

@app.put("/api/bls-accounts/{account_id}", response_model=BLSAccountResponse)
def update_bls_account(account_id: int, account_update: BLSAccountUpdate, db: Session = Depends(get_db)):
    """Update a BLS account"""
    logger.info(f"Updating BLS account: {account_id}")
    
    account = db.query(BLSAccount).filter(BLSAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="BLS account not found")
    
    # Update only provided fields
    update_data = account_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(account)
    
    logger.info(f"✅ Updated BLS account: {account.first_name} {account.last_name}")
    return account

@app.delete("/api/bls-accounts/{account_id}")
def delete_bls_account(account_id: int, db: Session = Depends(get_db)):
    """Delete a BLS account"""
    logger.info(f"Deleting BLS account: {account_id}")
    
    account = db.query(BLSAccount).filter(BLSAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="BLS account not found")
    
    db.delete(account)
    db.commit()
    
    logger.info(f"✅ Deleted BLS account: {account.first_name} {account.last_name}")
    return {"message": "BLS account deleted successfully"}

@app.post("/api/bls-accounts/{account_id}/validate")
def validate_bls_account(account_id: int, db: Session = Depends(get_db)):
    """Validate BLS account data"""
    logger.info(f"Validating BLS account: {account_id}")
    
    account = db.query(BLSAccount).filter(BLSAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="BLS account not found")
    
    validation_errors = []
    
    # Mobile validation
    if account.mobile.startswith('0'):
        validation_errors.append("Mobile Number Should Not Start With Zero")
    
    if not account.mobile.isdigit() or len(account.mobile) < 8 or len(account.mobile) > 10:
        validation_errors.append("Mobile number must be 8-10 digits")
    
    # Passport validation (BLS specific - exactly 9 digits only)
    import re
    if not account.passport_number or not re.match(r'^\d{9}$', account.passport_number):
        validation_errors.append("Passport Number must be exactly 9 digits")
    
    # Date validations
    today = datetime.utcnow().date()
    if account.date_of_birth.date() >= today:
        validation_errors.append("Date of birth must be in the past")
    
    if account.passport_issue_date.date() >= today:
        validation_errors.append("Passport issue date must be in the past")
    
    if account.passport_expiry_date.date() <= today:
        validation_errors.append("Passport must not be expired")
    
    if account.passport_issue_date >= account.passport_expiry_date:
        validation_errors.append("Passport expiry date must be after issue date")
    
    is_valid = len(validation_errors) == 0
    
    logger.info(f"✅ BLS account validation: {'PASSED' if is_valid else 'FAILED'}")
    
    return {
        "account_id": account_id,
        "is_valid": is_valid,
        "errors": validation_errors,
        "validated_at": datetime.utcnow()
    }

# Enhanced BLS Routes
@app.get("/api/enhanced-bls/health")
async def enhanced_bls_health_check():
    """Health check for enhanced BLS service"""
    return {
        "status": "healthy",
        "service": "Enhanced BLS Account Creation",
        "timestamp": "2024-01-01T00:00:00Z",
        "endpoints": [
            "/api/enhanced-bls/create-real-account",
            "/api/enhanced-bls/generate-real-email",
            "/api/enhanced-bls/test-email-service",
            "/api/enhanced-bls/get-otp/{email}",
            "/api/enhanced-bls/wait-for-otp/{email}"
        ]
    }

@app.post("/api/enhanced-bls/test-email-service")
async def test_email_service():
    """Test the email service functionality with comprehensive testing"""
    try:
        logger.info("Testing email service with comprehensive checks")
        
        # Check if aiohttp is available
        if not AIOHTTP_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="aiohttp not available. Please install it with: pip install aiohttp"
            )
        
        # Import the email service
        from services.email_service import real_email_service
        
        test_results = {
            "success": True,
            "tests": [],
            "email": None,
            "service": None,
            "message": "Email service test completed"
        }
        
        # Test 1: Generate email
        try:
            email, service_name = await real_email_service.generate_real_email()
            test_results["email"] = email
            test_results["service"] = service_name
            test_results["tests"].append({
                "test": "Email Generation",
                "status": "success",
                "details": f"Generated {email} using {service_name}"
            })
            logger.info(f"Email generation test passed: {email}")
        except Exception as e:
            test_results["tests"].append({
                "test": "Email Generation",
                "status": "failed",
                "details": f"Failed to generate email: {str(e)}"
            })
            logger.error(f"Email generation test failed: {e}")
            test_results["success"] = False
        
        # Test 2: Check email inbox (should be empty initially)
        if test_results["email"]:
            try:
                otp = await real_email_service.get_otp_from_email(test_results["email"], test_results["service"])
                test_results["tests"].append({
                    "test": "Inbox Check",
                    "status": "success",
                    "details": f"Inbox accessible, OTP: {otp or 'None (expected)'}"
                })
                logger.info(f"Inbox check test passed for {test_results['email']}")
            except Exception as e:
                test_results["tests"].append({
                    "test": "Inbox Check",
                    "status": "failed",
                    "details": f"Failed to check inbox: {str(e)}"
                })
                logger.error(f"Inbox check test failed: {e}")
                test_results["success"] = False
        
        # Overall status
        if test_results["success"]:
            test_results["message"] = f"All tests passed! Email service is working correctly with {test_results['service']}"
        else:
            test_results["message"] = "Some tests failed. Check individual test results."
        
        return test_results
        
    except Exception as e:
        logger.error(f"Error testing email service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enhanced-bls/generate-real-email")
async def generate_real_email():
    """Generate a real temporary email that can receive OTPs"""
    try:
        logger.info("Generating real temporary email")
        
        # Check if aiohttp is available
        if not AIOHTTP_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="aiohttp not available. Please install it with: pip install aiohttp"
            )
        
        # Import the email service
        from services.email_service import real_email_service
        
        email, service_name = await real_email_service.generate_real_email()
        
        return {
            "success": True,
            "email": email,
            "service": service_name,
            "message": f"Real email generated using {service_name}"
        }
        
    except Exception as e:
        logger.error(f"Error generating real email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enhanced-bls/get-otp/{email}")
async def get_otp_from_email(email: str, service_name: str = None):
    """Get OTP from email"""
    try:
        logger.info(f"Retrieving OTP from email: {email}")
        
        # Check if aiohttp is available
        if not AIOHTTP_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="aiohttp not available. Please install it with: pip install aiohttp"
            )
        
        # Import the email service
        from services.email_service import real_email_service
        
        otp = await real_email_service.get_otp_from_email(email, service_name)
        
        if otp:
            return {
                "success": True,
                "otp": otp,
                "email": email,
                "service": service_name or "auto-detected",
                "message": "OTP retrieved successfully"
            }
        else:
            return {
                "success": False,
                "otp": None,
                "email": email,
                "service": service_name or "auto-detected",
                "message": "No OTP found in email"
            }
            
    except Exception as e:
        logger.error(f"Error retrieving OTP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enhanced-bls/wait-for-otp/{email}")
async def wait_for_otp(
    email: str, 
    service_name: str = None, 
    timeout_seconds: int = 120
):
    """Wait for OTP to arrive in email"""
    try:
        logger.info(f"Waiting for OTP in email: {email}")
        
        # Check if aiohttp is available
        if not AIOHTTP_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="aiohttp not available. Please install it with: pip install aiohttp"
            )
        
        # Import the email service
        from services.email_service import real_email_service
        
        otp = await real_email_service.wait_for_otp(email, service_name, timeout_seconds)
        
        if otp:
            return {
                "success": True,
                "otp": otp,
                "email": email,
                "service": service_name or "auto-detected",
                "timeout_seconds": timeout_seconds,
                "message": "OTP received successfully"
            }
        else:
            return {
                "success": False,
                "otp": None,
                "email": email,
                "service": service_name or "auto-detected",
                "timeout_seconds": timeout_seconds,
                "message": "Timeout waiting for OTP"
            }
            
    except Exception as e:
        logger.error(f"Error waiting for OTP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enhanced-bls/test-otp-retrieval")
async def test_otp_retrieval():
    """Test OTP retrieval functionality with a sample email"""
    try:
        logger.info("Testing OTP retrieval functionality")
        
        # Check if aiohttp is available
        if not AIOHTTP_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="aiohttp not available. Please install it with: pip install aiohttp"
            )
        
        # Import the email service
        from services.email_service import real_email_service
        
        # Generate a test email
        email, service_name = await real_email_service.generate_real_email()
        
        # Test OTP retrieval (should return None initially)
        otp = await real_email_service.get_otp_from_email(email, service_name)
        
        return {
            "success": True,
            "email": email,
            "service": service_name,
            "otp": otp,
            "message": f"OTP retrieval test completed. Email: {email}, OTP: {otp or 'None (expected)'}",
            "instructions": {
                "step1": f"Send an email with OTP to: {email}",
                "step2": f"Call GET /api/enhanced-bls/get-otp/{email} to retrieve OTP",
                "step3": f"Or call POST /api/enhanced-bls/wait-for-otp/{email} to wait for OTP",
                "note": "OTP patterns supported: 4-digit, 6-digit, 8-digit, and text patterns like 'verification code: 123456'"
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing OTP retrieval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Proxy Management Endpoints
@app.post("/api/proxies/add")
def add_proxy(
    proxy_data: ProxyCreate,
    db: Session = Depends(get_db)
):
    """Add a new proxy to the database"""
    try:
        logger.info(f"Adding proxy: {proxy_data.host}:{proxy_data.port} ({proxy_data.country})")
        
        # Check if proxy already exists (check host, port, and username for session-based proxies)
        existing = db.query(Proxy).filter(
            Proxy.host == proxy_data.host,
            Proxy.port == proxy_data.port,
            Proxy.username == proxy_data.username
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Proxy already exists")
        
        # Create new proxy
        proxy = Proxy(
            host=proxy_data.host,
            port=proxy_data.port,
            username=proxy_data.username,
            password=proxy_data.password,
            country=proxy_data.country,
            is_active=True,
            validation_status="pending"
        )
        
        db.add(proxy)
        db.commit()
        db.refresh(proxy)
        
        logger.info(f"✅ Added proxy: {proxy.id}")
        return {
            "success": True,
            "message": f"Proxy added successfully",
            "proxy_id": proxy.id,
            "proxy": f"{proxy_data.host}:{proxy_data.port}"
        }
        
    except Exception as e:
        logger.error(f"Error adding proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/proxies/")
def get_proxies(db: Session = Depends(get_db)):
    """Get all proxies"""
    try:
        proxies = db.query(Proxy).all()
        return {
            "success": True,
            "proxies": [
                {
                    "id": p.id,
                    "host": p.host,
                    "port": p.port,
                    "username": p.username,
                    "country": p.country,
                    "is_active": p.is_active,
                    "validation_status": p.validation_status
                }
                for p in proxies
            ]
        }
    except Exception as e:
        logger.error(f"Error getting proxies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# BLS Login endpoint
class BLSLoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/enhanced-bls/login")
async def bls_login(login_data: BLSLoginRequest, db: Session = Depends(get_db)):
    """Login to BLS account with automatic captcha solving"""
    try:
        logger.info(f"🔐 Starting BLS login for: {login_data.email}")
        
        # Get proxy for login
        from services.proxy_service import ProxyService
        proxy_service = ProxyService()
        proxy_config = await proxy_service.get_algerian_proxy(db, avoid_recent=True)
        
        proxy_url = None
        if proxy_config:
            if proxy_config.get('username') and proxy_config.get('password'):
                proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}"
            else:
                proxy_url = f"http://{proxy_config['host']}:{proxy_config['port']}"
            logger.info(f"🌐 Using proxy: {proxy_config['host']}:{proxy_config['port']}")
        else:
            logger.warning("⚠️ No proxy available")
        
        # Browser will automatically handle AWS WAF and generate cookies
        import random
        cookies = {
            'visitorId_current': str(random.randint(10000000, 99999999))
        }
        
        # Perform login with browser automation
        from services.bls_modules.browser_login_handler import BrowserLoginHandler
        login_handler = BrowserLoginHandler()
        
        login_result = await login_handler.login_in_browser(
            login_url="https://algeria.blsspainglobal.com/dza/account/Login",
            email=login_data.email,
            password=login_data.password,
            cookies=cookies,
            proxy_url=proxy_url,
            headless=False  # Show browser for debugging
        )
        
        if login_result[0]:
            logger.info("✅ Login successful!")
            return {
                "success": True,
                "message": "Login successful",
                "cookies": login_result[1].get('cookies', {}),
                "email": login_data.email
            }
        else:
            logger.error(f"❌ Login failed: {login_result[1].get('error')}")
            return {
                "success": False,
                "error": login_result[1].get('error'),
                "email": login_data.email
            }
            
    except Exception as e:
        logger.error(f"❌ Error in BLS login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Booking Visa Bot Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

async def run_interactive_mode():
    """Run interactive CLI mode for visa booking"""
    try:
        from services.bls_modules.browser_login_handler import BrowserLoginHandler
        from services.proxy_service import ProxyService
        from models.database import Account
        
        logger.info("="*80)
        logger.info("📋 VISA RESERVATION SYSTEM")
        logger.info("="*80)
        logger.info("")
        
        # Step 1: Ask if user wants to book visa
        print("\n" + "="*80)
        response = input("❓ Do you want to book a Visa now? (yes/no): ").strip().lower()
        print("="*80 + "\n")
        
        if response not in ['yes', 'y']:
            logger.info("👋 Booking cancelled. Exiting interactive mode.")
            logger.info("💡 FastAPI server continues running at http://localhost:8000")
            return
        
        # Step 2: Count available accounts in database
        db = SessionLocal()
        try:
            account_count = db.query(Account).filter(Account.email.isnot(None)).count()
            
            if account_count == 0:
                logger.warning("⚠️ No accounts found in database!")
                logger.info("💡 Please create accounts using the frontend first at http://localhost:3000/create-account")
                return
            
            logger.info(f"✅ Found {account_count} available account(s) in database")
            logger.info("")
            
            # Step 3: Ask how many accounts to use
            print("="*80)
            num_accounts_str = input(f"❓ How many accounts do you want to use? (1-{account_count}): ").strip()
            print("="*80 + "\n")
            
            try:
                num_accounts = int(num_accounts_str)
                if num_accounts < 1 or num_accounts > account_count:
                    logger.error(f"❌ Invalid number. Please enter a number between 1 and {account_count}")
                    return
            except ValueError:
                logger.error("❌ Invalid input. Please enter a valid number.")
                return
            
            logger.info(f"✅ Will use {num_accounts} account(s) for booking")
            logger.info("")
            
            # Step 4: Get accounts from database
            accounts = db.query(Account).filter(Account.email.isnot(None)).limit(num_accounts).all()
            
            logger.info(f"📋 Processing {len(accounts)} account(s)...")
            logger.info("")
            
            # Step 5: Try to login with each account
            proxy_service = ProxyService()
            login_handler = BrowserLoginHandler()
            
            for idx, account in enumerate(accounts, 1):
                logger.info(f"\n{'='*80}")
                logger.info(f"🔐 LOGIN ATTEMPT {idx}/{len(accounts)}")
                logger.info(f"{'='*80}")
                logger.info(f"📧 Email: {account.email}")
                logger.info("")
                
                # Get proxy for this account
                proxy_config = await proxy_service.get_algerian_proxy(db, avoid_recent=True)
                proxy_url = None
                if proxy_config:
                    if proxy_config.get('username') and proxy_config.get('password'):
                        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}"
                    else:
                        proxy_url = f"http://{proxy_config['host']}:{proxy_config['port']}"
                    logger.info(f"🌐 Using proxy: {proxy_config['host']}:{proxy_config['port']}")
                
                # Generate random visitor ID
                import random
                cookies = {
                    'visitorId_current': str(random.randint(10000000, 99999999))
                }
                
                # Try to login (password will be prompted in console)
                try:
                    login_result = await login_handler.login_in_browser(
                        login_url="https://algeria.blsspainglobal.com/dza/account/Login",
                        email=account.email,
                        password="",  # Will prompt in console
                        cookies=cookies,
                        proxy_url=proxy_url,
                        headless=True  # Run in background
                    )
                    
                    if login_result[0]:
                        logger.info(f"✅ Login successful for {account.email}!")
                    else:
                        logger.error(f"❌ Login failed for {account.email}: {login_result[1].get('error')}")
                except Exception as e:
                    logger.error(f"❌ Error during login: {e}")
                
                logger.info("")
            
            logger.info("")
            logger.info("="*80)
            logger.info("✅ LOGIN PHASE COMPLETE")
            logger.info("="*80)
            logger.info("💡 Next: Implement booking functionality")
            logger.info("="*80)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error in interactive mode: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import uvicorn
    from database.config import create_tables
    from init_database import init_database
    
    logger.info("🚀 Starting Booking Visa Bot Backend...")
    
    # Initialize comprehensive database on startup
    try:
        init_database()
        create_tables()
        logger.info("✅ Comprehensive database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise
    
    # Start FastAPI server in background using threading
    logger.info("🌐 Starting FastAPI server...")
    import threading
    import time
    
    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    logger.info("⏳ Waiting for server to start...")
    time.sleep(3)
    logger.info("✅ FastAPI server running at http://localhost:8000")
    logger.info("")
    
    # Run interactive mode
    try:
        import asyncio
        asyncio.run(run_interactive_mode())
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

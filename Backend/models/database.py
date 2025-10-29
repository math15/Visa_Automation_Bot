"""
Database Models for Booking Visa Bot
Modular database models using SQLAlchemy
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

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
    bls_website_url = Column(String(255), default="https://algeria.blsspainglobal.com/")
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

class Account(Base):
    """Base account model for storing account information before BLS creation"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Information (BLS format)
    sur_name = Column(String(100), nullable=True)  # BLS: SurName (Family Name) - optional
    first_name = Column(String(100), nullable=False)  # BLS: FirstName (Given Name) - required
    last_name = Column(String(100), nullable=False)  # BLS: LastName - required
    family_name = Column(String(100), nullable=True)  # Legacy field, kept for compatibility
    date_of_birth = Column(String(10), nullable=False)  # YYYY-MM-DD format
    gender = Column(String(10), default="Male")
    marital_status = Column(String(20), default="Single")
    
    # Passport Information (BLS format)
    passport_number = Column(String(50), nullable=False, unique=True)  # BLS: any format
    passport_type = Column(String(255), default="Ordinary")  # BLS: GUID or name
    passport_type_guid = Column(String(255), nullable=True)  # BLS: PassportType GUID
    passport_issue_date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    passport_expiry_date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    passport_issue_place = Column(String(100), nullable=False)  # BLS: IssuePlace - required!
    passport_issue_country = Column(String(255), nullable=True)  # BLS: BirthCountry (name)
    passport_issue_country_guid = Column(String(255), nullable=True)  # BLS: BirthCountry GUID
    
    # Contact Information
    email = Column(String(255), nullable=False, unique=True)
    mobile = Column(String(20), nullable=False)
    phone_country_code = Column(String(10), default="+213")
    country_code = Column(String(10), default="+213")  # BLS: CountryCode field
    
    # Location Information (BLS format)
    birth_country = Column(String(255), nullable=True)  # BLS: BirthCountry (name)
    birth_country_guid = Column(String(255), nullable=True)  # BLS: BirthCountry GUID
    country_of_residence = Column(String(255), nullable=True)  # BLS: CountryOfResidence (name)
    country_of_residence_guid = Column(String(255), nullable=True)  # BLS: CountryOfResidence GUID
    
    # Additional Information
    number_of_members = Column(Integer, default=1)
    relationship = Column(String(20), default="Self")
    primary_applicant = Column(Boolean, default=True)
    
    # Account Credentials
    password = Column(String(255), nullable=False)
    
    # Account Status
    status = Column(String(20), default="created")  # created, bls_creating, bls_created, bls_failed, inactive
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # BLS Account Status
    bls_status = Column(String(20), default="not_created")  # not_created, creating, created, failed
    bls_username = Column(String(255), nullable=True)
    bls_password = Column(String(255), nullable=True)
    bls_created_at = Column(DateTime, nullable=True)
    bls_error_message = Column(Text, nullable=True)
    
    # Processing Information
    proxy_id = Column(Integer, nullable=True)
    processing_attempts = Column(Integer, default=0)
    last_processing_attempt = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)

class BLSAccount(Base):
    """Legacy BLS account model - keeping for backward compatibility"""
    __tablename__ = "bls_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    family_name = Column(String(100), nullable=True)
    date_of_birth = Column(String(10), nullable=False)  # YYYY-MM-DD format
    gender = Column(String(10), default="Male")
    marital_status = Column(String(20), default="Single")
    
    # Passport Information
    passport_number = Column(String(50), nullable=False, unique=True)
    passport_type = Column(String(20), default="Ordinary")
    passport_issue_date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    passport_expiry_date = Column(String(10), nullable=False)  # YYYY-MM-DD format
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

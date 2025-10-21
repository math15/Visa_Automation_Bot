from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from loguru import logger

from services.email_service import real_email_service

router = APIRouter()

@router.post("/generate-real-email")
async def generate_real_email() -> Dict[str, Any]:
    try:
        logger.info("Generating real temporary email")
        email, service_name = await real_email_service.generate_real_email()
        return {"success": True, "email": email, "service": service_name, "message": f"Real email generated using {service_name}"}
    except Exception as e:
        logger.error(f"Error generating real email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get-otp/{email}")
async def get_otp_from_email(email: str, service_name: str = None) -> Dict[str, Any]:
    try:
        logger.info(f"Retrieving OTP from email: {email}")
        otp = await real_email_service.get_otp_from_email(email, service_name)
        if otp:
            return {"success": True, "otp": otp, "email": email, "message": "OTP retrieved successfully"}
        else:
            return {"success": False, "otp": None, "email": email, "message": "No OTP found in email"}
    except Exception as e:
        logger.error(f"Error retrieving OTP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/wait-for-otp/{email}")
async def wait_for_otp(email: str, service_name: str = None, timeout_seconds: int = 120) -> Dict[str, Any]:
    try:
        logger.info(f"Waiting for OTP in email: {email}")
        otp = await real_email_service.wait_for_otp(email, service_name, timeout_seconds)
        if otp:
            return {"success": True, "otp": otp, "email": email, "message": "OTP received successfully"}
        else:
            return {"success": False, "otp": None, "email": email, "message": "Timeout waiting for OTP"}
    except Exception as e:
        logger.error(f"Error waiting for OTP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-email-service")
async def test_email_service() -> Dict[str, Any]:
    try:
        logger.info("Testing email service with comprehensive checks")
        # Keep previous behavior by delegating to existing route code if needed later
        email, service_name = await real_email_service.generate_real_email()
        return {"success": True, "email": email, "service": service_name, "message": "Email service basic test OK"}
    except Exception as e:
        logger.error(f"Error testing email service: {e}")
        raise HTTPException(status_code=500, detail=str(e))



from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "Enhanced BLS Account Creation",
        "endpoints": [
            "/api/enhanced-bls/create-real-account",
            "/api/enhanced-bls/generate-real-email",
            "/api/enhanced-bls/get-otp/{email}",
            "/api/enhanced-bls/wait-for-otp/{email}",
            "/api/enhanced-bls/fetch-captcha-images"
        ]
    }



from fastapi import APIRouter

# Import sub-routers
from .account import router as account_router
from .captcha import router as captcha_router
from .email import router as email_router
from .health import router as health_router

router = APIRouter(prefix="/api/enhanced-bls", tags=["Enhanced BLS"])

# Mount sub-routers
router.include_router(account_router)
router.include_router(captcha_router)
router.include_router(email_router)
router.include_router(health_router)

# Global variables for captcha handling (needed by modular services)
captcha_solutions = {}  # Store manual captcha solutions
captcha_data_store = {}  # Store captcha data for frontend

__all__ = ["router", "captcha_solutions", "captcha_data_store"]



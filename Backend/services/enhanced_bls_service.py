"""
Enhanced BLS Account Creation Service
Real BLS website account creation with captcha solving and OTP verification
Now using modular components for better maintainability
"""

# Import the modular service
from .bls_modules import enhanced_bls_service

# Re-export for backward compatibility
EnhancedBLSAccountService = enhanced_bls_service.__class__
"""
BLS Account Creation Module - Main orchestrator for automated BLS account creation
"""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from sqlalchemy.orm import Session

from .waf_bypass import WAFBypassHandler
from .form_handler import FormHandler
from .captcha_handler import CaptchaHandler
from .captcha_submitter import CaptchaSubmitter
from ..proxy_service import proxy_service


class BLSAccountCreator:
    """Main orchestrator for BLS account creation with modular components"""
    
    def __init__(self, visitor_id: str = None):
        """Initialize the BLS account creator with modular components"""
        self.visitor_id = visitor_id or "22615162"  # Default visitor ID
        self.base_url = "https://algeria.blsspainglobal.com"
        self.register_url = "/dza/account/RegisterUser"
        
        # Initialize modular components
        self.waf_handler = WAFBypassHandler(self.base_url, self.register_url, self.visitor_id)
        self.form_handler = FormHandler()
        self.captcha_handler = CaptchaHandler(self.base_url, self.register_url, self.visitor_id)
        self.captcha_submitter = CaptchaSubmitter()
        
        logger.info(f"🚀 BLS Account Creator initialized with visitor ID: {self.visitor_id}")
    
    async def create_account(self, account_data: Dict[str, Any], db: Session = None) -> 'BLSAccountCreationResult':
        """Create a real BLS account with full automation using modular components"""
        # Import locally to avoid circular imports
        from main import BLSAccountCreationResult
        
        try:
            logger.info(f"Starting real BLS account creation for: {account_data.email}")
            
            # Step 1: Use the provided email
            real_email = account_data.email
            logger.info(f"Using provided email: {real_email}")
            
            # Step 2: Navigate to registration page using WAF bypass
            registration_result = await self._get_registration_page(db)
            if not registration_result:
                return BLSAccountCreationResult(
                    success=False,
                    status="error",
                    error_message="Failed to get registration page"
                )
            
            registration_page = registration_result["content"]
            proxy_url = registration_result.get("proxy_url")
            headers = registration_result.get("headers")
            aws_waf_token = registration_result.get("aws_waf_token")
            session_cookies = registration_result.get("session_cookies", {})
            
            # Debug: Save content to file for inspection
            with open("debug_registration_page.html", "w", encoding="utf-8") as f:
                f.write(str(registration_page))
            logger.info("💾 Saved registration page to debug_registration_page.html")
            
            # Step 3: Extract form data using form handler
            form_data = await self.form_handler.extract_form_data(registration_page)
            
            # Step 4: Extract captcha info using captcha handler
            captcha_info = self.captcha_handler.extract_captcha_info(registration_page)
            logger.info(f"🔍 Captcha info extracted: {captcha_info}")
            
            # Step 5: Solve captcha if present
            captcha_solution = None
            if captcha_info:
                logger.info(f"🎯 Captcha detected: {captcha_info['type']}")
                captcha_solution = await self.captcha_handler.solve_captcha(
                    captcha_info, form_data, proxy_url, registration_page, session_cookies
                )
                logger.info(f"🔍 Captcha solution result: {captcha_solution}")
                
                if captcha_solution == "MANUAL_CAPTCHA_REQUIRED":
                    logger.info("⏳ Manual captcha solving required...")
                    captcha_id = captcha_info.get("captcha_id")
                    captcha_data_param = self.captcha_handler._extract_captcha_data_param(registration_page)
                    logger.info(f"🔑 Returning captcha_required with captcha_id: {captcha_id}")
                    logger.info(f"🔑 Captcha data parameter: {captcha_data_param}")
                    
                    result = BLSAccountCreationResult(
                        success=True,
                        status="captcha_required",
                        captcha_id=captcha_id,
                        captcha_data_param=captcha_data_param,
                        message="Manual captcha solving required"
                    )
                    logger.info(f"🔑 Returning result: {result}")
                    return result
                
                if not captcha_solution:
                    return BLSAccountCreationResult(
                        success=False,
                        status="error",
                        error_message="Failed to solve captcha"
                    )
            else:
                logger.info("ℹ️ No captcha detected, proceeding with form submission")
            
            # Step 6: Submit form with captcha solution
            submission_result = await self.form_handler.submit_form(
                registration_page, form_data, captcha_solution, proxy_url, aws_waf_token
            )
            
            if not submission_result:
                return BLSAccountCreationResult(
                    success=False,
                    status="error",
                    error_message="Failed to submit form"
                )
            
            logger.info(f"BLS account created successfully: {real_email}")
            return BLSAccountCreationResult(
                success=True,
                status="completed",
                account_id=registration_result.get("account_id")
            )
            
        except Exception as e:
            logger.error(f"Error creating BLS account: {e}")
            return BLSAccountCreationResult(
                success=False,
                status="error",
                error_message=str(e)
            )
    
    async def _get_registration_page(self, db: Session = None) -> Optional[Dict[str, Any]]:
        """Get BLS registration page using WAF bypass handler"""
        try:
            # Get proxy (Algeria or Spain)
            proxy_url = None
            proxy_config = None
            if db:
                proxy_config = await proxy_service.get_algerian_proxy(db)
                if proxy_config:
                    proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}"
                    logger.info(f"Using {proxy_config['country']} proxy: {proxy_config['host']}:{proxy_config['port']}")
                else:
                    logger.warning("No proxy available, trying direct connection")
            
            # Use WAF bypass handler to get registration page
            logger.info("🔄 Attempting to get BLS registration page with WAF bypass...")
            
            # Prepare headers for the request
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'es-ES,es;q=0.9',
                'cache-control': 'max-age=0',
                'priority': 'u=0, i',
                'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            }
            
            bypass_result = await self.waf_handler.try_comprehensive_bypass(proxy_url, headers)
            
            if bypass_result and bypass_result.get('success'):
                logger.info("✅ Successfully retrieved BLS registration page!")
                return {
                    "content": bypass_result.get('content', ''),
                    "proxy_url": proxy_url,
                    "headers": bypass_result.get('headers', {}),
                    "aws_waf_token": bypass_result.get('waf_token'),
                    "session_cookies": bypass_result.get('cookies', {}),
                    "account_id": None  # Will be set after successful form submission
                }
            else:
                logger.error("❌ Failed to retrieve BLS registration page")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting registration page: {e}")
            return None
    
    async def submit_captcha_solution(self, captcha_id: str, captcha_solution: str, 
                                    captcha_data_param: str, proxy_url: str = None) -> 'BLSAccountCreationResult':
        """Submit captcha solution and complete account creation"""
        # Import locally to avoid circular imports
        from main import BLSAccountCreationResult
        
        try:
            logger.info(f"🎯 Submitting captcha solution for captcha ID: {captcha_id}")
            
            # Use captcha submitter to submit the solution
            submission_result = await self.captcha_submitter.submit_captcha_solution(
                captcha_id, captcha_solution, captcha_data_param, proxy_url
            )
            
            if submission_result and submission_result.get('success'):
                logger.info("✅ Captcha solution submitted successfully!")
                return BLSAccountCreationResult(
                    success=True,
                    status="completed",
                    account_id=submission_result.get('account_id'),
                    message="Account created successfully"
                )
            else:
                logger.error("❌ Failed to submit captcha solution")
                return BLSAccountCreationResult(
                    success=False,
                    status="error",
                    error_message="Failed to submit captcha solution"
                )
                
        except Exception as e:
            logger.error(f"❌ Error submitting captcha solution: {e}")
            return BLSAccountCreationResult(
                success=False,
                status="error",
                error_message=str(e)
            )


# Create a global instance for backward compatibility
enhanced_bls_service = BLSAccountCreator()

# Add alias method for backward compatibility
enhanced_bls_service.create_real_bls_account = enhanced_bls_service.create_account
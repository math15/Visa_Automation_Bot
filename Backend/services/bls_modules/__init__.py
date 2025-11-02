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
from .browser_registration_handler import BrowserRegistrationHandler
from ..proxy_service import proxy_service


class BLSAccountCreator:
    """Main orchestrator for BLS account creation with modular components"""
    
    def __init__(self, visitor_id: str = None):
        """Initialize the BLS account creator with modular components"""
        # Generate random visitor ID (8 digits) if not provided
        # This ensures each account creation uses a different session ID
        import random
        self.visitor_id = visitor_id or str(random.randint(10000000, 99999999))
        self.base_url = "https://algeria.blsspainglobal.com"
        self.register_url = "/dza/account/RegisterUser"
        
        # Initialize modular components
        self.waf_handler = WAFBypassHandler(self.base_url, self.register_url, self.visitor_id)
        self.form_handler = FormHandler()
        self.captcha_handler = CaptchaHandler(self.base_url, self.register_url, self.visitor_id)
        self.captcha_submitter = CaptchaSubmitter()
        self.browser_registration_handler = BrowserRegistrationHandler()
        
        logger.info(f"🚀 BLS Account Creator initialized with visitor ID: {self.visitor_id}")
    
    async def create_account_with_browser(self, account_data: Dict[str, Any], db: Session = None, use_browser_flow: bool = True) -> 'BLSAccountCreationResult':
        """
        Create BLS account using full browser flow (RECOMMENDED - bypasses all WAF issues)
        
        This method:
        1. Opens registration page in browser
        2. Auto-fills all form fields
        3. User solves captcha manually
        4. Clicks Send OTP button in browser
        5. Retrieves OTP from email
        6. Auto-fills OTP and submits
        7. Returns success/failure
        """
        from main import BLSAccountCreationResult
        
        try:
            logger.info(f"🌐 Starting browser-based BLS account creation for: {account_data.email}")
            
            # Step 1: Get proxy for browser (REQUIRED to avoid CloudFront 403!)
            logger.info("📄 Step 1: Getting proxy for browser...")
            proxy_url = None
            try:
                from services.proxy_service import ProxyService
                proxy_service = ProxyService()
                proxy_config = await proxy_service.get_algerian_proxy(db)
                if proxy_config:
                    # Format proxy URL
                    if proxy_config.get('username') and proxy_config.get('password'):
                        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}"
                        logger.info(f"🌐 Using proxy: {proxy_config['host']}:{proxy_config['port']} (with auth)")
                        logger.info(f"🔑 Proxy credentials: username={proxy_config['username'][:10]}...")
                    else:
                        proxy_url = f"http://{proxy_config['host']}:{proxy_config['port']}"
                        logger.warning(f"⚠️ Using proxy WITHOUT authentication: {proxy_config['host']}:{proxy_config['port']}")
                        logger.warning(f"⚠️ This will likely fail! Proxy config: {proxy_config}")
                else:
                    logger.error("❌ No proxy available - CloudFront will block direct connections!")
                    return BLSAccountCreationResult(
                        success=False,
                        status="error",
                        error_message="No proxy available - direct connection blocked by CloudFront"
                    )
            except Exception as e:
                logger.error(f"❌ Failed to get proxy: {e}")
                return BLSAccountCreationResult(
                    success=False,
                    status="error",
                    error_message=f"Failed to get proxy: {e}"
                )
            
            # Step 2: Prepare minimal cookies (browser will generate the rest)
            logger.info("📝 Step 2: Preparing minimal cookies...")
            session_cookies = {}
            
            # Add visitorId_current (REQUIRED by BLS!)
            session_cookies['visitorId_current'] = self.visitor_id
            logger.info(f"🆔 Added visitorId_current to cookies for browser: {self.visitor_id}")
            
            # Step 3: Initialize email service and generate real temporary email if needed
            logger.info("📧 Step 3: Initializing email service...")
            from services.email_service import RealEmailService
            email_service = RealEmailService()
            
            # Check if account email is a placeholder (@example.com) and generate real temp email
            actual_email = account_data.email
            email_service_name = None
            
            if '@example.com' in account_data.email or not account_data.email:
                logger.info("⚠️ Detected placeholder email (@example.com), generating REAL temporary email...")
                try:
                    actual_email, email_service_name = await email_service.generate_real_email()
                    logger.info(f"✅ Generated real temporary email: {actual_email} (service: {email_service_name})")
                    logger.info(f"🌐 You can check inbox at:")
                    if '1secmail' in actual_email:
                        username, domain = actual_email.split('@')
                        logger.info(f"   https://www.1secmail.com/?login={username}&domain={domain}")
                    elif 'guerrillamail' in actual_email:
                        logger.info(f"   https://www.guerrillamail.com/inbox")
                    elif 'tempmail' in actual_email:
                        logger.info(f"   https://temp-mail.org/en/")
                except Exception as e:
                    logger.error(f"❌ Failed to generate temporary email: {e}")
                    logger.warning("⚠️ Using original email, manual OTP entry will be required")
                    actual_email = account_data.email
            else:
                logger.info(f"✅ Using provided email: {actual_email}")
            
            # Step 4: Prepare user data for browser form
            logger.info("📝 Step 4: Preparing user data...")
            user_data = {
                'SurName': account_data.family_name or '',
                'FirstName': account_data.first_name,
                'LastName': account_data.last_name,
                'DateOfBirth': account_data.date_of_birth.strftime('%Y-%m-%dT%H:%M') if hasattr(account_data.date_of_birth, 'strftime') else str(account_data.date_of_birth),
                'PassportNumber': account_data.passport_number,
                'PassportIssueDate': account_data.passport_issue_date.strftime('%Y-%m-%dT%H:%M') if hasattr(account_data.passport_issue_date, 'strftime') else str(account_data.passport_issue_date),
                'PassportExpiryDate': account_data.passport_expiry_date.strftime('%Y-%m-%dT%H:%M') if hasattr(account_data.passport_expiry_date, 'strftime') else str(account_data.passport_expiry_date),
                'BirthCountry': account_data.birth_country or 'Algeria',
                'PassportType': account_data.passport_type or 'Ordinary',
                'IssuePlace': account_data.passport_issue_place,
                'CountryOfResidence': account_data.country_of_residence or 'Algeria',
                'Mobile': account_data.mobile,
                'Email': actual_email  # Use real temporary email
            }
            
            # Step 5: Complete registration in browser
            logger.info("🌐 Step 5: Starting browser registration flow...")
            registration_url = f"{self.base_url}{self.register_url}"
            
            success, result = await self.browser_registration_handler.complete_registration_in_browser(
                registration_url=registration_url,
                user_data=user_data,
                cookies=session_cookies,
                proxy_url=proxy_url,
                headless=False,  # Show browser window
                email_service=email_service,
                email_service_name=email_service_name  # Pass service name for OTP retrieval
            )
            
            if success:
                logger.info(f"🎉 BLS account created successfully: {account_data.email}")
                return BLSAccountCreationResult(
                    success=True,
                    status="completed",
                    account_id=account_data.email,
                    message="BLS account created successfully using browser flow"
                )
            else:
                logger.error(f"❌ Browser registration failed: {result.get('error')}")
                return BLSAccountCreationResult(
                    success=False,
                    status="error",
                    error_message=f"Browser registration failed: {result.get('error')}"
                )
                
        except Exception as e:
            logger.error(f"❌ Error in browser-based account creation: {e}")
            return BLSAccountCreationResult(
                success=False,
                status="error",
                error_message=str(e)
            )
    
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
                # Use browser-based solving (RECOMMENDED - bypasses all detection)
                captcha_solution = await self.captcha_handler.solve_captcha(
                    captcha_info=captcha_info,
                    form_data=form_data,
                    proxy_url=proxy_url,
                    registration_page=registration_page,
                    session_cookies=session_cookies,
                    use_browser=True,    # Use browser-based solving (REQUIRED!)
                    headless=False,      # Show browser window for debugging/manual solving
                    manual_mode=True     # Manual solving - user clicks images and submits
                )
                logger.info(f"🔍 Captcha solution result: {captcha_solution}")
                
                # Handle dictionary response (new format with captcha_token)
                if isinstance(captcha_solution, dict):
                    if captcha_solution.get("success") and captcha_solution.get("status") == "CAPTCHA_SOLVED":
                        logger.info("✅ Browser-based captcha solved successfully!")
                        captcha_token = captcha_solution.get('captcha_token')
                        captcha_id_from_solution = captcha_solution.get('captcha_id')
                        logger.info(f"🔑 Captcha token: {captcha_token[:50] if captcha_token else 'N/A'}...")
                        logger.info(f"🔑 Captcha ID: {captcha_id_from_solution[:50] if captcha_id_from_solution else 'N/A'}...")
                        
                        # Step 6: Send OTP request with captcha tokens
                        logger.info("📧 Step 6: Sending OTP request to user's email...")
                        from .otp_handler import OTPHandler
                        otp_handler = OTPHandler()
                        
                        # Prepare user data for OTP request (from account_data)
                        otp_form_data = {
                            'SurName': account_data.family_name or '',
                            'FirstName': account_data.first_name,
                            'LastName': account_data.last_name,
                            'DateOfBirth': account_data.date_of_birth.strftime('%Y-%m-%d') if hasattr(account_data.date_of_birth, 'strftime') else str(account_data.date_of_birth),
                            'PassportNumber': account_data.passport_number,
                            'PassportIssueDate': account_data.passport_issue_date.strftime('%Y-%m-%d') if hasattr(account_data.passport_issue_date, 'strftime') else str(account_data.passport_issue_date),
                            'PassportExpiryDate': account_data.passport_expiry_date.strftime('%Y-%m-%d') if hasattr(account_data.passport_expiry_date, 'strftime') else str(account_data.passport_expiry_date),
                            'BirthCountry': account_data.birth_country or '',
                            'PassportType': account_data.passport_type or '',
                            'IssuePlace': account_data.passport_issue_place or '',
                            'CountryOfResidence': account_data.country_of_residence or '',
                            'CountryCode': account_data.phone_country_code or '+213',
                            'Mobile': account_data.mobile,
                            'Email': real_email,
                            'SecurityCode': form_data.get('SecurityCode', ''),
                        }
                        
                        # Get antiforgery token
                        antiforgery_token = form_data.get('__RequestVerificationToken', '')
                        
                        # Prepare cookies with AWS WAF token
                        otp_cookies = session_cookies.copy() if session_cookies else {}
                        if aws_waf_token and 'aws-waf-token' not in otp_cookies:
                            otp_cookies['aws-waf-token'] = aws_waf_token
                            logger.info(f"🔑 Added AWS WAF token to OTP request cookies: {aws_waf_token[:50]}...")
                        
                        # Send OTP request
                        otp_result = await otp_handler.send_otp_request(
                            form_data=otp_form_data,
                            captcha_token=captcha_token,
                            captcha_id=captcha_id_from_solution,
                            antiforgery_token=antiforgery_token,
                            session_cookies=otp_cookies,
                            proxy_url=proxy_url
                        )
                        
                        if not otp_result.get('success'):
                            logger.error(f"❌ Failed to send OTP: {otp_result.get('error')}")
                            return BLSAccountCreationResult(
                                success=False,
                                status="error",
                                error_message=f"Failed to send OTP: {otp_result.get('error')}"
                            )
                        
                        logger.info(f"✅ OTP sent successfully to {real_email}")
                        logger.info(f"🔐 Encrypted Email: {otp_result.get('encryptEmail', 'N/A')[:50]}...")
                        logger.info(f"🔐 Encrypted Mobile: {otp_result.get('encryptMobile', 'N/A')[:50]}...")
                        logger.info(f"🔐 Security Code: {otp_result.get('securityCode', 'N/A')[:50]}...")
                        
                        # Step 7: Wait for OTP from email
                        logger.info("📧 Step 7: Waiting for OTP from email...")
                        from services.email_service import RealEmailService
                        email_service = RealEmailService()
                        
                        # Wait for OTP (60 seconds timeout)
                        otp_code = await email_service.wait_for_otp(real_email, timeout=60)
                        
                        if not otp_code:
                            logger.error("❌ Failed to retrieve OTP from email")
                            return BLSAccountCreationResult(
                                success=False,
                                status="error",
                                error_message="Failed to retrieve OTP from email"
                            )
                        
                        logger.info(f"✅ OTP retrieved: {otp_code}")
                        
                        # Step 8: Final registration with OTP
                        logger.info("📝 Step 8: Submitting final registration with OTP...")
                        from .registration_submitter import RegistrationSubmitter
                        registration_submitter = RegistrationSubmitter()
                        
                        # Prepare cookies with AWS WAF token for final submission
                        final_cookies = otp_cookies.copy()  # Use the same cookies as OTP request
                        
                        final_result = await registration_submitter.submit_final_registration(
                            form_data=otp_form_data,
                            captcha_token=captcha_token,
                            captcha_id=captcha_id_from_solution,
                            otp_code=otp_code,
                            encrypted_email=otp_result.get('encryptEmail', ''),
                            encrypted_mobile=otp_result.get('encryptMobile', ''),
                            security_code=otp_result.get('securityCode', ''),
                            antiforgery_token=antiforgery_token,
                            session_cookies=final_cookies,
                            proxy_url=proxy_url
                        )
                        
                        if not final_result.get('success'):
                            logger.error(f"❌ Final registration failed: {final_result.get('error')}")
                            return BLSAccountCreationResult(
                                success=False,
                                status="error",
                                error_message=f"Final registration failed: {final_result.get('error')}"
                            )
                        
                        logger.info(f"🎉 BLS account created successfully: {real_email}")
                        
                        return BLSAccountCreationResult(
                            success=True,
                            status="completed",
                            account_id=real_email,
                            message="BLS account created successfully"
                        )
                        
                    elif not captcha_solution.get("success"):
                        logger.warning("⏳ Browser-based captcha solving failed - manual required")
                        captcha_id = captcha_info.get("captcha_id")
                        captcha_data_param = self.captcha_handler._extract_captcha_data_param(registration_page)
                        
                        result = BLSAccountCreationResult(
                            success=True,
                            status="captcha_required",
                            captcha_id=captcha_id,
                            captcha_data_param=captcha_data_param,
                            message="Manual captcha solving required"
                        )
                        return result
                # Handle old string response format
                elif captcha_solution == "MANUAL_CAPTCHA_REQUIRED":
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
                elif not captcha_solution:
                    return BLSAccountCreationResult(
                        success=False,
                        status="error",
                        error_message="Failed to solve captcha"
                    )
            else:
                logger.info("ℹ️ No captcha detected, proceeding with registration")
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
                                    captcha_data_param: str, proxy_url: str = None, 
                                    session_cookies: Dict[str, str] = None) -> 'BLSAccountCreationResult':
        """Submit captcha solution and complete account creation"""
        # Import locally to avoid circular imports
        from main import BLSAccountCreationResult
        
        try:
            logger.info(f"🎯 Submitting captcha solution for captcha ID: {captcha_id}")
            
            # CRITICAL: Use session cookies from registration page for consistency
            if session_cookies:
                logger.info(f"🍪 Using session cookies from registration page: {list(session_cookies.keys())}")
            else:
                logger.warning("⚠️ No session cookies provided - session may be inconsistent")
            
            # Use captcha submitter to submit the solution with session cookies
            submission_result = await self.captcha_submitter.submit_captcha_solution(
                captcha_id, captcha_solution, captcha_data_param, None, session_cookies, proxy_url
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
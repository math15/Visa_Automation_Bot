"""
Registration Flow Module for BLS Account Creation
Handles the 3-step registration process
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from loguru import logger

from main import BLSAccountCreate


class RegistrationFlowHandler:
    """Handles the 3-step BLS registration flow"""
    
    def __init__(self, base_url: str, register_url: str, visitor_id: str):
        self.base_url = base_url
        self.register_url = register_url
        self.visitor_id = visitor_id
    
    async def submit_registration_form(self, account_data: BLSAccountCreate, email: str, 
                                      form_data: Dict[str, Any], captcha_solution: str = None, 
                                      proxy_url: str = None, headers: dict = None, 
                                      aws_waf_token: str = None) -> Dict[str, Any]:
        """Submit registration form using proper BLS 3-step flow"""
        try:
            logger.info("📝 Starting BLS 3-step registration flow...")
            
            # Step 1: Submit form for captcha verification
            captcha_result = await self._step1_captcha_verification(
                account_data, email, form_data, proxy_url, aws_waf_token
            )
            if not captcha_result["success"]:
                return captcha_result
            
            # Step 2: Solve captcha and submit OTP request
            otp_result = await self._step2_otp_generation(
                account_data, email, form_data, captcha_solution, proxy_url, aws_waf_token
            )
            if not otp_result["success"]:
                return otp_result
            
            # Step 3: Submit OTP and complete registration
            final_result = await self._step3_final_submission(
                account_data, email, form_data, otp_result.get("otp"), proxy_url, aws_waf_token
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Error in 3-step registration flow: {e}")
            return {
                "success": False,
                "error": f"Registration flow error: {str(e)}"
            }
    
    async def _step1_captcha_verification(self, account_data: BLSAccountCreate, email: str, 
                                       form_data: Dict[str, Any], proxy_url: str, 
                                       aws_waf_token: str = None) -> Dict[str, Any]:
        """Step 1: Submit form for captcha verification"""
        try:
            logger.info("🔄 Step 1: Submitting form to trigger captcha verification...")
            
            # Prepare complete form data to trigger captcha
            captcha_data = {
                "FirstName": account_data.first_name,
                "LastName": account_data.last_name,
                "SurName": account_data.last_name,
                "DateOfBirth": account_data.date_of_birth,
                "PassportNumber": account_data.passport_number,
                "PassportIssueDate": account_data.passport_issue_date,
                "PassportExpiryDate": account_data.passport_expiry_date,
                "BirthCountry": account_data.birth_country or "DZ",
                "PassportType": account_data.passport_type or "",
                "IssuePlace": account_data.passport_issue_place or "",
                "CountryOfResidence": account_data.country_of_residence or "DZ",
                "CountryCode": "+213",
                "Mobile": account_data.mobile,
                "Email": email,
                "__RequestVerificationToken": form_data.get("__RequestVerificationToken"),
                "Mode": "Register",
                "CaptchaId": form_data.get("CaptchaId", ""),
                "CaptchaParam": "",
                "CaptchaData": ""
            }
            
            # Submit to captcha verification endpoint
            captcha_endpoint = "/dza/account/VerifyCaptcha"
            result = await self._make_bls_request(
                captcha_endpoint, captcha_data, proxy_url, aws_waf_token
            )
            
            if result["success"]:
                logger.info("✅ Step 1: Captcha verification submitted successfully")
            else:
                logger.error(f"❌ Step 1: Captcha verification failed: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in Step 1: {e}")
            return {"success": False, "error": str(e)}
    
    async def _step2_otp_generation(self, account_data: BLSAccountCreate, email: str, 
                                  form_data: Dict[str, Any], captcha_solution: str, 
                                  proxy_url: str, aws_waf_token: str = None) -> Dict[str, Any]:
        """Step 2: Submit captcha solution and generate OTP"""
        try:
            logger.info("🔄 Step 2: Submitting captcha solution and generating OTP...")
            
            # Prepare OTP generation data
            otp_data = {
                "Email": email,
                "CaptchaSolution": captcha_solution,
                "__RequestVerificationToken": form_data.get("__RequestVerificationToken"),
                "Mode": "GenerateOTP"
            }
            
            # Submit to OTP generation endpoint
            otp_endpoint = "/dza/account/SendRegisterUserVerificationCode"
            result = await self._make_bls_request(
                otp_endpoint, otp_data, proxy_url, aws_waf_token
            )
            
            if result["success"]:
                logger.info("✅ Step 2: OTP generation request submitted successfully")
                # Wait for OTP in email
                otp = await self._wait_for_otp(email)
                if otp:
                    result["otp"] = otp
                    logger.info(f"✅ Step 2: OTP received: {otp}")
                else:
                    result["success"] = False
                    result["error"] = "Failed to receive OTP from email"
            else:
                logger.error(f"❌ Step 2: OTP generation failed: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in Step 2: {e}")
            return {"success": False, "error": str(e)}
    
    async def _step3_final_submission(self, account_data: BLSAccountCreate, email: str, 
                                   form_data: Dict[str, Any], otp: str, 
                                   proxy_url: str, aws_waf_token: str = None) -> Dict[str, Any]:
        """Step 3: Submit complete registration with OTP"""
        try:
            logger.info("🔄 Step 3: Submitting complete registration with OTP...")
            
            # Prepare complete registration data
            registration_data = {
                "FirstName": account_data.first_name,
                "LastName": account_data.last_name,
                "FamilyName": account_data.family_name or "",
                "DateOfBirth": account_data.date_of_birth,
                "Gender": account_data.gender,
                "MaritalStatus": account_data.marital_status,
                "PassportNumber": account_data.passport_number,
                "PassportType": account_data.passport_type,
                "PassportIssueDate": account_data.passport_issue_date,
                "PassportExpiryDate": account_data.passport_expiry_date,
                "PassportIssuePlace": account_data.passport_issue_place or "",
                "PassportIssueCountry": account_data.passport_issue_country or "",
                "Email": email,
                "EmailOtp": otp,
                "Mobile": account_data.mobile,
                "PhoneCountryCode": account_data.phone_country_code or "+213",
                "BirthCountry": account_data.birth_country or "DZ",
                "CountryOfResidence": account_data.country_of_residence or "DZ",
                "NumberOfMembers": account_data.number_of_members or 1,
                "Relationship": account_data.relationship or "Self",
                "PrimaryApplicant": account_data.primary_applicant or True,
                "OTP": otp,
                "__RequestVerificationToken": form_data.get("__RequestVerificationToken"),
                "Mode": "Register"
            }
            
            # Submit to final registration endpoint
            result = await self._make_bls_request(
                self.register_url, registration_data, proxy_url, aws_waf_token
            )
            
            if result["success"]:
                logger.info("✅ Step 3: Registration completed successfully!")
            else:
                logger.error(f"❌ Step 3: Final registration failed: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in Step 3: {e}")
            return {"success": False, "error": str(e)}
    
    async def _make_bls_request(self, endpoint: str, data: Dict[str, Any], 
                              proxy_url: str, aws_waf_token: str = None) -> Dict[str, Any]:
        """Make a request to BLS endpoint"""
        try:
            # Prepare headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://algeria.blsspainglobal.com",
                "Referer": f"https://algeria.blsspainglobal.com{self.register_url}",
                "Upgrade-Insecure-Requests": "1"
            }
            
            # Add AWS WAF token if available
            if aws_waf_token:
                headers["Cookie"] = f"aws-waf-token={aws_waf_token}"
            
            logger.info(f"📡 Making request to: {self.base_url}{endpoint}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}{endpoint}",
                    data=data,
                    headers=headers,
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    content = await response.text()
                    
                    logger.info(f"📡 Response: {response.status}, Content length: {len(content)}")
                    
                    if response.status in [200, 202]:
                        return {"success": True, "content": content, "status_code": response.status}
                    else:
                        return {
                            "success": False, 
                            "error": f"HTTP {response.status}", 
                            "content": content,
                            "status_code": response.status
                        }
                        
        except Exception as e:
            logger.error(f"❌ Request error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _wait_for_otp(self, email: str, timeout: int = 60) -> Optional[str]:
        """Wait for OTP in email"""
        try:
            logger.info(f"📧 Waiting for OTP in email: {email}")
            
            # For Gmail accounts, check for manually submitted OTP
            if email.endswith("@gmail.com"):
                logger.info("📧 Gmail detected - checking for manually submitted OTP")
                
                # Initialize pending OTPs if not exists
                if not hasattr(self, 'pending_otps'):
                    self.pending_otps = {}
                
                # Wait for manual OTP submission
                start_time = asyncio.get_event_loop().time()
                
                while (asyncio.get_event_loop().time() - start_time) < timeout:
                    if email in self.pending_otps:
                        otp = self.pending_otps.pop(email)
                        logger.info(f"✅ Manual OTP received for {email}: {otp}")
                        return otp
                    
                    await asyncio.sleep(2)
                
                logger.warning(f"⏰ Timeout waiting for manual OTP for {email}")
                return None
            
            # Use our email service for temporary emails
            from ..email_service import real_email_service
            
            otp = await real_email_service.wait_for_otp(email, timeout)
            return otp
            
        except Exception as e:
            logger.error(f"❌ Error waiting for OTP: {e}")
            return None

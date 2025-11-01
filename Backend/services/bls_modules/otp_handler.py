"""
OTP Handler for BLS Account Registration
Handles sending OTP request and verification
"""

from typing import Dict, Any, Optional
from loguru import logger
import urllib.parse


class OTPHandler:
    """Handles OTP sending and verification for BLS registration"""
    
    def __init__(self):
        self.otp_endpoint = "https://algeria.blsspainglobal.com/dza/account/SendRegisterUserVerificationCode"
    
    async def send_otp_request(
        self,
        form_data: Dict[str, Any],
        captcha_token: str,
        captcha_id: str,
        antiforgery_token: str,
        session_cookies: Dict[str, str],
        proxy_url: str = None
    ) -> Dict[str, Any]:
        """
        Send OTP request to BLS
        
        Args:
            form_data: Complete registration form data
            captcha_token: Captcha token from captcha solving
            captcha_id: Captcha ID from captcha solving
            antiforgery_token: Request verification token from page
            session_cookies: Session cookies (antiforgery, visitorId, aws-waf-token)
            proxy_url: Proxy URL for request
            
        Returns:
            Dictionary with success status and encrypted email/mobile/security code
        """
        try:
            logger.info("📤 Sending OTP request to BLS...")
            
            # Prepare the form data for OTP request
            otp_form_data = self._prepare_otp_form_data(
                form_data, 
                captcha_token, 
                captcha_id,
                antiforgery_token
            )
            
            # Prepare headers
            headers = self._prepare_headers(antiforgery_token, session_cookies)
            
            # Send request with proxy support
            result = await self._send_request(
                otp_form_data,
                headers,
                session_cookies,
                proxy_url,
                antiforgery_token
            )
            
            if result.get('success'):
                logger.info("✅ OTP sent successfully!")
                logger.info(f"📧 Email: {form_data.get('Email')}")
                logger.info(f"📱 Mobile: {form_data.get('Mobile')}")
                logger.info(f"🔒 EncryptedEmail: {result.get('encryptEmail')[:50]}...")
                logger.info(f"🔒 EncryptedMobile: {result.get('encryptMobile')[:50] if result.get('encryptMobile') else 'None'}...")
                logger.info(f"🔑 SecurityCode: {result.get('securityCode')[:50]}...")
                
                return {
                    "success": True,
                    "encrypted_email": result.get('encryptEmail'),
                    "encrypted_mobile": result.get('encryptMobile'),
                    "security_code": result.get('securityCode'),
                    "message": result.get('error', 'OTP sent')
                }
            else:
                logger.error(f"❌ Failed to send OTP: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"❌ Error sending OTP request: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _prepare_otp_form_data(
        self,
        form_data: Dict[str, Any],
        captcha_token: str,
        captcha_id: str,
        antiforgery_token: str
    ) -> Dict[str, str]:
        """Prepare form data for OTP request"""
        
        # Base fields
        otp_data = {
            "Mode": "register",
            "CaptchaParam": "",  # Empty for OTP request
            "CaptchaData": captcha_token,  # The solved captcha token
            "CaptchaId": captcha_id,  # The captcha ID
            
            # Server-side date fields (encrypted/hashed)
            "ServerDateOfBirth": form_data.get('DateOfBirth', ''),
            "ServerPassportExpiryDate": form_data.get('PassportExpiryDate', ''),
            "ServerPassportIssueDate": form_data.get('PassportIssueDate', ''),
            
            # Security code from initial page load
            "SecurityCode": form_data.get('SecurityCode', ''),
            
            # Mobile verification (usually False for email-only)
            "MobileVerificationEnabled": form_data.get('MobileVerificationEnabled', 'False'),
            
            # Encrypted fields (initially empty, will be populated by server response)
            "EncryptedEmail": form_data.get('EncryptedEmail', ''),
            "EncryptedMobile": form_data.get('EncryptedMobile', ''),
            
            # Personal information (BLS format exactly)
            "SurName": form_data.get('SurName', ''),  # Family Name (optional)
            "FirstName": form_data.get('FirstName', ''),  # Given Name (required)
            "LastName": form_data.get('LastName', ''),  # Last Name (required)
            
            # Dates
            "DateOfBirth": form_data.get('DateOfBirth', ''),
            "__Invariant": "DateOfBirth",  # Invariant culture marker
            
            # Passport information
            "PassportNumber": form_data.get('PassportNumber', ''),
            "PassportIssueDate": form_data.get('PassportIssueDate', ''),
            "__Invariant": "PassportIssueDate",
            "PassportExpiryDate": form_data.get('PassportExpiryDate', ''),
            "__Invariant": "PassportExpiryDate",
            
            # Country and type information (MUST be GUIDs for BLS!)
            "BirthCountry": form_data.get('BirthCountry', form_data.get('BirthCountryGuid', '')),  # GUID!
            "PassportType": form_data.get('PassportType', form_data.get('PassportTypeGuid', '')),  # GUID!
            "IssuePlace": form_data.get('IssuePlace', ''),  # Required string field
            "CountryOfResidence": form_data.get('CountryOfResidence', form_data.get('CountryOfResidenceGuid', '')),  # GUID!
            
            # Contact information
            "CountryCode": form_data.get('CountryCode', '+213'),
            "Mobile": form_data.get('Mobile', ''),
            "Email": form_data.get('Email', ''),
            
            # OTP field (empty when sending request, filled when verifying)
            "EmailOtp": "",
            "__Invariant": "EmailOtp",
            
            # Antiforgery token
            "__RequestVerificationToken": antiforgery_token
        }
        
        logger.info(f"📝 Prepared OTP form data:")
        logger.info(f"   Email: {otp_data['Email']}")
        logger.info(f"   Mobile: {otp_data['Mobile']}")
        logger.info(f"   Name: {otp_data['FirstName']} {otp_data['LastName']}")
        logger.info(f"   Passport: {otp_data['PassportNumber']}")
        logger.info(f"   CaptchaData length: {len(captcha_token)}")
        logger.info(f"   CaptchaId: {captcha_id[:50]}...")
        
        return otp_data
    
    def _prepare_headers(
        self,
        antiforgery_token: str,
        session_cookies: Dict[str, str]
    ) -> Dict[str, str]:
        """Prepare headers for OTP request"""
        
        headers = {
            "accept": "*/*",
            "accept-language": "es-ES,es;q=0.9,en;q=0.8",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://algeria.blsspainglobal.com",
            "referer": "https://algeria.blsspainglobal.com/dza/account/RegisterUser",
            "requestverificationtoken": antiforgery_token,
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }
        
        return headers
    
    async def _send_request(
        self,
        form_data: Dict[str, str],
        headers: Dict[str, str],
        session_cookies: Dict[str, str],
        proxy_url: str = None,
        antiforgery_token: str = None
    ) -> Dict[str, Any]:
        """Send the OTP request"""
        
        try:
            # Try curl_cffi first (better for AWS WAF)
            try:
                from curl_cffi import requests
                session = requests.Session(impersonate="chrome110")
                logger.info("✅ Using curl_cffi session with Chrome impersonation")
            except ImportError:
                import requests
                session = requests.Session()
                logger.info("⚠️ Using standard requests session")
            
            # Prepare cookies
            cookies = {}
            if session_cookies:
                # Filter out non-cookie attributes
                invalid_keys = ['path', 'samesite', 'domain', 'expires', 'max-age', 'secure', 'httponly']
                cookies = {k: v for k, v in session_cookies.items() if k.lower() not in invalid_keys}
            
            # Add visitorId_current if not present (REQUIRED by BLS!)
            # This should come from the registration page cookies, but fallback to default if missing
            if 'visitorId_current' not in cookies:
                cookies['visitorId_current'] = '22615162'  # Fallback to default
                logger.warning("⚠️ visitorId_current not found in cookies, using fallback: 22615162")
            else:
                logger.info(f"🆔 Using visitorId_current from cookies: {cookies['visitorId_current']}")
            
            # Add requestverificationtoken header (REQUIRED by BLS OTP endpoint!)
            if antiforgery_token:
                headers['requestverificationtoken'] = antiforgery_token
                logger.info(f"🔑 Added requestverificationtoken header: {antiforgery_token[:50]}...")
            
            # Prepare proxy
            proxies = None
            if proxy_url:
                # Remove http:// prefix if present (it will be added back)
                clean_proxy = proxy_url.replace('http://', '').replace('https://', '')
                
                if '@' in clean_proxy:
                    # Format: username:password@host:port
                    proxies = {
                        'http': f'http://{clean_proxy}',
                        'https': f'http://{clean_proxy}'
                    }
                else:
                    # Format: host:port
                    proxies = {
                        'http': f'http://{clean_proxy}',
                        'https': f'http://{clean_proxy}'
                    }
                logger.info(f"🌐 Using proxy: {proxies['http'][:70]}...")
            
            # URL encode form data
            encoded_data = urllib.parse.urlencode(form_data)
            
            logger.info(f"📤 Sending POST request to: {self.otp_endpoint}")
            logger.info(f"📦 Data length: {len(encoded_data)} bytes")
            logger.info(f"🍪 Cookies being sent: {list(cookies.keys())}")
            if 'aws-waf-token' in cookies:
                logger.info(f"🔑 AWS WAF token present: {cookies['aws-waf-token'][:50]}...")
            else:
                logger.warning("⚠️ No AWS WAF token in cookies!")
            
            # Send request (with WAF retry logic)
            response = session.post(
                self.otp_endpoint,
                data=encoded_data,
                headers=headers,
                cookies=cookies,
                proxies=proxies,
                timeout=30,
                allow_redirects=False
            )
            
            logger.info(f"📡 Response status: {response.status_code}")
            logger.info(f"📡 Response headers: {dict(response.headers)}")
            
            # Check for AWS WAF challenge (status 202)
            if response.status_code == 202:
                logger.warning("⚠️ AWS WAF challenge detected (202)!")
                logger.info("🔄 Need to solve fresh WAF challenge for OTP endpoint...")
                
                # Try to extract and solve WAF challenge from response
                try:
                    response_text = response.text
                    
                    # Check if response body is empty (content-length: 0)
                    if not response_text or len(response_text) < 100:
                        logger.warning("⚠️ 202 response has empty body")
                        logger.info("💡 Empty 202 means AWS WAF token is invalid/expired for this endpoint")
                        logger.info("🔄 Will use existing WAF token from registration page and retry with delays...")
                        
                        # The aws-waf-token cookie should already be in cookies from the registration page
                        # Try multiple retries with increasing delays
                        import asyncio
                        max_retries = 3
                        
                        for retry_num in range(1, max_retries + 1):
                            wait_time = retry_num * 2  # 2s, 4s, 6s
                            logger.info(f"🔄 Retry {retry_num}/{max_retries}: Waiting {wait_time}s before retry...")
                            await asyncio.sleep(wait_time)
                            
                            retry_response = session.post(
                                self.otp_endpoint,
                                data=encoded_data,
                                headers=headers,
                                cookies=cookies,
                                proxies=proxies,
                                timeout=30,
                                allow_redirects=False
                            )
                            
                            logger.info(f"📡 Retry {retry_num} response status: {retry_response.status_code}")
                            
                            if retry_response.status_code != 202:
                                logger.info(f"✅ Retry {retry_num} successful! Status: {retry_response.status_code}")
                                response = retry_response
                                break
                            else:
                                logger.warning(f"⚠️ Retry {retry_num} still returned 202")
                                if retry_num == max_retries:
                                    logger.error("❌ All retries exhausted, WAF challenge persists")
                                    response = retry_response
                        
                        # Skip further WAF challenge solving since we already retried
                        response_text = ""  # Clear to skip the gokuProps check below
                    
                    # Check if this is a WAF challenge page (with body content)
                    if response_text and len(response_text) > 100 and ('gokuProps' in response_text or 'x-amzn-waf-action' in response.headers):
                        logger.info("🔍 Detected WAF challenge page with content, solving directly...")
                        
                        # Solve WAF challenge directly (without full bypass validation)
                        try:
                            from awswaf.aws import AwsWaf
                            import asyncio
                            
                            # Extract WAF challenge data
                            logger.info("🔍 Extracting WAF challenge data...")
                            goku_props, host = AwsWaf.extract(response_text)
                            
                            if goku_props and host:
                                logger.info(f"✅ Extracted WAF challenge data")
                                logger.info(f"🔑 Host: {host[:50]}...")
                                
                                # Solve the challenge
                                logger.info("🔄 Solving AWS WAF challenge...")
                                waf_token = AwsWaf.solve_challenge(goku_props, host)
                                logger.info(f"✅ Generated WAF token: {waf_token[:50]}...")
                                
                                # Update cookies with new token
                                cookies['aws-waf-token'] = waf_token
                                logger.info("🔑 Updated cookies with fresh WAF token")
                                
                                # Retry the OTP request with new token
                                logger.info("🔄 Retrying OTP POST request with fresh WAF token...")
                                await asyncio.sleep(2)
                                
                                response = session.post(
                                    self.otp_endpoint,
                                    data=encoded_data,
                                    headers=headers,
                                    cookies=cookies,
                                    proxies=proxies,
                                    timeout=30,
                                    allow_redirects=False
                                )
                                
                                logger.info(f"📡 Retry response status: {response.status_code}")
                            else:
                                logger.error("❌ Failed to extract WAF challenge data")
                                
                        except Exception as e:
                            logger.error(f"❌ Error solving WAF challenge: {e}")
                    else:
                        logger.warning("⚠️ 202 response but no WAF challenge detected, retrying...")
                        import asyncio
                        await asyncio.sleep(2)
                        
                        response = session.post(
                            self.otp_endpoint,
                            data=encoded_data,
                            headers=headers,
                            cookies=cookies,
                            proxies=proxies,
                            timeout=30,
                            allow_redirects=False
                        )
                        
                        logger.info(f"📡 Retry response status: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"❌ Error handling WAF challenge: {e}")
                    logger.warning("⚠️ Attempting simple retry...")
                    import asyncio
                    await asyncio.sleep(2)
                    
                    response = session.post(
                        self.otp_endpoint,
                        data=encoded_data,
                        headers=headers,
                        cookies=cookies,
                        proxies=proxies,
                        timeout=30,
                        allow_redirects=False
                    )
                    
                    logger.info(f"📡 Fallback retry response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"📋 Response JSON: {result}")
                    return result
                except Exception as e:
                    logger.error(f"❌ Failed to parse JSON response: {e}")
                    logger.error(f"📄 Response text: {response.text[:500]}")
                    return {
                        "success": False,
                        "error": "Invalid JSON response"
                    }
            else:
                logger.error(f"❌ HTTP {response.status_code}: {response.text[:500]}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_otp(
        self,
        otp_code: str,
        encrypted_email: str,
        encrypted_mobile: str,
        security_code: str,
        form_data: Dict[str, Any],
        captcha_token: str,
        captcha_id: str,
        antiforgery_token: str,
        session_cookies: Dict[str, str],
        proxy_url: str = None
    ) -> Dict[str, Any]:
        """
        Verify OTP code with BLS
        
        This is typically done by submitting the registration form again
        with the OTP filled in and the encrypted values from the send_otp response
        """
        try:
            logger.info(f"🔐 Verifying OTP: {otp_code}")
            
            # Update form data with OTP and encrypted values
            verification_data = form_data.copy()
            verification_data.update({
                "EmailOtp": otp_code,
                "EncryptedEmail": encrypted_email,
                "EncryptedMobile": encrypted_mobile,
                "SecurityCode": security_code,
                "CaptchaData": captcha_token,
                "CaptchaId": captcha_id,
                "__RequestVerificationToken": antiforgery_token
            })
            
            # The verification is typically sent to the registration endpoint
            # (not the SendVerificationCode endpoint)
            # Implementation depends on BLS flow
            
            logger.info("✅ OTP verification data prepared")
            return {
                "success": True,
                "verification_data": verification_data
            }
            
        except Exception as e:
            logger.error(f"❌ Error verifying OTP: {e}")
            return {
                "success": False,
                "error": str(e)
            }


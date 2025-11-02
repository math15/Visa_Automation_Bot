"""
BLS Registration Final Submission Handler
Handles the final registration submission with OTP
"""

from typing import Dict, Any
from loguru import logger
import urllib.parse


class RegistrationSubmitter:
    """Handles final registration submission to BLS"""
    
    def __init__(self):
        self.submit_url = "https://algeria.blsspainglobal.com/dza/Account/RegisterUser"
    
    async def submit_final_registration(
        self,
        form_data: Dict[str, Any],
        captcha_token: str,
        captcha_id: str,
        otp_code: str,
        encrypted_email: str,
        encrypted_mobile: str,
        security_code: str,
        antiforgery_token: str,
        session_cookies: Dict[str, str],
        proxy_url: str = None
    ) -> Dict[str, Any]:
        """
        Submit final registration with OTP
        
        Args:
            form_data: User registration data
            captcha_token: Captcha token from SubmitCaptcha
            captcha_id: Captcha ID
            otp_code: OTP code from email
            encrypted_email: Encrypted email from SendRegisterUserVerificationCode
            encrypted_mobile: Encrypted mobile from SendRegisterUserVerificationCode
            security_code: Security code from SendRegisterUserVerificationCode
            antiforgery_token: Anti-forgery token
            session_cookies: Session cookies
            proxy_url: Proxy URL (optional)
            
        Returns:
            Dictionary with success status and response data
        """
        try:
            logger.info("📝 Preparing final registration submission...")
            
            # Prepare headers (exactly as in reference.txt)
            headers = self._prepare_headers(antiforgery_token, session_cookies)
            
            # Prepare form data (exactly as in reference.txt lines 69)
            final_form_data = self._prepare_final_form_data(
                form_data=form_data,
                captcha_token=captcha_token,
                captcha_id=captcha_id,
                otp_code=otp_code,
                encrypted_email=encrypted_email,
                encrypted_mobile=encrypted_mobile,
                security_code=security_code,
                antiforgery_token=antiforgery_token
            )
            
            # Send request
            response_data = await self._send_request(
                form_data=final_form_data,
                headers=headers,
                session_cookies=session_cookies,
                proxy_url=proxy_url
            )
            
            return response_data
            
        except Exception as e:
            logger.error(f"❌ Error submitting final registration: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _prepare_final_form_data(
        self,
        form_data: Dict[str, Any],
        captcha_token: str,
        captcha_id: str,
        otp_code: str,
        encrypted_email: str,
        encrypted_mobile: str,
        security_code: str,
        antiforgery_token: str
    ) -> Dict[str, str]:
        """Prepare form data for final registration (matches reference.txt line 69)"""
        
        final_data = {
            "Mode": "register",
            "CaptchaParam": "",
            "CaptchaData": captcha_token,  # The captcha token from SubmitCaptcha
            "CaptchaId": captcha_id,
            
            # Server-side date fields (from OTP request)
            "ServerDateOfBirth": form_data.get('DateOfBirth', ''),
            "ServerPassportExpiryDate": form_data.get('PassportExpiryDate', ''),
            "ServerPassportIssueDate": form_data.get('PassportIssueDate', ''),
            
            # Security code from OTP response
            "SecurityCode": security_code,
            
            # Mobile verification
            "MobileVerificationEnabled": "False",
            
            # Encrypted fields from OTP response
            "EncryptedEmail": encrypted_email,
            "EncryptedMobile": encrypted_mobile,
            
            # Personal information
            "SurName": form_data.get('SurName', ''),
            "FirstName": form_data.get('FirstName', ''),
            "LastName": form_data.get('LastName', ''),
            
            # Dates with invariant markers
            "DateOfBirth": form_data.get('DateOfBirth', ''),
            "__Invariant": "DateOfBirth",
            
            # Passport information
            "PassportNumber": form_data.get('PassportNumber', ''),
            "PassportIssueDate": form_data.get('PassportIssueDate', ''),
            "__Invariant": "PassportIssueDate",
            "PassportExpiryDate": form_data.get('PassportExpiryDate', ''),
            "__Invariant": "PassportExpiryDate",
            
            # Country and type information (GUIDs)
            "BirthCountry": form_data.get('BirthCountry', ''),
            "PassportType": form_data.get('PassportType', ''),
            "IssuePlace": form_data.get('IssuePlace', ''),
            "CountryOfResidence": form_data.get('CountryOfResidence', ''),
            
            # Contact information
            "CountryCode": form_data.get('CountryCode', '+213'),
            "Mobile": form_data.get('Mobile', ''),
            "Email": form_data.get('Email', ''),
            
            # OTP CODE - THE KEY FIELD!
            "EmailOtp": otp_code,
            "__Invariant": "EmailOtp",
            
            # Anti-forgery token
            "__RequestVerificationToken": antiforgery_token,
            
            # X-Requested-With header value (in data for some reason)
            "X-Requested-With": "XMLHttpRequest"
        }
        
        return final_data
    
    def _prepare_headers(
        self,
        antiforgery_token: str,
        session_cookies: Dict[str, str]
    ) -> Dict[str, str]:
        """Prepare headers for final registration (matches reference.txt lines 54-68)"""
        
        headers = {
            "accept": "*/*",
            "accept-language": "es-ES,es;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://algeria.blsspainglobal.com",
            "priority": "u=1, i",
            "referer": "https://algeria.blsspainglobal.com/dza/account/RegisterUser",
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
        proxy_url: str = None
    ) -> Dict[str, Any]:
        """Send the final registration request"""
        
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
            # This should come from the registration page cookies, but fallback to random if missing
            if 'visitorId_current' not in cookies:
                import random
                fallback_id = str(random.randint(10000000, 99999999))
                cookies['visitorId_current'] = fallback_id
                logger.warning(f"⚠️ visitorId_current not found in cookies, using random fallback: {fallback_id}")
            else:
                logger.info(f"🆔 Using visitorId_current from cookies: {cookies['visitorId_current']}")
            
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
            
            logger.info(f"📤 Sending POST request to: {self.submit_url}")
            logger.info(f"📊 Form data fields: {list(form_data.keys())}")
            logger.info(f"📊 OTP value: {form_data.get('EmailOtp', 'N/A')}")
            
            # Send request (with WAF retry logic)
            response = session.post(
                self.submit_url,
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
                logger.info("🔄 Need to solve fresh WAF challenge for final registration endpoint...")
                
                # Try to solve WAF challenge directly
                try:
                    response_text = response.text
                    
                    # Check if response body is empty (content-length: 0)
                    if not response_text or len(response_text) < 100:
                        logger.warning("⚠️ 202 response has empty body, need to GET the challenge page")
                        logger.info("🔄 Making GET request to retrieve WAF challenge...")
                        
                        # Make a GET request to the same endpoint to get the challenge page
                        import asyncio
                        await asyncio.sleep(1)
                        
                        challenge_response = session.get(
                            self.submit_url,
                            headers=headers,
                            cookies=cookies,
                            proxies=proxies,
                            timeout=30,
                            allow_redirects=False
                        )
                        
                        logger.info(f"📡 Challenge GET response status: {challenge_response.status_code}")
                        logger.info(f"📡 Challenge response length: {len(challenge_response.text)}")
                        response_text = challenge_response.text
                    
                    # Check if this is a WAF challenge page
                    if 'gokuProps' in response_text or 'x-amzn-waf-action' in response.headers:
                        logger.info("🔍 Detected WAF challenge in response, solving directly...")
                        
                        # Solve WAF challenge directly
                        from awswaf.aws import AwsWaf
                        import asyncio
                        
                        # Extract WAF challenge data
                        logger.info("🔍 Extracting WAF challenge data from 202 response...")
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
                            
                            # Retry the final registration request with new token
                            logger.info("🔄 Retrying final registration with fresh WAF token...")
                            await asyncio.sleep(2)
                            
                            response = session.post(
                                self.submit_url,
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
                            logger.warning("⚠️ Trying simple retry...")
                            import asyncio
                            await asyncio.sleep(2)
                            
                            response = session.post(
                                self.submit_url,
                                data=encoded_data,
                                headers=headers,
                                cookies=cookies,
                                proxies=proxies,
                                timeout=30,
                                allow_redirects=False
                            )
                            
                            logger.info(f"📡 Simple retry response status: {response.status_code}")
                    else:
                        logger.warning("⚠️ 202 response but no WAF challenge detected, retrying...")
                        import asyncio
                        await asyncio.sleep(2)
                        
                        response = session.post(
                            self.submit_url,
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
                        self.submit_url,
                        data=encoded_data,
                        headers=headers,
                        cookies=cookies,
                        proxies=proxies,
                        timeout=30,
                        allow_redirects=False
                    )
                    
                    logger.info(f"📡 Fallback retry response status: {response.status_code}")
            
            # Parse response
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    logger.info(f"📡 Response JSON: {response_json}")
                    
                    if response_json.get('success'):
                        logger.info("✅ Final registration successful!")
                        return {
                            "success": True,
                            "response": response_json
                        }
                    else:
                        logger.error(f"❌ Registration failed: {response_json}")
                        return {
                            "success": False,
                            "error": response_json.get('error', 'Unknown error'),
                            "response": response_json
                        }
                except Exception as e:
                    logger.error(f"❌ Error parsing response: {e}")
                    logger.info(f"📡 Raw response: {response.text[:500]}")
                    return {
                        "success": False,
                        "error": f"Failed to parse response: {e}",
                        "raw_response": response.text
                    }
            else:
                logger.error(f"❌ HTTP {response.status_code}")
                logger.error(f"📄 Response text: {response.text[:500]}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "raw_response": response.text
                }
            
        except Exception as e:
            logger.error(f"❌ Error sending request: {e}")
            return {
                "success": False,
                "error": str(e)
            }


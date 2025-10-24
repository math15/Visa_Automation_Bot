"""
Captcha submission module for BLS captcha handling
Handles submission of captcha solutions to BLS endpoints
"""

from typing import List, Dict, Optional
from loguru import logger


class CaptchaSubmitter:
    """Handles submission of captcha solutions to BLS"""
    
    def __init__(self):
        self.captcha_responses = {}
    
    async def submit_captcha_solution(self, captcha_id: str, selected_image_ids: List[str], 
                                    captcha_data: str, aws_waf_token: Optional[str] = None,
                                    cookies: Dict[str, str] = None, proxy_url: str = None, 
                                    existing_session = None) -> bool:
        """
        Submit captcha solution to BLS
        
        Args:
            captcha_id: The captcha ID from the form
            selected_image_ids: List of selected image IDs
            captcha_data: The captcha data parameter
            aws_waf_token: AWS WAF token (optional)
            cookies: Session cookies
            proxy_url: Proxy URL for the request
            existing_session: Existing curl_cffi session (optional)
            
        Returns:
            True if submission successful, False otherwise
        """
        try:
            logger.info(f"📤 Submitting captcha solution with {len(selected_image_ids)} selected images")
            
            # Get proxy if not provided
            if not proxy_url:
                proxy_url = await self._get_proxy()
                if not proxy_url:
                    logger.error("❌ No proxy available for BLS")
                    return False
            
            logger.info(f"🌐 Using proxy for HTTP request: {proxy_url}")
            
            # Prepare headers and cookies
            headers, session_cookies = self._prepare_headers(aws_waf_token, cookies)
            
            # Prepare data
            # Extract _RequestVerificationToken from cookies (not from aws_waf_token parameter)
            request_verification_token = cookies.get('__RequestVerificationToken', '') if cookies else ''
            
            # Validate session consistency - all values should be from the same session
            logger.info(f"🔍 Session validation:")
            logger.info(f"🔍 Id from captcha page: {captcha_id[:20]}...")
            logger.info(f"🔍 __RequestVerificationToken: {request_verification_token[:20]}...")
            logger.info(f"🔍 Antiforgery cookie: {session_cookies.get('.AspNetCore.Antiforgery.cyS7zUT4rj8', 'None')[:20] if session_cookies.get('.AspNetCore.Antiforgery.cyS7zUT4rj8') else 'None'}...")
            logger.info(f"🔍 AWS WAF token: {aws_waf_token[:20] if aws_waf_token else 'None'}...")
            
            # Check if all values are from the same session (they should have similar prefixes)
            if request_verification_token and session_cookies.get('.AspNetCore.Antiforgery.cyS7zUT4rj8'):
                token_prefix = request_verification_token[:20]
                cookie_prefix = session_cookies['.AspNetCore.Antiforgery.cyS7zUT4rj8'][:20]
                if token_prefix == cookie_prefix:
                    logger.info(f"✅ Session consistency validated - token and cookie match")
                else:
                    logger.warning(f"⚠️ Session inconsistency detected - token: {token_prefix}, cookie: {cookie_prefix}")
            
            data = self._prepare_submission_data(captcha_id, selected_image_ids, captcha_data, request_verification_token)
            
            # Submit captcha with WAF bypass handling
            submission_url = "https://algeria.blsspainglobal.com/dza/CaptchaPublic/SubmitCaptcha"
            
            # Always use standard requests library (same as test script) for consistency
            import requests
            
            # Create session with same approach as test script
            session = requests.Session()
            logger.info("🔄 Using standard requests.Session (same as test script)")
            
            # Convert existing session cookies if provided
            if existing_session and hasattr(existing_session, 'cookies'):
                try:
                    # Extract cookies from curl_cffi session
                    curl_cookies = existing_session.cookies.get_dict()
                    logger.info(f"🔄 Converting curl_cffi session cookies: {list(curl_cookies.keys())}")
                    
                    # Update our standard requests session with these cookies
                    session.cookies.update(curl_cookies)
                    logger.info(f"🍪 Converted cookies to requests session: {list(session.cookies.keys())}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to convert curl_cffi session cookies: {e}")
            
            # Also set session cookies if provided
            if session_cookies:
                session.cookies.update(session_cookies)
                logger.info(f"🍪 Set additional cookies in session: {list(session_cookies.keys())}")
            
            logger.info(f"🍪 Final session cookies: {dict(session.cookies)}")
            
            # Set proxy if provided
            if proxy_url:
                if not proxy_url.startswith('http://'):
                    proxy_url = f"http://{proxy_url}"
                session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                logger.info(f"🌐 Using proxy: {proxy_url[:50]}...")
            
            try:
                # Make POST request using standard requests (same as test script)
                logger.info(f"🔗 URL: {submission_url}")
                logger.info(f"📤 Data: {data}")
                logger.info(f"📋 Headers: {headers}")
                logger.info(f"🍪 Cookies: {dict(session.cookies)}")
                
                # Add timing optimization - submit immediately to avoid session expiration
                import time
                logger.info(f"⏰ Submitting captcha immediately to avoid session expiration...")
                
                response = session.post(
                    submission_url,
                    data=data,
                    headers=headers,  # Use the prepared headers
                    proxies=session.proxies if hasattr(session, 'proxies') else None,
                    timeout=30
                )
                
                # Get response text first for debugging
                response_text = response.text
                
                # Enhanced console debugging
                logger.info(f"📡 Captcha submission response status: {response.status_code}")
                logger.info(f"📄 Captcha submission response body: {response_text}")
                logger.info(f"🔍 Response headers: {dict(response.headers)}")
                
                # Check for WAF challenge headers specifically
                if 'x-amzn-waf-action' in response.headers:
                    logger.info(f"🛡️ WAF Action Header: {response.headers.get('x-amzn-waf-action')}")
                if 'x-amzn-waf-request-id' in response.headers:
                    logger.info(f"🛡️ WAF Request ID: {response.headers.get('x-amzn-waf-request-id')}")
                
                if response.status_code == 200:
                    # Store the response for future use
                    await self._store_captcha_response(captcha_id, response_text)
                    
                    # Check if submission was successful
                    if "success" in response_text.lower() or "valid" in response_text.lower():
                        logger.info("✅ Captcha submission successful!")
                        return True
                    else:
                        logger.error(f"❌ Captcha submission failed - response doesn't indicate success")
                        return False
                elif response.status_code == 202 and 'x-amzn-waf-action' in response.headers:
                    waf_action = response.headers.get('x-amzn-waf-action')
                    logger.info(f"🔍 AWS WAF challenge detected on captcha submission! Action: {waf_action}")
                    logger.info(f"🔍 Challenge content length: {len(response_text)}")
                    
                    # Try to solve the WAF challenge for the captcha submission URL
                    from .waf_bypass import WAFBypassHandler
                    waf_handler = WAFBypassHandler("https://algeria.blsspainglobal.com", "/dza/CaptchaPublic/SubmitCaptcha", "temp_visitor_id")
                    
                    # Pass the existing session cookies to WAF bypass
                    logger.info(f"🍪 Passing existing cookies to WAF bypass: {list(session_cookies.keys())}")
                    bypass_result = await waf_handler.try_comprehensive_bypass(proxy_url, headers, "POST", data, session_cookies)
                    
                    if bypass_result and bypass_result.get('aws_waf_token'):
                        logger.info("✅ AWS WAF challenge solved for captcha submission!")
                        fresh_waf_token = bypass_result.get('aws_waf_token')
                        fresh_cookies = bypass_result.get('cookies', {})
                        
                        # Add the fresh AWS WAF token to cookies
                        if fresh_waf_token:
                            fresh_cookies['aws-waf-token'] = fresh_waf_token
                        
                        # Make a new POST request with fresh credentials (retry with same data)
                        logger.info("🔄 Step 3: Retrying POST with fresh WAF credentials...")
                        logger.info(f"🔄 Using same data: {data}")
                        logger.info(f"🔄 Using fresh cookies: {list(fresh_cookies.keys())}")
                        
                        # Update session cookies with fresh WAF token
                        for name, value in fresh_cookies.items():
                            session.cookies.set(name, value)
                        
                        # Retry with updated session (same as test script)
                        retry_response = session.post(
                            submission_url,
                            data=data,
                            headers=headers,  # Use the prepared headers
                            proxies=session.proxies if hasattr(session, 'proxies') else None,
                            timeout=30
                        )
                        
                        retry_text = retry_response.text
                        logger.info(f"📡 Retry response status: {retry_response.status_code}")
                        logger.info(f"📄 Retry response content length: {len(retry_text)}")
                        
                        if retry_response.status_code == 200:
                            logger.info("✅ Captcha submission successful with fresh WAF credentials!")
                            return True
                        else:
                            logger.warning(f"⚠️ Retry request failed with status: {retry_response.status_code}")
                            return False
                    else:
                        logger.error("❌ Failed to solve AWS WAF challenge for captcha submission")
                        return False
                else:
                    logger.error(f"❌ Captcha submission failed with status: {response.status_code}")
                    return False
                        
            except Exception as e:
                logger.error(f"❌ Error submitting captcha solution: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error submitting captcha solution: {e}")
            return False
    
    async def _get_proxy(self) -> Optional[str]:
        """Get proxy for BLS requests"""
        try:
            from ..proxy_service import proxy_service
            from database.config import get_db
            
            async with get_db() as db:
                proxy = await proxy_service.get_proxy(db)
                if proxy:
                    return f"{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
                return None
        except Exception as e:
            logger.error(f"❌ Error getting proxy: {e}")
            return None
    
    def _prepare_headers(self, aws_waf_token: Optional[str], cookies: Dict[str, str]) -> tuple:
        """Prepare headers and cookies for submission - EXACT same as test script"""
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://algeria.blsspainglobal.com',
            'Referer': 'https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Add AWS WAF token to headers if provided
        if aws_waf_token:
            headers['aws-waf-token'] = aws_waf_token
        
        # Prepare session cookies (exclude __RequestVerificationToken - it should only be in form data)
        session_cookies = {}
        if cookies:
            # Filter out __RequestVerificationToken from cookies - it should only be in form data
            filtered_cookies = {k: v for k, v in cookies.items() if k != '__RequestVerificationToken'}
            session_cookies.update(filtered_cookies)
            logger.info(f"🍪 Filtered cookies (removed __RequestVerificationToken): {list(session_cookies.keys())}")
        
        return headers, session_cookies
    
    def _prepare_submission_data(self, captcha_id: str, selected_image_ids: List[str], 
                               captcha_data: str, request_verification_token: str) -> Dict[str, str]:
        """Prepare form data for captcha submission - EXACT same as test script"""
        data = {
            'Id': captcha_id,
            'SelectedImages': ','.join(selected_image_ids),
            'Captcha': captcha_data,
            '__RequestVerificationToken': request_verification_token  # Note: double underscore like test script
        }
        
        logger.info(f"📤 Submission data prepared:")
        logger.info(f"📤 Id: {captcha_id[:20]}...")
        logger.info(f"📤 SelectedImages: {data['SelectedImages']}")
        logger.info(f"📤 Captcha: {captcha_data[:20]}...")
        logger.info(f"📤 __RequestVerificationToken: {request_verification_token[:20]}...")
        return data
    
    async def _store_captcha_response(self, captcha_id: str, response_text: str):
        """Store captcha response for future use"""
        try:
            import json
            import os
            
            # Store in memory
            self.captcha_responses[captcha_id] = response_text
            
            # Also save to file for debugging
            debug_file = f"debug_captcha_response_{captcha_id}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response_text)
            logger.info(f"💾 Saved captcha response to {debug_file}")
            
            # Parse the response to extract useful data
            try:
                response_data = json.loads(response_text)
                logger.info(f"📊 Parsed captcha response: success={response_data.get('success')}, captchaId={response_data.get('captchaId', 'N/A')[:20]}...")
            except json.JSONDecodeError:
                logger.info("📄 Response is not JSON, treating as HTML/text")
                
        except Exception as e:
            logger.error(f"❌ Error storing captcha response: {e}")

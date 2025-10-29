"""
Captcha submission module for BLS captcha handling
Handles submission of captcha solutions to BLS endpoints with AWS WAF bypass
"""

from typing import List, Dict, Optional
from loguru import logger
import urllib.parse


class CaptchaSubmitter:
    """Handles submission of captcha solutions to BLS"""
    
    def __init__(self):
        self.captcha_responses = {}
    
    async def submit_captcha_solution(self, captcha_id: str, selected_image_ids: List[str], 
                                    captcha_data: str, aws_waf_token: Optional[str] = None,
                                    cookies: Dict[str, str] = None, proxy_url: str = None, 
                                    existing_session = None, request_verification_token: str = None) -> bool:
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
            request_verification_token: The __RequestVerificationToken from captcha page (optional)
            
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
            
            # Prepare data first
            if not request_verification_token:
                request_verification_token = cookies.get('__RequestVerificationToken', '') if cookies else ''
            
            data = self._prepare_submission_data(captcha_id, selected_image_ids, captcha_data, request_verification_token)
            
            # Submit captcha with WAF bypass handling
            submission_url = "https://algeria.blsspainglobal.com/dza/CaptchaPublic/SubmitCaptcha"
            
            # ALWAYS create a fresh session (exactly like test script line 75)
            # The test script doesn't reuse sessions - it creates fresh for submission
            try:
                from curl_cffi import requests
                session = requests.Session(impersonate="chrome110")
                logger.info("✅ Created fresh curl_cffi session with Chrome impersonation (EXACTLY like test script)")
            except:
                import requests
                session = requests.Session()
                logger.info("⚠️ Using standard requests.Session (curl_cffi not available)")
            
            # Filter cookies for session (exclude __RequestVerificationToken and cookie attributes)
            session_cookies = {}
            if cookies:
                invalid_keys = ['__RequestVerificationToken', 'path', 'samesite']
                filtered_cookies = {k: v for k, v in cookies.items() if k not in invalid_keys}
                session_cookies.update(filtered_cookies)
                logger.info(f"🍪 Filtered cookies (removed __RequestVerificationToken, path, samesite): {list(session_cookies.keys())}")
            
            # Set cookies in BOTH session.cookies AND Cookie header 
            # EXACTLY like browser curl command
            # BROWSER CURL ORDER: .AspNetCore.Antiforgery.cyS7zUT4rj8, visitorId_current, aws-waf-token
            cookies_list = []
            if session_cookies:
                # 1. .AspNetCore.Antiforgery.cyS7zUT4rj8 FIRST (browser curl order)
                if '.AspNetCore.Antiforgery.cyS7zUT4rj8' in session_cookies:
                    session.cookies.set('.AspNetCore.Antiforgery.cyS7zUT4rj8', session_cookies['.AspNetCore.Antiforgery.cyS7zUT4rj8'])
                    cookies_list.append(f".AspNetCore.Antiforgery.cyS7zUT4rj8={session_cookies['.AspNetCore.Antiforgery.cyS7zUT4rj8']}")
                
                # 2. visitorId_current SECOND (browser curl order)
                if 'visitorId_current' in session_cookies:
                    session.cookies.set('visitorId_current', session_cookies['visitorId_current'])
                    cookies_list.append(f"visitorId_current={session_cookies['visitorId_current']}")
                
                # 3. aws-waf-token THIRD (browser curl order)
                if 'aws-waf-token' in session_cookies:
                    session.cookies.set('aws-waf-token', session_cookies['aws-waf-token'])
                    cookies_list.append(f"aws-waf-token={session_cookies['aws-waf-token']}")
                    
                logger.info(f"🍪 Set cookies in BOTH session.cookies AND Cookie header (BROWSER CURL ORDER)")
                logger.info(f"🍪 Set {len(cookies_list)} cookies in BROWSER order: antiforgery → visitorId_current → aws-waf-token")
            
            # Set proxy (exactly like test script lines 88-95)
            if proxy_url:
                if not proxy_url.startswith('http://'):
                    proxy_url = f"http://{proxy_url}"
                session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                logger.info(f"🌐 Using proxy: {proxy_url[:50]}...")
            else:
                logger.info("⚠️ No proxy configured - using direct connection")
            
            # NOW prepare headers with session cookies (AFTER setting cookies in session)
            # ALWAYS include all headers - curl_cffi doesn't auto-add User-Agent/Sec-Ch-Ua
            headers = self._prepare_headers_only(captcha_id, aws_waf_token, session_cookies)
            
            # Add Cookie header explicitly (test script line 148)
            # The test script sets cookies in BOTH session.cookies AND Cookie header
            if cookies_list:
                headers['Cookie'] = '; '.join(cookies_list)
                logger.info(f"🍪 Set Cookie header explicitly (TEST SCRIPT line 148): {len(cookies_list)} cookies")
                logger.info(f"🍪 Cookie header value (first 150 chars): {headers['Cookie'][:150]}...")
            
            # Debug: Log Referer URL to verify it matches test script
            referer_url = headers.get('Referer', '')
            logger.info(f"🔍 Referer URL: {referer_url[:150]}...")
            
            # Validate session consistency
            logger.info(f"🔍 Session validation:")
            logger.info(f"🔍 Id from captcha page: {captcha_id[:20]}...")
            logger.info(f"🔍 __RequestVerificationToken: {request_verification_token[:20]}...")
            logger.info(f"🔍 Antiforgery cookie: {session_cookies.get('.AspNetCore.Antiforgery.cyS7zUT4rj8', 'None')[:20] if session_cookies.get('.AspNetCore.Antiforgery.cyS7zUT4rj8') else 'None'}...")
            logger.info(f"🔍 AWS WAF token: {aws_waf_token[:20] if aws_waf_token else 'None'}...")
            
            # Check if all values are from the same session
            if request_verification_token and session_cookies.get('.AspNetCore.Antiforgery.cyS7zUT4rj8'):
                token_prefix = request_verification_token[:20]
                cookie_prefix = session_cookies['.AspNetCore.Antiforgery.cyS7zUT4rj8'][:20]
                if token_prefix == cookie_prefix:
                    logger.info(f"✅ Session consistency validated - token and cookie match")
                else:
                    logger.warning(f"⚠️ Session inconsistency detected - token: {token_prefix}, cookie: {cookie_prefix}")
            
            logger.info(f"🍪 Final session cookies: {dict(session.cookies)}")
            
            try:
                # Debug output
                logger.info(f"🔗 URL: {submission_url}")
                logger.info(f"📤 Data keys: {list(data.keys())}")
                for key in data.keys():
                    value_preview = str(data[key])[:100] if data[key] else ''
                    logger.info(f"📤 Data[{key}]: {value_preview}... (length: {len(str(data[key]))})")
                logger.info(f"📋 Headers: {list(headers.keys())}")
                logger.info(f"🍪 Session cookies (curl_cffi will add these automatically): {dict(session.cookies)}")
                
                # Add timing optimization - submit immediately to avoid session expiration
                import time
                logger.info(f"⏰ Submitting captcha immediately to avoid session expiration...")
                
                # Match test script EXACTLY (line 185) - just pass url, data, headers, timeout
                # Test script: response = session.post(url, data=data, headers=headers, timeout=30)
                response = session.post(submission_url, data=data, headers=headers, timeout=30)
                
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
    
    def _prepare_headers_only(self, captcha_id: str = None, aws_waf_token: Optional[str] = None, session_cookies: Dict[str, str] = None) -> dict:
        """Prepare headers without Cookie header (Cookie is built separately from session cookies) - MATCH BROWSER CURL"""
        # Build Referer URL with data parameter (MUST include this!)
        referer_url = 'https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha'
        if captcha_id:
            referer_data_param = urllib.parse.quote(captcha_id, safe='')
            referer_url = f'{referer_url}?data={referer_data_param}'
        
        # Headers in EXACT browser order from curl command
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://algeria.blsspainglobal.com',
            'Priority': 'u=1, i',
            'Referer': referer_url,
            'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',  # CRITICAL: Must be 'empty' not empty string
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        return headers
    
    def _prepare_headers(self, aws_waf_token: Optional[str], cookies: Dict[str, str], captcha_id: str = None) -> tuple:
        """Prepare headers and cookies for submission - Match browser curl exactly"""
        
        # Build Referer URL with data parameter (MUST include this!)
        referer_url = 'https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha'
        if captcha_id:
            referer_data_param = urllib.parse.quote(captcha_id, safe='')
            referer_url = f'{referer_url}?data={referer_data_param}'
        
        # Headers in EXACT browser order from curl command
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://algeria.blsspainglobal.com',
            'Priority': 'u=1, i',
            'Referer': referer_url,
            'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',  # CRITICAL: Must be 'empty' not empty string
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        # Prepare session cookies (exclude __RequestVerificationToken - it should only be in form data)
        session_cookies = {}
        if cookies:
            # Filter out __RequestVerificationToken and cookie attributes like 'path', 'samesite' that aren't actual cookies
            invalid_keys = ['__RequestVerificationToken', 'path', 'samesite']
            filtered_cookies = {k: v for k, v in cookies.items() if k not in invalid_keys}
            session_cookies.update(filtered_cookies)
            logger.info(f"🍪 Filtered cookies (removed __RequestVerificationToken, path, samesite): {list(session_cookies.keys())}")
        
        return headers, session_cookies
    
    def _prepare_submission_data(self, captcha_id: str, selected_image_ids: List[str],
                              captcha_data: str, request_verification_token: str) -> Dict[str, str]:
        """Prepare form data for captcha submission - EXACT same as browser curl"""
        # CRITICAL: The browser sends form data in this EXACT order, and includes X-Requested-With in the data payload
        data = {
            'SelectedImages': ','.join(selected_image_ids),
            'Id': captcha_id,
            'Captcha': captcha_data,
            '__RequestVerificationToken': request_verification_token,
            'X-Requested-With': 'XMLHttpRequest'  # CRITICAL: This is in BOTH header AND form data!
        }
        
        logger.info(f"📤 Submission data prepared (BROWSER ORDER):")
        logger.info(f"📤 SelectedImages: {data['SelectedImages']}")
        logger.info(f"📤 Id: {captcha_id[:20]}...")
        logger.info(f"📤 Captcha: {captcha_data[:20]}...")
        logger.info(f"📤 __RequestVerificationToken: {request_verification_token[:20]}...")
        logger.info(f"📤 X-Requested-With: {data['X-Requested-With']}")
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

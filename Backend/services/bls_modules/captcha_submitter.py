"""
Captcha submission module for BLS captcha handling
Handles submission of captcha solutions to BLS endpoints
"""

import aiohttp
from typing import List, Dict, Optional
from loguru import logger


class CaptchaSubmitter:
    """Handles submission of captcha solutions to BLS"""
    
    def __init__(self):
        pass
    
    async def submit_captcha_solution(self, captcha_id: str, selected_image_ids: List[str], 
                                    captcha_data: str, aws_waf_token: str = None, 
                                    cookies: Dict[str, str] = None, proxy_url: str = None, 
                                    captcha_page_url: str = None) -> bool:
        """
        Submit captcha solution to BLS endpoint
        
        Args:
            captcha_id: Captcha ID
            selected_image_ids: List of selected image IDs
            captcha_data: Captcha data parameter
            aws_waf_token: AWS WAF token
            cookies: Session cookies
            proxy_url: Proxy URL to use
            
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
            headers, session_cookies = self._prepare_headers(aws_waf_token, cookies, captcha_page_url)
            
            # Prepare data
            request_verification_token = cookies.get('__RequestVerificationToken', '') if cookies else ''
            data = self._prepare_submission_data(captcha_id, selected_image_ids, captcha_data, request_verification_token)
            
            # DEBUG: Log all form data being sent
            logger.info("🔍 DEBUG - Form data being sent via POST:")
            logger.info(f"🔍 DEBUG - Id: {captcha_id}")
            logger.info(f"🔍 DEBUG - SelectedImages: {','.join(selected_image_ids)}")
            logger.info(f"🔍 DEBUG - Captcha: {captcha_data}")
            logger.info(f"🔍 DEBUG - __RequestVerificationToken: {request_verification_token}")
            logger.info(f"🔍 DEBUG - Total form data: {data}")
            
            # DEBUG: Log headers being sent
            logger.info("🔍 DEBUG - Headers being sent:")
            for key, value in headers.items():
                if key.lower() == 'cookie':
                    logger.info(f"🔍 DEBUG - {key}: {value[:100]}...")
                else:
                    logger.info(f"🔍 DEBUG - {key}: {value}")
            
            # DEBUG: Log cookies being sent
            logger.info("🔍 DEBUG - Cookies being sent:")
            for key, value in session_cookies.items():
                logger.info(f"🔍 DEBUG - {key}: {value[:50]}...")
            
            # DEBUG: Log submission URL
            submission_url = "https://algeria.blsspainglobal.com/dza/CaptchaPublic/SubmitCaptcha"
            logger.info(f"🔍 DEBUG - Submission URL: {submission_url}")
            
            # Submit captcha with WAF bypass handling
            
            # DEBUG: Log the actual POST request body
            import urllib.parse
            post_body = urllib.parse.urlencode(data)
            logger.info(f"🔍 DEBUG - POST request body: {post_body}")
            logger.info(f"🔍 DEBUG - POST body length: {len(post_body)} characters")
            
            # DEBUG: Check if token is fresh (extracted from captcha page)
            logger.info(f"🔍 DEBUG - Token source: {'captcha_page' if request_verification_token else 'missing'}")
            logger.info(f"🔍 DEBUG - Token length: {len(request_verification_token) if request_verification_token else 0}")
            
            # DEBUG: Check critical session cookies
            logger.info(f"🔍 DEBUG - Has visitorId_current: {'visitorId_current' in session_cookies}")
            
            # Check for any antiforgery cookie (they have dynamic names)
            has_antiforgery = any(key.startswith('.AspNetCore.Antiforgery.') for key in session_cookies.keys())
            logger.info(f"🔍 DEBUG - Has antiforgery cookie: {has_antiforgery}")
            
            logger.info(f"🔍 DEBUG - Has aws-waf-token: {'aws-waf-token' in session_cookies}")
            
            # DEBUG: Show all cookie names
            logger.info(f"🔍 DEBUG - All cookie names: {list(session_cookies.keys())}")
            
            # Convert curl_cffi cookies to aiohttp-compatible format
            aiohttp_cookies = {}
            if session_cookies:
                # Filter out cookie attributes and create clean dictionary
                for name, value in session_cookies.items():
                    if name not in ['path', 'samesite', 'domain', 'expires', 'max-age', 'secure', 'httponly']:
                        aiohttp_cookies[name] = value
                
                logger.info(f"🔍 DEBUG - Converted cookies for aiohttp: {aiohttp_cookies}")
            
            async with aiohttp.ClientSession(cookies=aiohttp_cookies) as session:
                async with session.post(
                    submission_url,
                    headers=headers,
                    data=data,
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    # Get response text first for debugging
                    response_text = await response.text()
                    
                    # Enhanced console debugging
                    logger.info(f"📡 Captcha submission response status: {response.status}")
                    logger.info(f"📄 Captcha submission response body: {response_text}")
                    logger.info(f"🔍 Response headers: {dict(response.headers)}")
                    
                    if response.status == 200:
                        # Store the response for future use
                        await self._store_captcha_response(captcha_id, response_text)
                        
                        # Check if submission was successful
                        if "success" in response_text.lower() or "valid" in response_text.lower():
                            logger.info("✅ Captcha submission successful!")
                            return True
                        else:
                            logger.error(f"❌ Captcha submission failed - response doesn't indicate success")
                            return False
                    elif response.status == 202:
                        logger.info("🔍 AWS WAF challenge detected on captcha submission!")
                        logger.info(f"🔍 Challenge content length: {len(response_text)}")
                        
                        # Try to solve the WAF challenge for the captcha submission URL
                        from .waf_bypass import WAFBypassHandler
                        waf_handler = WAFBypassHandler("https://algeria.blsspainglobal.com", "/dza/CaptchaPublic/SubmitCaptcha", "temp_visitor_id")
                        bypass_result = await waf_handler.try_comprehensive_bypass(proxy_url, headers, "POST", data)
                        
                        if bypass_result and bypass_result.get('success'):
                            logger.info("✅ AWS WAF challenge solved for captcha submission!")
                            new_waf_token = bypass_result.get('waf_token')
                            new_cookies = bypass_result.get('cookies', {})
                            
                            # Update cookies with new WAF token
                            if new_waf_token:
                                session_cookies['aws-waf-token'] = new_waf_token.rstrip(':')
                            
                            # Merge new cookies
                            session_cookies.update(new_cookies)
                            
                            # Retry submission with new WAF token
                            logger.info("🔄 Retrying captcha submission with new WAF token...")
                            async with session.post(
                                submission_url,
                                headers=headers,
                                data=data,
                                cookies=session_cookies,
                                proxy=proxy_url,
                                timeout=aiohttp.ClientTimeout(total=30)
                            ) as retry_response:
                                
                                # Get retry response text for debugging
                                retry_response_text = await retry_response.text()
                                
                                # Enhanced console debugging for retry
                                logger.info(f"📡 Retry submission response status: {retry_response.status}")
                                logger.info(f"📄 Retry submission response body: {retry_response_text}")
                                logger.info(f"🔍 Retry response headers: {dict(retry_response.headers)}")
                                
                                if retry_response.status == 200:
                                    # Store the retry response for future use
                                    await self._store_captcha_response(captcha_id, retry_response_text)
                                    
                                    if "success" in retry_response_text.lower() or "valid" in retry_response_text.lower():
                                        logger.info("✅ Captcha submission successful after WAF bypass!")
                                        return True
                                    else:
                                        logger.error("❌ Captcha submission failed after WAF bypass - response doesn't indicate success")
                                        return False
                                else:
                                    logger.error(f"❌ Retry submission failed with status: {retry_response.status}")
                                    return False
                        else:
                            logger.error("❌ Failed to solve AWS WAF challenge for captcha submission")
                            return False
                    else:
                        logger.error(f"❌ Captcha submission failed with status: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Error submitting captcha solution: {e}")
            return False
    
    async def _get_proxy(self) -> Optional[str]:
        """Get proxy for BLS requests"""
        try:
            from ..proxy_service import proxy_service
            from database.config import get_db
            
            db = next(get_db())
            proxy_url = await proxy_service.get_proxy_for_bls(db, skip_validation=True)
            return proxy_url
        except Exception as e:
            logger.error(f"❌ Error getting proxy: {e}")
            return None
    
    def _prepare_headers(self, aws_waf_token: str = None, cookies: Dict[str, str] = None, captcha_page_url: str = None) -> tuple:
        """Prepare headers and cookies for captcha submission"""
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://algeria.blsspainglobal.com',
            'Referer': captcha_page_url,
            'Priority': 'u=1, i',
            'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        # Prepare cookies dictionary
        session_cookies = cookies.copy() if cookies else {}
        if aws_waf_token:
            # Clean the token (remove trailing colon if present)
            clean_token = aws_waf_token.rstrip(':')
            session_cookies['aws-waf-token'] = clean_token
            logger.info(f"🔑 Using AWS WAF token as cookie: {clean_token[:20]}...")
        
        return headers, session_cookies
    
    def _prepare_submission_data(self, captcha_id: str, selected_image_ids: List[str], captcha_data: str, request_verification_token: str = None) -> Dict[str, str]:
        """Prepare form data for captcha submission"""
        # Convert selected image IDs to the format expected by BLS
        selected_ids_str = ','.join(selected_image_ids)
        
        data = {
            'Id': captcha_id,
            'SelectedImages': selected_ids_str,
            'Captcha': captcha_data
        }
        
        # Add request verification token if provided (REQUIRED for captcha submission!)
        if request_verification_token:
            data['__RequestVerificationToken'] = request_verification_token
        
        logger.info(f"📤 Submission data: Id={captcha_id[:20]}..., SelectedImages={selected_ids_str}, Captcha={captcha_data[:20]}..., __RequestVerificationToken={request_verification_token[:20] if request_verification_token else 'None'}...")
        return data
    
    async def _store_captcha_response(self, captcha_id: str, response_text: str):
        """Store captcha response for future use"""
        try:
            import json
            import os
            from datetime import datetime
            
            # Create responses directory if it doesn't exist
            responses_dir = "captcha_responses"
            if not os.path.exists(responses_dir):
                os.makedirs(responses_dir)
            
            # Parse the response to extract useful data
            try:
                response_data = json.loads(response_text)
                logger.info(f"📊 Parsed captcha response: success={response_data.get('success')}, captchaId={response_data.get('captchaId', 'N/A')[:20]}...")
            except json.JSONDecodeError:
                logger.warning("⚠️ Could not parse captcha response as JSON")
                response_data = {"raw_response": response_text}
            
            # Create filename with timestamp and captcha ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{responses_dir}/captcha_response_{captcha_id[:8]}_{timestamp}.json"
            
            # Store the response
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "captcha_id": captcha_id,
                    "timestamp": timestamp,
                    "response": response_data,
                    "raw_response": response_text
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Captcha response stored: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store captcha response: {e}")

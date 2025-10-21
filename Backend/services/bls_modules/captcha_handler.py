"""
Captcha Handler Module

This module handles BLS captcha solving using modular components:
- Image extraction
- Instruction analysis  
- Captcha solving
- Captcha submission
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from loguru import logger

from .image_extractor import ImageExtractor
from .instruction_analyzer import InstructionAnalyzer
from .captcha_solver import CaptchaSolver
from .captcha_submitter import CaptchaSubmitter


class CaptchaHandler:
    """Main captcha handler that coordinates all captcha-related operations"""
    
    def __init__(self, base_url: str, register_url: str, visitor_id: str):
        self.base_url = base_url
        self.register_url = register_url
        self.visitor_id = visitor_id
    
        # Initialize modular components
        self.image_extractor = ImageExtractor()
        self.instruction_analyzer = InstructionAnalyzer()
        self.captcha_solver = CaptchaSolver()
        self.captcha_submitter = CaptchaSubmitter()
    
    def extract_captcha_info(self, page_content: str) -> Dict[str, Any]:
        """Extract captcha information from page content"""
        logger.info("🔍 Extracting captcha info from page...")
        
        try:
            # Search for BLS CaptchaId patterns
            import re
            
            # Pattern 1: CaptchaId hidden input
            captcha_id_patterns = [
                r'<input[^>]*name=["\']CaptchaId["\'][^>]*value=["\']([^"\']+)["\']',
                r'<input[^>]*value=["\']([^"\']+)["\'][^>]*name=["\']CaptchaId["\']',
                r'CaptchaId["\']\s*value=["\']([^"\']+)["\']',
                r'value=["\']([^"\']+)["\']\s*name=["\']CaptchaId["\']'
            ]
            
            logger.info("🔍 Searching for BLS CaptchaId patterns...")
            
            captcha_id = None
            for i, pattern in enumerate(captcha_id_patterns, 1):
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                if matches:
                    captcha_id = matches[0]
                    logger.info(f"✅ Found BLS CaptchaId with pattern {i}: {matches}")
                    break
            
            if not captcha_id:
                logger.warning("⚠️ No BLS CaptchaId found")
                return {}
            
            # Extract captcha data parameter to construct proper captcha URL
            captcha_data = self._extract_captcha_data_param(page_content)
            if not captcha_data:
                logger.warning("⚠️ No captcha data parameter found, using registration URL")
                page_url = self.register_url
            else:
                # DEBUG: Log the extracted captcha data
                logger.info(f"🔍 DEBUG - Extracted captcha_data (repr): {repr(captcha_data)}")
                logger.info(f"🔍 DEBUG - Extracted captcha_data: {captcha_data}")
                logger.info(f"🔍 DEBUG - captcha_data length: {len(captcha_data)}")
                logger.info(f"🔍 DEBUG - captcha_data type: {type(captcha_data)}")
                
                # Construct the proper captcha page URL
                page_url = f"{self.base_url}/dza/CaptchaPublic/GenerateCaptcha?data={captcha_data}"
                logger.info(f"🎯 Constructed captcha page URL: {page_url}")
            
            return {
                "type": "bls_captcha",
                "captcha_id": captcha_id,
                "site_key": "mayas94-9c2063ba-0944-cd88-ab10-9c4325fbb9fd",  # NoCaptchaAI key
                "page_url": page_url
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting captcha info: {e}")
            return {}
    
    async def solve_captcha(self, captcha_info: Dict[str, Any], form_data: Dict[str, Any], 
                          proxy_url: str = None, registration_page: str = None, session_cookies: Dict[str, str] = None) -> Optional[str]:
        """Solve captcha using the appropriate method"""
        try:
            captcha_type = captcha_info.get("type")
            logger.info(f"🔍 Solving captcha type: {captcha_type}")
            
            if captcha_type == "bls_captcha":
                captcha_id = captcha_info.get("captcha_id")
                page_url = captcha_info.get("page_url", self.register_url)
                
                return await self._solve_bls_image_captcha(
                    captcha_id, page_url, form_data, proxy_url, registration_page, session_cookies
                )
            else:
                logger.warning(f"⚠️ Unsupported captcha type: {captcha_type}")
                return "MANUAL_CAPTCHA_REQUIRED"
            
        except Exception as e:
            logger.error(f"❌ Error solving captcha: {e}")
            return "MANUAL_CAPTCHA_REQUIRED"
    
    async def extract_captcha_images_with_ids(self, page_url: str, 
                                            cookies: Dict[str, str] = None, proxy_url: str = None,
                                            form_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract captcha images and their IDs from the page"""
        logger.info("🌐 Extracting captcha images with IDs from BLS page using HTTP...")
        
        try:
            # Get page content (captcha page will generate its own fresh WAF token)
            content, cookies = await self._get_captcha_page_content(page_url, cookies, proxy_url, form_data)
            if not content:
                logger.error("❌ Failed to get captcha page content")
                return {}
            
            # Extract visible images
            captcha_images, image_ids = self.image_extractor.extract_visible_images(content)
            
            # Extract instruction
            instruction = self.instruction_analyzer.extract_instruction(content)
            
            # Extract Id and Captcha fields from captcha page
            captcha_fields = self._extract_captcha_page_fields(content)
            
            return {
                "images": captcha_images,
                "image_ids": image_ids,
                "instruction": instruction,
                "content": content,
                "captcha_fields": captcha_fields,
                "cookies": cookies  # Return the fresh cookies from captcha page
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting captcha images with IDs: {e}")
            return {}
    
    def _extract_captcha_page_fields(self, captcha_page_content: str) -> Dict[str, str]:
        """Extract Id, Captcha, and __RequestVerificationToken fields from the captcha page HTML"""
        try:
            import re
            
            result = {}
            
            # Extract Id field
            id_pattern = r'<input[^>]*name="Id"[^>]*value="([^"]*)"'
            id_match = re.search(id_pattern, captcha_page_content)
            if id_match:
                captcha_id = id_match.group(1)
                # Decode HTML entities
                captcha_id = captcha_id.replace('&#x2B;', '+').replace('&amp;', '&')
                result['Id'] = captcha_id
                logger.info(f"✅ Extracted captcha page Id: {captcha_id[:20]}...")
            
            # Extract Captcha field
            captcha_pattern = r'<input[^>]*name="Captcha"[^>]*value="([^"]*)"'
            captcha_match = re.search(captcha_pattern, captcha_page_content)
            if captcha_match:
                captcha_data = captcha_match.group(1)
                # Decode HTML entities
                captcha_data = captcha_data.replace('&#x2B;', '+').replace('&amp;', '&')
                result['Captcha'] = captcha_data
                logger.info(f"✅ Extracted captcha page Captcha: {captcha_data[:20]}...")
            
            # Extract __RequestVerificationToken field (REQUIRED for captcha submission!)
            token_pattern = r'<input[^>]*name="__RequestVerificationToken"[^>]*value="([^"]*)"'
            token_match = re.search(token_pattern, captcha_page_content)
            if token_match:
                request_token = token_match.group(1)
                result['__RequestVerificationToken'] = request_token
                logger.info(f"✅ Extracted captcha page __RequestVerificationToken: {request_token[:20]}...")
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Error extracting captcha page fields: {e}")
            return {}
    
    def _sanitize_data_param(self, raw: str) -> str:
        """Sanitize captcha data parameter by removing quotes and handling encoding"""
        if raw is None:
            return ""
        
        try:
            from html import unescape
            from urllib.parse import quote_plus
            
            # Unescape HTML entities (turn '&#x2B;' into '+', '&amp;' into '&')
            s = unescape(raw)
            # Trim whitespace and surrounding quotes
            s = s.strip().strip('\'"')
            
            # If string contains spaces or raw plus signs that should be percent-encoded,
            # re-encode safely. Only do this if you detect the string looks unencoded.
            # If it already contains % signs, prefer leaving it as-is.
            if '%' not in s:
                s = quote_plus(s, safe='')  # encode into %-format
            
            logger.info(f"🔧 Sanitized captcha_data: {repr(s)}")
            return s
            
        except Exception as e:
            logger.error(f"❌ Error sanitizing captcha data: {e}")
            return raw
    
    def _extract_captcha_data_param(self, html_content: str) -> str:
        try:
            import re
            from html import unescape
            from urllib.parse import quote_plus
            
            # Prefer exact hidden input names if present
            m = re.search(r'<input[^>]*name=["\'](?:CaptchaData|Captcha)["\'][^>]*value=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            if m:
                raw = m.group(1)
                logger.info(f"🔍 Found captcha data in hidden input: {repr(raw)}")
            else:
                # fallback to earlier patterns but be conservative
                m2 = re.search(r'GenerateCaptcha\?data=([^"\'>\s;]+)', html_content, re.IGNORECASE)
                raw = m2.group(1) if m2 else ""
                logger.info(f"🔍 Found captcha data in URL pattern: {repr(raw)}")

            if not raw:
                logger.warning("⚠️ No captcha data parameter found")
                return ""

            # Unescape HTML entities and trim quotes/spaces
            raw = unescape(raw).strip().strip('\'"')
            # If raw appears percent-encoded already, keep it; else percent-encode
            if '%' not in raw:
                raw = quote_plus(raw, safe='')
            
            logger.info(f"✅ Extracted captcha data parameter: {raw[:20]}...")
            logger.info(f"🔧 Final sanitized captcha_data: {repr(raw)}")
            return raw
            
        except Exception as e:
            logger.error(f"❌ Error extracting captcha data parameter: {e}")
            return ""
    
    async def _solve_bls_image_captcha(self, captcha_id: str, page_url: str, 
                                     form_data: Dict[str, Any], 
                                     proxy_url: str, registration_page: str, session_cookies: Dict[str, str] = None) -> str:
        """Solve BLS image captcha""" 
        try:
            logger.info("🎯 BLS image selection captcha detected")
            
            # Extract captcha data parameter from form data or HTML content
            captcha_data = form_data.get('CaptchaData', '')
            if not captcha_data:
                logger.warning("⚠️ No CaptchaData in form data, trying to extract from HTML")
                # Try to get the registration page content to extract captcha data
                if registration_page:
                    captcha_data = self._extract_captcha_data_param(registration_page)
                if not captcha_data:
                    logger.error("❌ Failed to extract captcha data parameter")
                    return "MANUAL_CAPTCHA_REQUIRED"
            
            logger.info(f"✅ Extracted captcha data parameter: {captcha_data[:20]}...")
            
            # Construct the captcha page URL
            captcha_url = f"{self.base_url}/dza/CaptchaPublic/GenerateCaptcha?data={captcha_data}"
            logger.info(f"🎯 Constructed captcha URL: {captcha_url}")
            
            # Prepare cookies for the captcha request
            cookies = {
                'visitor_id': self.visitor_id,
                'antiforgery_cookie': form_data.get('__RequestVerificationToken', '')
            }
            
            # Extract images and instruction
            result = await self.extract_captcha_images_with_ids(captcha_url, session_cookies, proxy_url, form_data)
            if not result:
                logger.error("❌ Failed to extract captcha images")
                return "MANUAL_CAPTCHA_REQUIRED"
            
            captcha_images = result["images"]
            image_ids = result["image_ids"]
            instruction = result["instruction"]
            captcha_fields = result.get("captcha_fields", {})
            
            # CRITICAL: Get the fresh cookies from the captcha page request
            # These include the new aws-waf-token and visitorId_current
            captcha_page_cookies = result.get("cookies", {})
            logger.info(f"🔍 DEBUG - Captcha page cookies: {captcha_page_cookies}")
            
            # CRITICAL: Merge original session cookies with fresh captcha page cookies
            # The original session cookies contain visitorId_current and antiforgery cookies
            # The captcha page cookies contain the fresh aws-waf-token
            merged_cookies = {}
            
            # Add original session cookies (visitorId_current, antiforgery, etc.)
            if session_cookies:
                for key, value in session_cookies.items():
                    if key not in ['path', 'samesite', 'domain', 'expires', 'max-age', 'secure', 'httponly']:
                        merged_cookies[key] = value
                        logger.info(f"🔍 DEBUG - Added original cookie: {key} = {value[:50]}...")
            
            # Add/override with fresh captcha page cookies (aws-waf-token, etc.)
            if captcha_page_cookies:
                for key, value in captcha_page_cookies.items():
                    if key not in ['path', 'samesite', 'domain', 'expires', 'max-age', 'secure', 'httponly']:
                        merged_cookies[key] = value
                        logger.info(f"🔍 DEBUG - Added/updated captcha page cookie: {key} = {value[:50]}...")
            
            logger.info(f"🔍 DEBUG - Final merged cookies: {merged_cookies}")
            captcha_page_cookies = merged_cookies
            
            if not captcha_images or not instruction:
                logger.error("❌ No captcha images or instruction found")
                return "MANUAL_CAPTCHA_REQUIRED"
            
            # Check if we have the required captcha page fields
            if not captcha_fields.get('Id') or not captcha_fields.get('Captcha'):
                logger.error("❌ Failed to extract Id and Captcha fields from captcha page")
                return "MANUAL_CAPTCHA_REQUIRED"
            
            # Use the Id, Captcha, and __RequestVerificationToken from captcha page
            captcha_page_id = captcha_fields['Id']
            captcha_page_data = captcha_fields['Captcha']
            captcha_page_token = captcha_fields.get('__RequestVerificationToken', '')
            logger.info(f"✅ Using captcha page Id: {captcha_page_id[:20]}...")
            logger.info(f"✅ Using captcha page data: {captcha_page_data[:20]}...")
            logger.info(f"✅ Using captcha page token: {captcha_page_token[:20]}...")
            
            # Solve captcha
            selected_image_ids = await self.captcha_solver.solve_bls_image_captcha(captcha_images, image_ids, instruction)
            if not selected_image_ids:
                logger.error("❌ Failed to solve captcha")
                return "MANUAL_CAPTCHA_REQUIRED"
            
            # Prepare cookies with the captcha page token (REQUIRED for captcha submission!)
            # Use the fresh cookies from the captcha page (includes aws-waf-token and visitorId_current)
            submission_cookies = captcha_page_cookies.copy() if captcha_page_cookies else {}
            if captcha_page_token:
                submission_cookies['__RequestVerificationToken'] = captcha_page_token
            
            logger.info(f"🔍 DEBUG - Final submission cookies: {submission_cookies}")
            
            # Submit solution using the correct Id, Captcha, and __RequestVerificationToken from captcha page
            success = await self.captcha_submitter.submit_captcha_solution(
                captcha_page_id, selected_image_ids, captcha_page_data, None, submission_cookies, proxy_url, captcha_url
            )
                        
            if success:
                logger.info("✅ Captcha solved and submitted successfully!")
                return "CAPTCHA_SOLVED"
            else:
                logger.error("❌ Failed to submit captcha solution")
                return "MANUAL_CAPTCHA_REQUIRED"
                    
        except Exception as e:
            logger.error(f"❌ Error solving BLS image captcha: {e}")
            return "MANUAL_CAPTCHA_REQUIRED"

    async def _get_proxy(self) -> Optional[str]:
        """Get proxy for BLS requests"""
        try:
            from ..proxy_service import proxy_service
            from ..database import get_db
            
            db = next(get_db())
            proxy_url = await proxy_service.get_proxy_for_bls(db, skip_validation=True)
            return proxy_url
        except Exception as e:
            logger.error(f"❌ Error getting proxy: {e}")
            return None
    
    async def _get_captcha_page_content(self, page_url: str, 
                                     cookies: Dict[str, str] = None, proxy_url: str = None,
                                     form_data: Dict[str, Any] = None, existing_session = None) -> tuple[str, dict]:
        """Get captcha page content with WAF bypass handling and retry logic"""
        logger.info("🔄 Using comprehensive WAF bypass for captcha page...")
        logger.info(f"🔍 DEBUG - _get_captcha_page_content called with URL: {page_url}")
        logger.info(f"🔍 DEBUG - Cookies parameter: {cookies}")
        logger.info(f"🔍 DEBUG - Proxy URL: {proxy_url}")
        logger.info(f"🔍 DEBUG - Form data: {form_data}")
        logger.info(f"🔍 DEBUG - Existing session: {existing_session}")
        
        # DEBUG: Check if this method is actually being called
        import traceback
        logger.info(f"🔍 DEBUG - Call stack: {traceback.format_stack()[-3:-1]}")
        
        try:
            # Use the SAME approach as our working test script
            logger.info("🔄 Using test script approach for captcha page...")
            
            # Import the same modules as test script
            import sys
            import os
            import time
            from curl_cffi import requests
            
            # Add awswaf path (same as test script)
            awswaf_path = os.path.join(os.path.dirname(__file__), '..', '..', 'awswaf', 'python')
            sys.path.insert(0, awswaf_path)
            
            from awswaf.aws import AwsWaf
            
            # Create session with EXACT same headers as test script
            session = requests.Session(impersonate="chrome")
            
            # Use EXACT same header setting approach as test script
            session.headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'ar-DZ,ar;q=0.9,en;q=0.8',  # Algerian headers (same as test script)
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
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
                # Algerian IP spoofing (same as test script)
                'X-Forwarded-For': '41.200.0.1',
                'X-Real-IP': '41.200.0.1',
                'X-Client-IP': '41.200.0.1',
                'CF-IPCountry': 'DZ',
            }
            
            # Use same proxy as test script
            session.proxies = {
                'http': 'http://7929b5ffffe8ef9be2d0__cr.es:18b90548041f7f87@gw.dataimpulse.com:10000',
                'https': 'http://7929b5ffffe8ef9be2d0__cr.es:18b90548041f7f87@gw.dataimpulse.com:10000'
            }
            
            # CRITICAL: Use session cookies from registration page!
            # The captcha_data parameter is tied to the specific session cookies
            if cookies:
                cookie_parts = []
                for key, value in cookies.items():
                    cookie_parts.append(f"{key}={value}")
                if cookie_parts:
                    session.headers['Cookie'] = "; ".join(cookie_parts)
                    logger.info(f"🍪 Using session cookies: {session.headers['Cookie'][:100]}...")
            else:
                logger.info("⚠️ No session cookies provided - captcha_data might be invalid!")
            
            # Step 1: Make initial request with dynamic URL
            logger.info(f"🌐 Using dynamic captcha URL: {page_url}")
            response = session.get(page_url, timeout=30)
            logger.info(f"📡 Initial response: {response.status_code}")
            
            # Step 2: Check if we got a WAF challenge (same as test script)
            if ('gokuProps' in response.text and 'challenge.js' in response.text) or response.status_code in [202, 403]:
                logger.info("🔍 AWS WAF challenge detected!")
                
                # Step 3: Extract challenge data (same as test script)
                extract_result = AwsWaf.extract(response.text)
                if isinstance(extract_result, tuple) and len(extract_result) == 2:
                    goku_props, host = extract_result
                elif isinstance(extract_result, dict) and 'key' in extract_result and 'host' in extract_result:
                    goku_props = {'key': extract_result['key'], 'iv': extract_result.get('iv'), 'context': extract_result.get('context')}
                    host = extract_result['host']
                else:
                    logger.warning(f"⚠️ Unexpected AwsWaf.extract() result format: {extract_result}")
                    return None
                
                # Step 4: Solve challenge (same as test script)
                logger.info("🔄 Solving AWS WAF challenge...")
                start = time.time()
                token = AwsWaf(goku_props, host, "algeria.blsspainglobal.com")()
                end = time.time()
                logger.info(f"✅ Challenge solved in {end - start:.2f} seconds!")
                
                # Step 5: Make NEW request with token (same as test script)
                logger.info(f"🔑 Generated AWS WAF token: {token[:20]}...")
                
                logger.info("🌐 Testing with token...")
                # CRITICAL: Set the WAF token as a proper cookie in the session
                session.cookies.set("aws-waf-token", token)
                
                # DEBUG: Check cookies after setting WAF token
                logger.info(f"🔍 DEBUG - Cookies after setting WAF token: {session.cookies.get_dict()}")
                
                solved_response = session.get(page_url, timeout=30)
                logger.info(f"📡 Solved response: {solved_response.status_code}")
                logger.info(f"📄 Solved content length: {len(solved_response.text)}")
                logger.info(f"🔍 DEBUG - Response headers: {dict(solved_response.headers)}")
                logger.info(f"🔍 DEBUG - Response text preview: {solved_response.text[:200]}...")
                
                # DEBUG: Check response conditions
                logger.info(f"🔍 DEBUG - Status code check: {solved_response.status_code == 200}")
                logger.info(f"🔍 DEBUG - Content length check: {len(solved_response.text) > 100}")
                logger.info(f"🔍 DEBUG - Both conditions met: {solved_response.status_code == 200 and len(solved_response.text) > 100}")
                
                if solved_response.status_code == 200 and len(solved_response.text) > 100:
                    logger.info(f"✅ Retrieved captcha page content: {len(solved_response.text)} characters")
                    logger.info(f"🔍 Captcha content preview: {solved_response.text[:500]}...")
                    
                    # Extract cookies from the curl_cffi session
                    session_cookies = {}
                    
                    # DEBUG: Check session and cookies attributes
                    logger.info(f"🔍 DEBUG - Session type: {type(session)}")
                    logger.info(f"🔍 DEBUG - Has cookies attr: {hasattr(session, 'cookies')}")
                    
                    if hasattr(session, 'cookies'):
                        logger.info(f"🔍 DEBUG - Cookies type: {type(session.cookies)}")
                        logger.info(f"🔍 DEBUG - Cookies dir: {dir(session.cookies)}")
                        logger.info(f"🔍 DEBUG - Has get_dict method: {hasattr(session.cookies, 'get_dict')}")
                        
                        # Method 1: Use curl_cffi's get_dict() method (recommended by docs)
                        if hasattr(session.cookies, 'get_dict'):
                            try:
                                session_cookies = session.cookies.get_dict()
                                logger.info(f"🔍 DEBUG - Cookies from get_dict(): {session_cookies}")
                            except Exception as e:
                                logger.error(f"❌ Error calling get_dict(): {e}")
                        
                        # Method 2: Fallback to manual iteration
                        if not session_cookies:
                            logger.info("🔍 DEBUG - Trying manual cookie iteration...")
                            for cookie in session.cookies:
                                logger.info(f"🔍 DEBUG - Raw cookie: {cookie}")
                                logger.info(f"🔍 DEBUG - Cookie name: {getattr(cookie, 'name', 'NO_NAME')}")
                                logger.info(f"🔍 DEBUG - Cookie value: {getattr(cookie, 'value', 'NO_VALUE')}")
                                
                                # Filter out cookie attributes (path, samesite, etc.)
                                cookie_name = getattr(cookie, 'name', None)
                                cookie_value = getattr(cookie, 'value', None)
                                
                                if cookie_name and cookie_value and cookie_name not in ['path', 'samesite', 'domain', 'expires', 'max-age', 'secure', 'httponly']:
                                    session_cookies[cookie_name] = cookie_value
                                    logger.info(f"🔍 DEBUG - Added cookie: {cookie_name} = {cookie_value[:50]}...")
                    
                    # Method 3: Check response headers for Set-Cookie
                    if hasattr(solved_response, 'headers'):
                        set_cookie_headers = solved_response.headers.get('Set-Cookie', '')
                        if set_cookie_headers:
                            logger.info(f"🔍 DEBUG - Set-Cookie headers: {set_cookie_headers}")
                    
                    logger.info(f"🔍 DEBUG - Final session cookies from captcha page: {session_cookies}")
                    return solved_response.text, session_cookies
                else:
                    logger.warning(f"⚠️ Captcha response failed: status={solved_response.status_code}, length={len(solved_response.text)}")
                    return None, {}
                    
            elif response.status_code == 200 and len(response.text) > 100:
                logger.info("✅ Already have captcha page (no challenge needed)!")
                
                # Extract cookies from the curl_cffi session
                session_cookies = {}
                
                # DEBUG: Check session and cookies attributes
                logger.info(f"🔍 DEBUG - Session type (no challenge): {type(session)}")
                logger.info(f"🔍 DEBUG - Has cookies attr (no challenge): {hasattr(session, 'cookies')}")
                
                if hasattr(session, 'cookies'):
                    logger.info(f"🔍 DEBUG - Cookies type (no challenge): {type(session.cookies)}")
                    logger.info(f"🔍 DEBUG - Cookies dir (no challenge): {dir(session.cookies)}")
                    logger.info(f"🔍 DEBUG - Has get_dict method (no challenge): {hasattr(session.cookies, 'get_dict')}")
                    
                    # Method 1: Use curl_cffi's get_dict() method (recommended by docs)
                    if hasattr(session.cookies, 'get_dict'):
                        try:
                            session_cookies = session.cookies.get_dict()
                            logger.info(f"🔍 DEBUG - Cookies from get_dict() (no challenge): {session_cookies}")
                        except Exception as e:
                            logger.error(f"❌ Error calling get_dict() (no challenge): {e}")
                    
                    # Method 2: Fallback to manual iteration
                    if not session_cookies:
                        logger.info("🔍 DEBUG - Trying manual cookie iteration (no challenge)...")
                        for cookie in session.cookies:
                            logger.info(f"🔍 DEBUG - Raw cookie (no challenge): {cookie}")
                            logger.info(f"🔍 DEBUG - Cookie name (no challenge): {getattr(cookie, 'name', 'NO_NAME')}")
                            logger.info(f"🔍 DEBUG - Cookie value (no challenge): {getattr(cookie, 'value', 'NO_VALUE')}")
                            
                            # Filter out cookie attributes (path, samesite, etc.)
                            cookie_name = getattr(cookie, 'name', None)
                            cookie_value = getattr(cookie, 'value', None)
                            
                            if cookie_name and cookie_value and cookie_name not in ['path', 'samesite', 'domain', 'expires', 'max-age', 'secure', 'httponly']:
                                session_cookies[cookie_name] = cookie_value
                                logger.info(f"🔍 DEBUG - Added cookie (no challenge): {cookie_name} = {cookie_value[:50]}...")
                
                # Method 3: Check response headers for Set-Cookie
                if hasattr(response, 'headers'):
                    set_cookie_headers = response.headers.get('Set-Cookie', '')
                    if set_cookie_headers:
                        logger.info(f"🔍 DEBUG - Set-Cookie headers (no challenge): {set_cookie_headers}")
                
                logger.info(f"🔍 DEBUG - Final session cookies from captcha page (no challenge): {session_cookies}")
                return response.text, session_cookies
            else:
                logger.warning(f"⚠️ Unexpected response: status={response.status_code}, length={len(response.text)}")
                return None, {}
            
            # Fallback: Use the comprehensive WAF bypass handler for captcha requests
            from .waf_bypass import WAFBypassHandler
            from urllib.parse import urlparse
            
            # Extract the path and query parameters from the captcha URL
            parsed_url = urlparse(page_url)
            captcha_path = parsed_url.path
            if parsed_url.query:
                captcha_path += f"?{parsed_url.query}"
            
            # Prepare headers with session cookies (but let WAF bypass generate fresh WAF token)
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'es-ES,es;q=0.9',  # Spanish like the browser request
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
            
            # Add session cookies from registration page (but NOT the old WAF token)
            cookie_parts = []
            
            # Add visitor ID cookie
            cookie_parts.append(f"visitorId_current={self.visitor_id}")
            
            # Add antiforgery token from registration page if available
            if form_data and '__RequestVerificationToken' in form_data:
                antiforgery_token = form_data['__RequestVerificationToken']
                cookie_parts.append(f".AspNetCore.Antiforgery.cyS7zUT4rj8={antiforgery_token}")
                logger.info(f"🔑 Using antiforgery token for captcha WAF bypass")
            
            if cookie_parts:
                headers['Cookie'] = "; ".join(cookie_parts)
                logger.info(f"🍪 Cookie header for WAF bypass: {headers['Cookie'][:100]}...")
            
            # Use WAF bypass handler for captcha page
            waf_handler = WAFBypassHandler("https://algeria.blsspainglobal.com", captcha_path, self.visitor_id)
            
            # Note: We don't try direct request with old WAF token because captcha page needs its own fresh WAF token
            logger.info("🔄 Skipping direct request - captcha page needs fresh WAF token from its own bypass")
            
            bypass_result = await waf_handler.try_comprehensive_bypass(proxy_url, headers)
            
            if bypass_result and bypass_result.get('success'):
                logger.info("✅ Comprehensive WAF bypass successful for captcha URL!")
                bypass_content = bypass_result.get('content', '')
                if bypass_content and len(bypass_content) > 100:
                    logger.info(f"✅ Retrieved captcha page content: {len(bypass_content)} characters")
                    logger.info(f"🔍 Captcha content preview: {bypass_content[:500]}...")
                    # For fallback, we don't have fresh cookies, so return empty dict
                    return bypass_content, {}
                else:
                    logger.warning("⚠️ Bypass content too short or empty")
            else:
                logger.warning("⚠️ Comprehensive WAF bypass failed for captcha URL")
                
        except Exception as e:
            logger.error(f"❌ Error in comprehensive WAF bypass for captcha: {e}")
        
        # Fallback: try direct request with retry logic
        logger.info("🔄 Falling back to direct request with retry logic...")
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Attempt {attempt + 1}/{max_retries} to get captcha page content")
                
                # Prepare headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                # Prepare session cookies
                session_cookies = cookies.copy() if cookies else {}
                
                # Make request with aiohttp
                async with aiohttp.ClientSession(cookies=session_cookies) as session:
                    async with session.get(page_url, headers=headers, proxy=proxy_url, timeout=30) as response:
                        logger.info(f"📡 Captcha response status: {response.status}")
                        
                        if response.status == 200:
                            content = await response.text()
                            logger.info(f"✅ Successfully retrieved captcha page content: {len(content)} characters")
                            # For fallback, we don't have fresh cookies, so return empty dict
                            return content, {}
                        elif response.status == 202:
                            logger.info("🔍 AWS WAF challenge detected on captcha URL!")
                            challenge_content = await response.text()
                            logger.info(f"🔍 Challenge content length: {len(challenge_content)}")
                            
                            # Try to solve the WAF challenge
                            try:
                                import re
                                import json
                                
                                # Look for AWS WAF challenge patterns
                                goku_props_patterns = [
                                    r'window\.gokuProps\s*=\s*({.*?});',
                                    r'window\.gokuProps\s*=\s*({.*?})',
                                    r'goku_props\s*=\s*({.*?});',
                                    r'"goku_props"\s*:\s*({.*?})',
                                    r'window\.goku_props\s*=\s*({.*?});'
                                ]
                                
                                goku_match = None
                                for pattern in goku_props_patterns:
                                    goku_match = re.search(pattern, challenge_content, re.DOTALL)
                                    if goku_match:
                                        logger.info(f"🔍 Found WAF challenge with pattern: {pattern[:30]}...")
                                        break
                                
                                if goku_match:
                                    goku_props = json.loads(goku_match.group(1))
                                    logger.info(f"🔍 Extracted goku_props: {type(goku_props)}")
                                    
                                    # Solve the WAF challenge
                                    from awswaf.aws import AwsWaf
                                    
                                    # Extract host from the challenge content
                                    host_pattern = r'([a-f0-9]+\.5feecc1e\.eu-central-1\.token\.awswaf\.com/[^/]+/[^/]+/[^/]+)'
                                    host_match = re.search(host_pattern, challenge_content)
                                    host = host_match.group(1) if host_match else "5f2749aa43d4.5feecc1e.eu-central-1.token.awswaf.com/5f2749aa43d4/4bc7b7b893fe/fcc234ea0ef6"
                                    
                                    # Solve the challenge using AwsWaf
                                    solved_token = AwsWaf(goku_props, host, "algeria.blsspainglobal.com")()
                                    
                                    if solved_token:
                                        logger.info(f"✅ Solved captcha WAF challenge: {solved_token[:20]}...")
                                        
                                        # Retry the captcha request with the solved token
                                        new_headers = headers.copy()
                                        clean_token = solved_token.rstrip(':')
                                        new_headers['Cookie'] = f"aws-waf-token={clean_token}"
                                        
                                        async with session.get(page_url, headers=new_headers, proxy=proxy_url, timeout=30) as retry_response:
                                            if retry_response.status == 200:
                                                content = await retry_response.text()
                                                logger.info(f"✅ Successfully retrieved captcha page content after WAF bypass: {len(content)} characters")
                                                # For fallback, we don't have fresh cookies, so return empty dict
                                                return content, {}
                                            else:
                                                logger.warning(f"⚠️ Retry failed with status: {retry_response.status}")
                                    else:
                                        logger.warning("⚠️ Failed to solve captcha WAF challenge")
                                else:
                                    logger.warning("⚠️ No WAF challenge data found in captcha response")
                                    
                            except Exception as e:
                                logger.error(f"❌ Error solving captcha WAF challenge: {e}")
                        else:
                            logger.warning(f"⚠️ Unexpected response status: {response.status}")
                        
                        # If we reach here, the attempt failed
                        if attempt < max_retries - 1:
                            logger.info(f"⏳ Waiting 2 seconds before retry attempt {attempt + 2}...")
                            await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"❌ Error in attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Waiting 2 seconds before retry attempt {attempt + 2}...")
                    await asyncio.sleep(2)
        
        logger.error(f"❌ Failed to get captcha page content after {max_retries} attempts")
        return "", {}
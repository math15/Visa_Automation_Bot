"""
WAF Bypass Module for BLS Account Creation
Handles AWS WAF bypass techniques and proxy management
"""

import asyncio
import aiohttp
import time
import random
import secrets
from typing import Optional, Dict, Any
from loguru import logger


class WAFBypassHandler:
    """Handles AWS WAF bypass techniques for BLS website"""
    
    def __init__(self, base_url: str, register_url: str, visitor_id: str):
        self.base_url = base_url
        self.register_url = register_url
        self.visitor_id = visitor_id
    
    async def try_comprehensive_bypass(self, proxy_url: str, headers: dict) -> Optional[Dict[str, Any]]:
        """Try comprehensive WAF bypass approaches with retry logic"""
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Attempt {attempt + 1}/{max_retries} - Attempting comprehensive WAF bypass...")
                
                # Try multiple bypass techniques
                bypass_techniques = [
                    self._try_aws_waf_bypass,
                    self._try_direct_bypass,  # Try direct bypass earlier
                    self._try_tesla_waf_bypass
                ]
                
                for technique in bypass_techniques:
                    try:
                        result = await technique(proxy_url, headers)
                        if result:
                            logger.info("✅ WAF bypass successful!")
                            extracted_result = self._extract_result_data(result)
                            # Check if we got valid content
                            if extracted_result and extracted_result.get('success') and len(extracted_result.get('content', '')) > 100:
                                return extracted_result
                            else:
                                logger.warning("⚠️ Bypass succeeded but returned invalid content, trying next technique...")
                                continue
                    except Exception as e:
                        logger.warning(f"⚠️ Bypass technique failed: {e}")
                        continue
                
                # Try direct fallback if all techniques failed
                logger.warning("⚠️ All bypass techniques failed, trying direct approach")
                fallback_result = await self._try_direct_fallback(proxy_url, headers)
                if fallback_result and fallback_result.get('success') and len(fallback_result.get('content', '')) > 100:
                    return fallback_result
                
                # If all techniques failed in this attempt, wait before retry
                if attempt < max_retries - 1:
                    logger.info(f"⏳ All techniques failed in attempt {attempt + 1}, waiting 3 seconds before retry...")
                    await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Error in attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(3)
        
        logger.error(f"❌ All WAF bypass attempts failed after {max_retries} tries")
        return None
    
    def _extract_result_data(self, result: str) -> Dict[str, Any]:
        """Extract AWS WAF token, content, and cookies from result"""
        aws_waf_token = None
        content = result
        session_cookies = {}
        
        if isinstance(result, str):
            # Check if result contains aws-waf-token format
            if "aws-waf-token=" in result:
                import re
                token_match = re.search(r'aws-waf-token=([a-f0-9-:]+)', result)
                if token_match:
                    aws_waf_token = token_match.group(1)
                    logger.info(f"🔑 Extracted AWS WAF token: {aws_waf_token[:20]}...")
                
                # Extract cookies if present
                if "COOKIES=" in result:
                    cookies_match = re.search(r'COOKIES=([^\n]*)', result)
                    if cookies_match:
                        cookies_str = cookies_match.group(1)
                        if cookies_str:
                            # Parse cookies string
                            for cookie_pair in cookies_str.split(';'):
                                if '=' in cookie_pair:
                                    name, value = cookie_pair.split('=', 1)
                                    session_cookies[name.strip()] = value.strip()
                            logger.info(f"🍪 Extracted session cookies: {len(session_cookies)} cookies")
                
                # Extract content (everything between token and SESSION/COOKIES)
                lines = result.split('\n')
                content_lines = []
                in_content = False
                for line in lines:
                    if line.startswith('aws-waf-token='):
                        in_content = True
                        continue
                    elif line.startswith('SESSION=') or line.startswith('COOKIES='):
                        break
                    elif in_content:
                        content_lines.append(line)
                
                content = '\n'.join(content_lines)
                logger.info(f"📄 Extracted HTML content length: {len(content)}")
            else:
                # Direct content format - check if it's valid HTML content
                if len(result) > 100 and ('<html' in result.lower() or '<!doctype' in result.lower()):
                    logger.info(f"📄 Using direct content: {len(result)} characters")
                    content = result
                else:
                    logger.warning(f"⚠️ Invalid content format: {len(result)} characters")
                    content = ""
        
        return {
            "success": len(content) > 100,
            "content": content,
            "waf_token": aws_waf_token,
            "cookies": session_cookies
        }
    
    async def _try_aws_waf_bypass(self, proxy_url: str, headers: dict) -> Optional[str]:
        """Try AWS WAF bypass using awswaf project"""
        try:
            logger.info("🔄 Attempting AWS WAF bypass with direct implementation...")
            
            # Import awswaf directly
            import sys
            import os
            import time
            awswaf_path = os.path.join(os.path.dirname(__file__), '..', '..', 'awswaf', 'python')
            
            if not os.path.exists(awswaf_path):
                logger.error(f"❌ AWS WAF path does not exist: {awswaf_path}")
                return None
            
            sys.path.insert(0, awswaf_path)
            
            from awswaf.aws import AwsWaf
            from curl_cffi import requests
            
            # Create session with proper headers
            session = requests.Session(impersonate="chrome")
            session.headers.update({
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'ar-DZ,ar;q=0.9,en;q=0.8',
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
                'X-Forwarded-For': '41.200.0.1',
                'X-Real-IP': '41.200.0.1',
                'X-Client-IP': '41.200.0.1',
                'CF-IPCountry': 'DZ',
            })
            
            # Use working proxy configuration (same as successful registration page approach)
            session.proxies = {
                'http': 'http://7929b5ffffe8ef9be2d0__cr.es:18b90548041f7f87@gw.dataimpulse.com:10000',
                'https': 'http://7929b5ffffe8ef9be2d0__cr.es:18b90548041f7f87@gw.dataimpulse.com:10000'
            }
            logger.info("🌐 Using working proxy configuration")
            
            # Use the URL this handler was initialized with
            target_url = f"{self.base_url}{self.register_url}"
            logger.info(f"🌐 Getting BLS page: {target_url}")
            logger.info(f"🌐 Base URL: {self.base_url}")
            logger.info(f"🌐 Register URL: {self.register_url}")
            
            # Use longer timeout for captcha pages
            timeout_seconds = 30 if '/CaptchaPublic/' in target_url or 'GenerateCaptcha' in target_url else 15
            response = session.get(target_url, timeout=timeout_seconds)
            logger.info(f"📡 BLS response: {response.status_code}")
            
            # If we get 403, try different approaches
            if response.status_code == 403:
                logger.warning("⚠️ Got 403, trying different approaches...")
                
                # Try 1: Without proxy but with different headers
                try:
                    logger.info("🔄 Trying without proxy with different headers...")
                    fallback_session = requests.Session(impersonate="chrome")
                    # Use more realistic headers
                    fallback_session.headers.update({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                    })
                    fallback_response = fallback_session.get(target_url, timeout=15)
                    logger.info(f"📡 Fallback response: {fallback_response.status_code}")
                    
                    if fallback_response.status_code in [200, 202] and ('gokuProps' in fallback_response.text or 'challenge.js' in fallback_response.text):
                        logger.info("✅ Fallback request successful, using fallback response")
                        response = fallback_response
                    else:
                        logger.warning(f"⚠️ Fallback also failed: {fallback_response.status_code}")
                        
                        # Try 2: With different user agent
                        logger.info("🔄 Trying with different user agent...")
                        fallback_session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                        fallback_response2 = fallback_session.get(target_url, timeout=15)
                        logger.info(f"📡 Fallback response 2: {fallback_response2.status_code}")
                        
                        if fallback_response2.status_code in [200, 202] and ('gokuProps' in fallback_response2.text or 'challenge.js' in fallback_response2.text):
                            logger.info("✅ Fallback request 2 successful, using fallback response")
                            response = fallback_response2
                        else:
                            logger.warning(f"⚠️ All fallback attempts failed")
                            
                except Exception as e:
                    logger.warning(f"⚠️ Fallback request failed: {e}")
            
            if ('gokuProps' in response.text and 'challenge.js' in response.text) or response.status_code in [202, 403]:
                logger.info("🔍 AWS WAF challenge detected!")
                
                try:
                    # Handle different return formats from AwsWaf.extract()
                    extract_result = AwsWaf.extract(response.text)
                    logger.info(f"🔍 AWS WAF extract result type: {type(extract_result)}")
                    logger.info(f"🔍 AWS WAF extract result: {extract_result}")
                    
                    if isinstance(extract_result, (list, tuple)) and len(extract_result) >= 2:
                        goku_props, host = extract_result[0], extract_result[1]
                        logger.info(f"✅ Extracted goku_props: {type(goku_props)}, host: {host}")
                    elif isinstance(extract_result, dict):
                        goku_props = extract_result.get('goku_props', extract_result.get('props'))
                        host = extract_result.get('host', 'algeria.blsspainglobal.com')
                        logger.info(f"✅ Extracted from dict - goku_props: {type(goku_props)}, host: {host}")
                    else:
                        logger.warning(f"⚠️ Unexpected extract result format: {extract_result}")
                        return None
                        
                    if not goku_props:
                        logger.warning("⚠️ No goku_props found in extraction result")
                        return None
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract AWS WAF challenge data: {e}")
                    logger.warning(f"⚠️ Response text preview: {response.text[:500]}...")
                    return None
                
                logger.info("🔄 Solving AWS WAF challenge...")
                start = time.time()
                
                try:
                    token = AwsWaf(goku_props, host, "algeria.blsspainglobal.com")()
                    logger.info(f"🔑 Generated AWS WAF token: {token[:20]}...")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to solve AWS WAF challenge: {e}")
                    # Try without proxy as fallback
                    if proxy_url:
                        logger.info("🔄 Trying AWS WAF bypass without proxy as fallback...")
                        try:
                            # Create new session without proxy
                            fallback_session = requests.Session(impersonate="chrome")
                            fallback_session.headers.update(session.headers)
                            
                            fallback_response = fallback_session.get(target_url, timeout=15)
                            if fallback_response.status_code in [202, 403]:
                                try:
                                    fallback_extract_result = AwsWaf.extract(fallback_response.text)
                                    if isinstance(fallback_extract_result, (list, tuple)) and len(fallback_extract_result) >= 2:
                                        fallback_goku_props, fallback_host = fallback_extract_result[0], fallback_extract_result[1]
                                        token = AwsWaf(fallback_goku_props, fallback_host, "algeria.blsspainglobal.com")()
                                        logger.info(f"🔑 Generated AWS WAF token without proxy: {token[:20]}...")
                                    else:
                                        logger.warning("⚠️ Fallback extraction also failed")
                                        return None
                                except Exception as fallback_e:
                                    logger.warning(f"⚠️ Fallback AWS WAF bypass failed: {fallback_e}")
                                    return None
                            else:
                                logger.warning(f"⚠️ Fallback request status: {fallback_response.status_code}")
                                return None
                        except Exception as fallback_e:
                            logger.warning(f"⚠️ Fallback session creation failed: {fallback_e}")
                            return None
                    else:
                        return None
                
                end = time.time()
                logger.info(f"✅ Challenge solved in {end - start:.2f} seconds!")
                
                # Return the token and content from the WAF challenge response
                clean_token = token.rstrip(':')
                logger.info(f"🔑 Generated AWS WAF token: {clean_token[:20]}...")
                
                # Test with token (make a NEW request with the token)
                logger.info("🌐 Testing with token...")
                session.headers.update({
                    "cookie": "aws-waf-token=" + clean_token
                })
                
                # Detect if this is a captcha page
                is_captcha_page = '/CaptchaPublic/' in self.register_url or 'GenerateCaptcha' in self.register_url
                
                solved_response = session.get(target_url, timeout=timeout_seconds)
                logger.info(f"📡 Solved response: {solved_response.status_code}")
                logger.info(f"📡 Solved response content length: {len(solved_response.text)}")
                logger.info(f"📡 Solved response headers: {dict(solved_response.headers)}")
                
                # Extract session cookies from response
                session_cookies = {}
                if 'set-cookie' in solved_response.headers:
                    cookie_header = solved_response.headers['set-cookie']
                    logger.info(f"🍪 Extracted set-cookie header: {cookie_header[:100]}...")
                    
                    # Parse cookies from set-cookie header
                    import re
                    cookie_pattern = r'([^=]+)=([^;]+)'
                    cookies = re.findall(cookie_pattern, cookie_header)
                    for name, value in cookies:
                        session_cookies[name] = value
                        logger.info(f"🍪 Parsed cookie: {name}={value[:20]}...")
                
                # Save captcha page response for debugging
                if is_captcha_page:
                    debug_file = f"debug_captcha_response_{int(time.time())}.html"
                    try:
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(f"<!-- Status: {solved_response.status_code} -->\n")
                            f.write(f"<!-- Headers: {dict(solved_response.headers)} -->\n")
                            f.write(f"<!-- Content Length: {len(solved_response.text)} -->\n")
                            f.write(solved_response.text)
                        logger.info(f"💾 Saved captcha response to {debug_file}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not save captcha response: {e}")
                
                # Note: Removed AJAX wait and follow-up request since test script works without it
                # The issue was that follow-up requests were returning empty content
                
                # Check for actual registration form - be more lenient for captcha pages
                has_form = 'FirstName' in solved_response.text or 'LastName' in solved_response.text
                has_captcha = 'CaptchaId' in solved_response.text or 'captcha' in solved_response.text.lower()
                has_tokens = 'RequestVerificationToken' in solved_response.text
                has_html = '<html' in solved_response.text.lower() or '<!doctype' in solved_response.text.lower()
                has_content = len(solved_response.text) > 100
                
                # Additional validation for captcha pages (already detected above)
                has_captcha_images = 'img' in solved_response.text.lower() and ('id=' in solved_response.text.lower() or 'captcha' in solved_response.text.lower())
                has_captcha_form = 'captcha' in solved_response.text.lower() and 'form' in solved_response.text.lower()
                
                logger.info(f"🔍 Content validation: has_form={has_form}, has_captcha={has_captcha}, has_tokens={has_tokens}, has_html={has_html}, has_content={has_content}")
                logger.info(f"🔍 Captcha page validation: is_captcha_page={is_captcha_page}, has_captcha_images={has_captcha_images}, has_captcha_form={has_captcha_form}")
                logger.info(f"🔍 Response length: {len(solved_response.text)}")
                logger.info(f"🔍 Content preview: {solved_response.text[:200]}...")
                
                # Accept content if it has any of these indicators OR if it's substantial HTML content
                # For captcha pages, also accept if it has captcha-related content
                # REJECT empty content even for captcha pages - we need actual content
                if (has_form or has_captcha or has_tokens or (has_html and has_content) or 
                    (is_captcha_page and (has_captcha_images or has_captcha_form or has_html))):
                    logger.info("✅ Successfully retrieved actual BLS page content!")
                    # Include session cookies in the return string
                    cookies_str = ";".join([f"{k}={v}" for k, v in session_cookies.items()]) if session_cookies else ""
                    return f"aws-waf-token={clean_token}\n{solved_response.text}\nSESSION={session}\nCOOKIES={cookies_str}"
                else:
                    logger.warning("⚠️ No valid page content found - rejecting empty content")
                    # Save the response for debugging
                    try:
                        import os
                        debug_file = "debug_waf_bypass_response.html"
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(solved_response.text)
                        logger.info(f"💾 Saved WAF bypass response to {debug_file} for debugging")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not save WAF bypass response: {e}")
                    return None
                
            elif response.status_code == 200 and ('FirstName' in response.text or 'LastName' in response.text):
                logger.info("✅ Already have registration page (no challenge needed)!")
                return response.text
            else:
                logger.warning("⚠️ No AWS WAF challenge detected")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ AWS WAF bypass error: {e}")
            return None
    
    async def _try_tesla_waf_bypass(self, proxy_url: str, headers: dict) -> Optional[str]:
        """Try Tesla 2.0 comprehensive WAF bypass techniques"""
        try:
            logger.info("🔄 Attempting Tesla 2.0 WAF bypass...")
            
            bypass_methods = [
                self._try_url_bypass,
                self._try_args_bypass,
                self._try_header_bypass,
                self._try_cookie_bypass
            ]
            
            for method in bypass_methods:
                try:
                    result = await method(proxy_url, headers)
                    if result:
                        logger.info(f"✅ Tesla bypass successful with {method.__name__}!")
                        return result
                except Exception as e:
                    logger.warning(f"⚠️ {method.__name__} failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Tesla WAF bypass error: {e}")
            return None
    
    async def _try_direct_bypass(self, proxy_url: str, headers: dict) -> Optional[str]:
        """Try direct bypass with enhanced headers"""
        try:
            logger.info("🔄 Attempting direct bypass...")
            
            enhanced_headers = headers.copy()
            enhanced_headers.update({
                'X-Forwarded-Proto': 'https',
                'X-Forwarded-Host': 'algeria.blsspainglobal.com',
                'X-Original-URL': '/dza/account/RegisterUser',
                'X-Rewrite-URL': '/dza/account/RegisterUser',
                'X-Real-IP': '41.200.0.1',
                'X-Client-IP': '41.200.0.1',
                'X-Cluster-Client-IP': '41.200.0.1',
                'X-Forwarded-For': '41.200.0.1',
            })
            
            # Prepare proxy configuration for aiohttp
            proxy_config = None
            if proxy_url:
                if not proxy_url.startswith('http://'):
                    proxy_url = f"http://{proxy_url}"
                proxy_config = proxy_url
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}{self.register_url}",
                    proxy=proxy_config,
                    headers=enhanced_headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    logger.info(f"📡 Direct bypass response: {response.status}")
                    content = await response.text()
                    
                    # Check if this is a WAF challenge
                    if response.status == 202 and ('gokuProps' in content or 'challenge.js' in content):
                        logger.info("🔍 Direct bypass returned WAF challenge, not solving it")
                        return None
                    
                    # For captcha pages, accept smaller content
                    is_captcha_page = '/CaptchaPublic/' in self.register_url or 'GenerateCaptcha' in self.register_url
                    min_content_length = 500 if is_captcha_page else 1000
                    
                    if response.status == 200 and len(content) > min_content_length:
                        logger.info("✅ Direct bypass successful!")
                        return content
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Direct bypass error: {e}")
            return None
    
    async def _try_url_bypass(self, proxy_url: str, headers: dict) -> Optional[str]:
        """Try URL-based WAF bypass"""
        try:
            url_patterns = [
                f"{self.base_url}{self.register_url}",
                f"{self.base_url}{self.register_url}?v=1",
                f"{self.base_url}{self.register_url}?t={int(time.time())}",
                f"{self.base_url}{self.register_url}?r={random.randint(1000, 9999)}",
                f"{self.base_url}{self.register_url}?sid=algeria",
                f"{self.base_url}{self.register_url}?country=DZ",
            ]
            
            for url in url_patterns:
                try:
                    # Prepare proxy configuration for aiohttp
                    proxy_config = None
                    if proxy_url:
                        if not proxy_url.startswith('http://'):
                            proxy_url = f"http://{proxy_url}"
                        proxy_config = proxy_url
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            url,
                            proxy=proxy_config,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=15)
                        ) as response:
                            content = await response.text()
                            # Check if this is a WAF challenge first
                            if response.status == 202 and ('gokuProps' in content or 'challenge.js' in content):
                                logger.info(f"🔍 URL bypass returned WAF challenge: {url}")
                                continue
                            
                            # For captcha pages, accept smaller content
                            is_captcha_page = '/CaptchaPublic/' in self.register_url or 'GenerateCaptcha' in self.register_url
                            min_content_length = 500 if is_captcha_page else 1000
                            if response.status == 200 and len(content) > min_content_length:
                                logger.info(f"✅ URL bypass successful: {url}")
                                return content
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ URL bypass error: {e}")
            return None
    
    async def _try_args_bypass(self, proxy_url: str, headers: dict) -> Optional[str]:
        """Try query arguments WAF bypass"""
        try:
            params_list = [
                {f"param{secrets.token_hex(3)}": "algeria"},
                {"sid": "algeria", "country": "DZ"},
                {"lang": "ar", "timezone": "Africa/Algiers"},
                {"v": "1", "t": str(int(time.time()))},
            ]
            
            for params in params_list:
                try:
                    # Prepare proxy configuration for aiohttp
                    proxy_config = None
                    if proxy_url:
                        if not proxy_url.startswith('http://'):
                            proxy_url = f"http://{proxy_url}"
                        proxy_config = proxy_url
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{self.base_url}{self.register_url}",
                            proxy=proxy_config,
                            headers=headers,
                            params=params,
                            timeout=aiohttp.ClientTimeout(total=15)
                        ) as response:
                            content = await response.text()
                            # For captcha pages, accept smaller content
                            is_captcha_page = '/CaptchaPublic/' in self.register_url or 'GenerateCaptcha' in self.register_url
                            min_content_length = 500 if is_captcha_page else 1000
                            # Check if this is a WAF challenge first
                            if response.status == 202 and ('gokuProps' in content or 'challenge.js' in content):
                                logger.info(f"🔍 Args bypass returned WAF challenge")
                                continue
                            
                            if response.status == 200 and len(content) > min_content_length:
                                # Check if this is an AWS WAF challenge instead of the actual page
                                if 'gokuProps' in content and 'challenge.js' in content:
                                    logger.info(f"🔍 ARGS bypass returned AWS WAF challenge: {params}")
                                    continue  # Try next params
                                logger.info(f"✅ ARGS bypass successful: {params}")
                                return content
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ ARGS bypass error: {e}")
            return None
    
    async def _try_header_bypass(self, proxy_url: str, headers: dict) -> Optional[str]:
        """Try header-based WAF bypass"""
        try:
            header_variations = [
                {**headers, f"WBH-{secrets.token_hex(3)}": "algeria"},
                {**headers, "X-Country": "DZ", "X-Language": "ar"},
                {**headers, "X-Timezone": "Africa/Algiers", "X-Region": "North Africa"},
                {**headers, "X-Session": "algeria", "X-Client": "bls"},
            ]
            
            for header_set in header_variations:
                try:
                    # Prepare proxy configuration for aiohttp
                    proxy_config = None
                    if proxy_url:
                        if not proxy_url.startswith('http://'):
                            proxy_url = f"http://{proxy_url}"
                        proxy_config = proxy_url
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{self.base_url}{self.register_url}",
                            proxy=proxy_config,
                            headers=header_set,
                            timeout=aiohttp.ClientTimeout(total=15)
                        ) as response:
                            content = await response.text()
                            # For captcha pages, accept smaller content
                            is_captcha_page = '/CaptchaPublic/' in self.register_url or 'GenerateCaptcha' in self.register_url
                            min_content_length = 500 if is_captcha_page else 1000
                            # Check if this is a WAF challenge first
                            if response.status == 202 and ('gokuProps' in content or 'challenge.js' in content):
                                logger.info(f"🔍 Args bypass returned WAF challenge")
                                continue
                            
                            if response.status == 200 and len(content) > min_content_length:
                                # Check if this is an AWS WAF challenge instead of the actual page
                                if 'gokuProps' in content and 'challenge.js' in content:
                                    logger.info(f"🔍 HEADER bypass returned AWS WAF challenge")
                                    continue  # Try next header set
                                logger.info(f"✅ HEADER bypass successful")
                                return content
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ HEADER bypass error: {e}")
            return None
    
    async def _try_cookie_bypass(self, proxy_url: str, headers: dict) -> Optional[str]:
        """Try cookie-based WAF bypass"""
        try:
            cookie_variations = [
                {f"WBC-{secrets.token_hex(3)}": "algeria"},
                {"sessionid": "algeria", "country": "DZ"},
                {"lang": "ar", "timezone": "Africa/Algiers"},
                {"sid": "algeria", "client": "bls"},
            ]
            
            for cookies in cookie_variations:
                try:
                    # Prepare proxy configuration for aiohttp
                    proxy_config = None
                    if proxy_url:
                        if not proxy_url.startswith('http://'):
                            proxy_url = f"http://{proxy_url}"
                        proxy_config = proxy_url
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{self.base_url}{self.register_url}",
                            proxy=proxy_config,
                            headers=headers,
                            cookies=cookies,
                            timeout=aiohttp.ClientTimeout(total=15)
                        ) as response:
                            content = await response.text()
                            # For captcha pages, accept smaller content
                            is_captcha_page = '/CaptchaPublic/' in self.register_url or 'GenerateCaptcha' in self.register_url
                            min_content_length = 500 if is_captcha_page else 1000
                            # Check if this is a WAF challenge first
                            if response.status == 202 and ('gokuProps' in content or 'challenge.js' in content):
                                logger.info(f"🔍 Args bypass returned WAF challenge")
                                continue
                            
                            if response.status == 200 and len(content) > min_content_length:
                                # Check if this is an AWS WAF challenge instead of the actual page
                                if 'gokuProps' in content and 'challenge.js' in content:
                                    logger.info(f"🔍 COOKIE bypass returned AWS WAF challenge")
                                    continue  # Try next cookies
                                logger.info(f"✅ COOKIE bypass successful")
                                return content
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ COOKIE bypass error: {e}")
            return None
    
    async def _try_direct_fallback(self, proxy_url: str, headers: dict) -> Optional[Dict[str, Any]]:
        """Try direct approach as fallback"""
        try:
            logger.info("🌐 Making direct request with Tesla 2.0 headers...")
            
            async with aiohttp.ClientSession() as session:
                # First try with proxy
                try:
                    # Prepare proxy configuration for aiohttp
                    proxy_config = None
                    if proxy_url:
                        if not proxy_url.startswith('http://'):
                            proxy_url = f"http://{proxy_url}"
                        proxy_config = proxy_url
                    
                    async with session.get(
                        f"{self.base_url}{self.register_url}",
                        proxy=proxy_config,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        logger.info(f"📡 Direct response with proxy: {response.status}")
                        content = await response.text()
                        
                        # Check if this is a WAF challenge first
                        if response.status == 202 and ('gokuProps' in content or 'challenge.js' in content):
                            logger.info(f"🔍 Proxy request returned WAF challenge")
                        elif response.status == 200 and len(content) > 1000:
                            logger.info("✅ Successfully retrieved BLS page with proxy!")
                            return {"content": content, "aws_waf_token": None}
                        else:
                            logger.warning(f"⚠️ Proxy request failed: {response.status}")
                            
                except Exception as e:
                    logger.warning(f"⚠️ Proxy request failed: {e}")
                
                # Fallback: try without proxy
                logger.info("🔄 Trying direct request without proxy...")
                try:
                    async with session.get(
                        f"{self.base_url}{self.register_url}",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        logger.info(f"📡 Direct response without proxy: {response.status}")
                        content = await response.text()
                        
                        # Check if this is a WAF challenge first
                        if response.status == 202 and ('gokuProps' in content or 'challenge.js' in content):
                            logger.info(f"🔍 Direct request returned WAF challenge")
                        elif response.status == 200 and len(content) > 1000:
                            logger.info("✅ Successfully retrieved BLS page without proxy!")
                            return {"content": content, "aws_waf_token": None}
                        else:
                            logger.error(f"❌ Failed to get registration page: {response.status}")
                            return None
                            
                except Exception as e:
                    logger.warning(f"⚠️ Direct request without proxy failed: {e}")
                    return None
                        
        except Exception as e:
            logger.error(f"❌ Error in direct fallback: {e}")
            return None

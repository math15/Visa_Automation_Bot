"""
Browser-based captcha solver for BLS
Uses Playwright with proxy support to solve captchas in a real browser
"""

from typing import Dict, List, Optional, Tuple
from loguru import logger
import asyncio
import re


class BrowserCaptchaSolver:
    """Solves BLS captchas using a real browser (Playwright) with proxy support"""
    
    def __init__(self, nocaptcha_api_key: str = None):
        self.nocaptcha_api_key = nocaptcha_api_key or "mayas94-e794b1ea-f6b5-582a-46c6-980f5c6cd7c3"
        self.browser = None
        self.context = None
        self.page = None
        
    async def solve_captcha_in_browser(
        self, 
        captcha_url: str, 
        cookies: Dict[str, str], 
        proxy_url: str = None,
        headless: bool = False,
        manual_mode: bool = False
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Solve captcha using a real browser
        
        Args:
            captcha_url: Full URL to captcha generation page (with data parameter)
            cookies: Cookies to set in browser (antiforgery, visitorId, aws-waf-token)
            proxy_url: Proxy in format "username:password@host:port"
            headless: Whether to run browser in headless mode (False shows small window)
            manual_mode: If True, wait for manual solving (user clicks images and submit)
            
        Returns:
            Tuple of (success: bool, result: dict with solution data)
        """
        try:
            from playwright.async_api import async_playwright
            
            logger.info("🌐 Starting browser-based captcha solver...")
            logger.info(f"🔗 Captcha URL: {captcha_url[:100]}...")
            logger.info(f"🌐 Proxy: {proxy_url[:50] if proxy_url else 'None'}...")
            logger.info(f"👁️ Headless: {headless}")
            
            async with async_playwright() as p:
                # Configure browser launch options to avoid detection
                launch_options = {
                    'headless': headless,
                    'args': [
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-ipc-flooding-protection',
                        '--disable-renderer-backgrounding',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-client-side-phishing-detection',
                        '--disable-sync',
                        '--disable-default-apps',
                        '--disable-extensions',
                        '--disable-plugins',
                        '--disable-translate',
                        '--hide-scrollbars',
                        '--mute-audio',
                        '--no-first-run',
                        '--no-default-browser-check',
                        '--disable-logging',
                        '--disable-gpu-logging',
                        '--silent',
                        '--disable-background-timer-throttling',
                        '--disable-background-networking',
                        '--disable-breakpad',
                        '--disable-component-extensions-with-background-pages',
                        '--disable-domain-reliability',
                        '--disable-features=TranslateUI',
                        '--disable-hang-monitor',
                        '--disable-prompt-on-repost',
                        '--disable-client-side-phishing-detection',
                        '--disable-component-update',
                        '--disable-domain-reliability',
                        '--disable-features=AudioServiceOutOfProcess',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-ipc-flooding-protection',
                        '--disable-renderer-backgrounding',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-background-timer-throttling',
                        '--disable-background-networking',
                        '--disable-breakpad',
                        '--disable-component-extensions-with-background-pages',
                        '--disable-domain-reliability',
                        '--disable-features=TranslateUI',
                        '--disable-hang-monitor',
                        '--disable-prompt-on-repost',
                        '--disable-client-side-phishing-detection',
                        '--disable-component-update',
                        '--disable-domain-reliability',
                        '--disable-features=AudioServiceOutOfProcess',
                        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                        '--window-size=1,1'  # 1x1 pixel window
                    ]
                }
                
                # Configure proxy if provided
                proxy_config = None
                if proxy_url:
                    proxy_config = self._parse_proxy_url(proxy_url)
                    if proxy_config and 'server' in proxy_config:
                        logger.info(f"🌐 Using proxy for browser: {proxy_config['server']}")
                        if 'username' in proxy_config:
                            logger.info(f"🔐 Proxy authentication enabled: {proxy_config['username'][:10]}...")
                    else:
                        logger.error(f"❌ Failed to parse proxy URL: {proxy_url}")
                        logger.warning("⚠️ Continuing without proxy - may be blocked by IP detection!")
                else:
                    logger.warning("⚠️ No proxy provided - browser may be blocked by IP detection!")
                
                # Launch browser with Chrome profile
                logger.info("🚀 Launching browser...")
                browser = await p.chromium.launch(**launch_options)
                
                # Create context with proxy and viewport settings
                context_options = {
                    'viewport': {'width': 1, 'height': 1},  # 1x1 pixel viewport
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                    'locale': 'es-ES',
                    'timezone_id': 'Europe/Madrid',
                    # Add extra headers to bypass IP detection
                    'extra_http_headers': {
                        'Accept-Language': 'ar-DZ,ar;q=0.9,en;q=0.8',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache',
                        'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Ch-Ua-Platform': '"Windows"',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                        # Algerian IP headers to bypass detection
                        'X-Forwarded-For': '41.200.0.1',
                        'X-Real-IP': '41.200.0.1',
                        'X-Client-IP': '41.200.0.1',
                        'CF-IPCountry': 'DZ',
                    }
                }
                
                # Add proxy to context if provided and valid
                if proxy_config and isinstance(proxy_config, dict) and 'server' in proxy_config:
                    context_options['proxy'] = proxy_config
                    logger.info("✅ Proxy configured in browser context")
                    logger.info(f"🔍 Proxy server: {proxy_config['server']}")
                elif proxy_url:
                    logger.error("❌ Proxy URL provided but parsing failed - continuing without proxy")
                
                context = await browser.new_context(**context_options)
                
                # Set cookies in browser context
                logger.info("🍪 Setting cookies in browser...")
                browser_cookies = []
                for name, value in cookies.items():
                    if name not in ['path', 'samesite', '__RequestVerificationToken']:
                        browser_cookies.append({
                            'name': name,
                            'value': value,
                            'domain': '.blsspainglobal.com',
                            'path': '/'
                        })
                        logger.info(f"🍪 Set cookie: {name}={value[:20]}...")
                
                await context.add_cookies(browser_cookies)
                
                # Create new page
                page = await context.new_page()
                self.page = page
                
                # Add stealth JavaScript to hide automation
                await page.add_init_script("""
                    // Hide webdriver property
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Spoof Chrome properties
                    window.chrome = {
                        runtime: {}
                    };
                    
                    // Override permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    // Spoof plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // Spoof languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['ar-DZ', 'ar', 'en']
                    });
                """)
                
                # Navigate to captcha page
                logger.info(f"🔗 Navigating to captcha page...")
                try:
                    response = await page.goto(captcha_url, wait_until='domcontentloaded', timeout=30000)
                    logger.info(f"📡 Page loaded with status: {response.status}")
                    
                    # Check for AWS WAF challenge
                    page_content = await page.content()
                    if await self._handle_waf_challenge(page, page_content, captcha_url):
                        logger.info("✅ AWS WAF challenge solved, retrying navigation...")
                        response = await page.goto(captcha_url, wait_until='domcontentloaded', timeout=30000)
                        logger.info(f"📡 Page loaded after WAF bypass with status: {response.status}")
                    
                    # Check if manual mode
                    if manual_mode:
                        logger.info("👤 MANUAL MODE: Captcha page loaded!")
                        logger.info("👤 Please solve the captcha manually:")
                        logger.info("   1. Click on the correct images")
                        logger.info("   2. Click the Submit button")
                        logger.info("   3. Wait for the response...")
                        logger.info("⏳ Browser will stay open and capture the response...")
                    else:
                        # Wait for captcha images to load (20 seconds timeout - doubled from 10s)
                        await page.wait_for_selector('.captcha-image-container', timeout=20000)
                    logger.info("✅ Captcha images loaded!")
                    
                except Exception as e:
                    if manual_mode:
                        # In manual mode, ignore selector timeout - page might be loaded differently
                        logger.warning(f"⚠️ Selector timeout (expected in manual mode): {e}")
                        logger.info("👤 Page is loaded - please solve captcha manually")
                    else:
                        logger.error(f"❌ Error loading captcha page: {e}")
                        await browser.close()
                        return False, {'error': str(e)}
                
                # If manual mode, skip automatic solving
                if manual_mode:
                    logger.info("👤 MANUAL MODE: Waiting for you to solve the captcha...")
                    logger.info("⏳ Listening for submit response...")
                    
                    # Set up response listener to capture token
                    captcha_response_token = None
                    captcha_response_data = {}
                    response_received = False
                    
                    # Use route to intercept and capture response before it's consumed
                    captured_responses = []
                    
                    async def handle_route(route):
                        # Log request details
                        if 'SubmitCaptcha' in route.request.url:
                            logger.info(f"📤 Outgoing request to: {route.request.url}")
                            logger.info(f"📤 Method: {route.request.method}")
                            logger.info(f"📤 Headers: {route.request.headers}")
                            try:
                                post_data = route.request.post_data
                                logger.info(f"📤 POST data: {post_data[:500] if post_data else 'None'}...")
                            except Exception as e:
                                logger.warning(f"⚠️ Could not get POST data: {e}")
                        
                        # Let the request go through normally
                        response = await route.fetch()
                        
                        # Capture SubmitCaptcha responses
                        if 'SubmitCaptcha' in route.request.url:
                            try:
                                body = await response.text()
                                captured_responses.append({
                                    'url': route.request.url,
                                    'status': response.status,
                                    'body': body
                                })
                                logger.info(f"🎯 Captured response body: {body[:200]}...")
                            except Exception as e:
                                logger.warning(f"⚠️ Could not capture body in route: {e}")
                        
                        # Fulfill the response
                        await route.fulfill(response=response)
                    
                    # Register route for captcha submissions
                    await page.route("**/*Captcha*", handle_route)
                    logger.info("🎯 Route interceptor registered for captcha responses")
                    
                    async def handle_response(response):
                        nonlocal captcha_response_token, captcha_response_data, response_received
                        # Listen for SubmitCaptcha response
                        if 'SubmitCaptcha' in response.url or 'Captcha' in response.url:
                            logger.info(f"🔍 Intercepted response from: {response.url}")
                            logger.info(f"📡 Response status: {response.status}")
                            
                            try:
                                # Try to get response body as text first
                                response_text = await response.text()
                                logger.info(f"📡 Response body (text): {response_text[:200]}...")
                                
                                # Try to parse as JSON
                                try:
                                    import json
                                    response_json = json.loads(response_text)
                                    logger.info(f"📡 Parsed JSON response: {response_json}")
                                    
                                    response_received = True
                                    captcha_response_data = response_json
                                    
                                    if response_json.get('success'):
                                        captcha_response_token = response_json.get('captcha')
                                        logger.info(f"✅ Captured captcha token: {captcha_response_token[:50] if captcha_response_token else 'None'}...")
                                    else:
                                        logger.warning(f"⚠️ Captcha submission response indicates failure: {response_json}")
                                        response_received = True
                                except json.JSONDecodeError:
                                    # Not JSON, but we still got a response
                                    logger.warning(f"⚠️ Response is not JSON, treating as HTML/redirect")
                                    # Check if it's a redirect (3xx status) which usually means success
                                    if 200 <= response.status < 400:
                                        logger.info("✅ Got successful response (200-399 status)")
                                        response_received = True
                                        captcha_response_data = {'text': response_text[:500]}
                                    else:
                                        logger.warning(f"⚠️ Response status {response.status} - might indicate failure")
                                        response_received = True
                                        
                            except Exception as e:
                                logger.warning(f"⚠️ Could not get response body: {e}")
                                # Even if we can't parse, mark as received
                                logger.info(f"📡 Response received but couldn't parse - checking status: {response.status}")
                                
                                # Mark as received regardless of status so we don't wait forever
                                response_received = True
                                captcha_response_data = {'status': response.status, 'url': response.url}
                                
                                if 200 <= response.status < 400:
                                    logger.info("✅ Status 200-399: Likely success")
                                elif response.status == 400:
                                    logger.error("❌ Status 400: Bad Request - Captcha was solved incorrectly or submission data invalid")
                                    logger.error("💡 This usually means you selected wrong images")
                                elif response.status == 403:
                                    logger.error("❌ Status 403: Forbidden - WAF or IP blocked")
                                else:
                                    logger.warning(f"⚠️ Status {response.status}: Unknown error")
                    
                    # Also add a general response logger to see all requests
                    async def log_all_responses(response):
                        logger.debug(f"🌐 Response: {response.url} (status: {response.status})")
                    
                    page.on('response', log_all_responses)
                    
                    # Register response listener
                    page.on('response', handle_response)
                    logger.info("✅ Response listener registered - solve captcha now!")
                    logger.info("💡 After you click Submit, wait a moment for the response to be captured...")
                    
                    # Wait for response (longer timeout for manual solving)
                    logger.info("⏳ Waiting for manual captcha submission (max 300 seconds / 5 minutes)...")
                    max_wait = 300  # 5 minutes for manual solving
                    waited = 0
                    check_interval = 1.0  # Check every second
                    
                    while not response_received and waited < max_wait:
                        await asyncio.sleep(check_interval)
                        waited += check_interval
                        if waited % 30 == 0:  # Log every 30 seconds
                            logger.info(f"⏳ Still waiting for manual submission... ({waited}s / {max_wait}s)")
                    
                    if response_received:
                        logger.info(f"✅ Response received after {waited:.1f} seconds")
                        
                        # Give a moment for any final page updates
                        logger.info("⏳ Waiting 2 seconds for page to finish processing...")
                        await asyncio.sleep(2)
                        
                        # Check if we have captured responses from route interceptor
                        if captured_responses:
                            logger.info(f"🎯 Found {len(captured_responses)} captured response(s)")
                            for captured in captured_responses:
                                if 'SubmitCaptcha' in captured['url']:
                                    logger.info(f"🎯 Processing SubmitCaptcha response:")
                                    logger.info(f"   Status: {captured['status']}")
                                    logger.info(f"   Body: {captured['body'][:300]}...")
                                    
                                    # Try to parse as JSON
                                    try:
                                        import json
                                        response_json = json.loads(captured['body'])
                                        captcha_response_data = response_json
                                        
                                        if response_json.get('success'):
                                            captcha_response_token = response_json.get('captcha')
                                            captcha_id = response_json.get('captchaId')
                                            logger.info(f"✅ Extracted token from captured response: {captcha_response_token[:50] if captcha_response_token else 'None'}...")
                                            logger.info(f"✅ Extracted captcha ID: {captcha_id[:50] if captcha_id else 'None'}...")
                                        else:
                                            logger.error(f"❌ Captcha submission failed (wrong images): {response_json}")
                                            logger.error("💡 The images you selected were incorrect")
                                            logger.error("💡 Please try again with different images")
                                    except json.JSONDecodeError:
                                        logger.warning(f"⚠️ Captured response is not JSON")
                                        # If status 400, it's a request error
                                        if captured['status'] == 400:
                                            logger.error("❌ Status 400: Bad Request - invalid submission data")
                                            logger.error("💡 This usually means required fields are missing or malformed")
                                        elif captured['status'] == 200:
                                            logger.warning("⚠️ Status 200 but response is not JSON - unexpected format")
                                    except Exception as e:
                                        logger.error(f"❌ Error parsing captured response: {e}")
                        
                        logger.info("🔒 Closing browser after receiving response...")
                        
                        # Check if submission was successful
                        success = captcha_response_data.get('success', False)
                        
                        # Build result
                        result = {
                            'submission_successful': success,
                            'captcha_token': captcha_response_token,
                            'captcha_id': captcha_response_data.get('captchaId'),
                            'response': captcha_response_data,
                            'manual_mode': True
                        }
                        
                        # Store token if successful
                        if success and captcha_response_token:
                            logger.info("💾 Storing captcha token...")
                            await self._store_captcha_token(captcha_response_data)
                        
                        # Close browser
                        await browser.close()
                        logger.info("✅ Browser closed")
                        
                        return success, result
                    else:
                        logger.warning(f"⚠️ No response received after {max_wait} seconds")
                        logger.warning("⚠️ Manual solving timeout")
                        await browser.close()
                        return False, {'error': 'Manual solving timeout'}
                
                # Extract captcha data from page (automatic mode only)
                logger.info("🔍 Extracting captcha data from page...")
                captcha_data = await self._extract_captcha_data_from_page(page)
                
                if not captcha_data:
                    logger.error("❌ Failed to extract captcha data")
                    await browser.close()
                    return False, {'error': 'Failed to extract captcha data'}
                
                logger.info(f"✅ Extracted captcha data: {list(captcha_data.keys())}")
                
                # Get image data for NoCaptcha API
                logger.info("📸 Extracting captcha images...")
                images_data = await self._extract_captcha_images(page)
                
                if not images_data:
                    logger.error("❌ Failed to extract captcha images")
                    await browser.close()
                    return False, {'error': 'Failed to extract images'}
                
                logger.info(f"✅ Extracted {len(images_data)} captcha images")
                
                # Solve captcha using NoCaptcha API
                logger.info("🤖 Solving captcha with NoCaptcha API...")
                selected_images = await self._solve_with_nocaptcha(images_data, captcha_data.get('instruction', ''))
                
                if not selected_images:
                    logger.error("❌ Failed to solve captcha")
                    await browser.close()
                    return False, {'error': 'Failed to solve captcha'}
                
                logger.info(f"✅ Captcha solved! Selected images: {selected_images}")
                
                # Click selected images in browser
                logger.info("🖱️ Clicking selected images in browser...")
                for image_id in selected_images:
                    try:
                        # Find and click the image
                        await page.click(f'img[data-image-id="{image_id}"]', timeout=2000)
                        logger.info(f"✅ Clicked image: {image_id}")
                        await asyncio.sleep(0.1)  # Small delay between clicks
                    except Exception as e:
                        logger.warning(f"⚠️ Could not click image {image_id}: {e}")
                
                # Submit captcha by clicking submit button
                logger.info("📤 Submitting captcha in browser...")
                try:
                    # Set up response listener to capture captcha token
                    captcha_response_token = None
                    captcha_response_data = {}
                    response_received = False
                    
                    async def handle_response(response):
                        nonlocal captcha_response_token, captcha_response_data, response_received
                        # Listen for SubmitCaptcha response
                        if 'SubmitCaptcha' in response.url:
                            try:
                                response_json = await response.json()
                                logger.info(f"📡 Captcha submission response: {response_json}")
                                
                                response_received = True
                                captcha_response_data = response_json
                                
                                if response_json.get('success'):
                                    captcha_response_token = response_json.get('captcha')
                                    logger.info(f"✅ Captured captcha token: {captcha_response_token[:50] if captcha_response_token else 'None'}...")
                                else:
                                    logger.warning(f"⚠️ Captcha submission failed: {response_json}")
                            except Exception as e:
                                logger.warning(f"⚠️ Could not parse captcha response: {e}")
                                response_received = True  # Mark as received even if parsing failed
                    
                    # Register response listener BEFORE clicking
                    page.on('response', handle_response)
                    logger.info("✅ Response listener registered")
                    
                    # Click the submit button (10 seconds timeout - doubled from 5s)
                    logger.info("🖱️ Clicking submit button...")
                    await page.click('button[type="submit"], .submit-button, input[type="submit"]', timeout=10000)
                    logger.info("✅ Submit button clicked")
                    
                    # Wait for the API response (with generous timeout for slow pages)
                    logger.info("⏳ Waiting for captcha submission response (max 60 seconds)...")
                    max_wait = 60  # 60 seconds max wait (doubled from 30s)
                    waited = 0
                    check_interval = 0.5  # Check every 0.5 seconds
                    
                    while not response_received and waited < max_wait:
                        await asyncio.sleep(check_interval)
                        waited += check_interval
                        if waited % 5 == 0:  # Log every 5 seconds
                            logger.info(f"⏳ Still waiting for response... ({waited}s / {max_wait}s)")
                    
                    if response_received:
                        logger.info(f"✅ Response received after {waited:.1f} seconds")
                        
                        # Close browser immediately after getting response (as user requested)
                        logger.info("🔒 Closing browser after receiving captcha response...")
                    else:
                        logger.warning(f"⚠️ No response received after {max_wait} seconds")
                        logger.warning("⚠️ This might mean the submission failed or the page is very slow")
                    
                    # Give a bit more time for page to process (only if needed)
                    if not response_received:
                        logger.info("⏳ Waiting for page to process response...")
                        try:
                            await page.wait_for_load_state('networkidle', timeout=10000)  # Doubled from 5s
                            logger.info("✅ Page reached network idle state")
                        except Exception as e:
                            logger.warning(f"⚠️ Page did not reach network idle: {e}")
                            # Continue anyway
                    
                    # Check if submission was successful
                    success = False
                    if captcha_response_data.get('success'):
                        logger.info("✅ Captcha submission successful (from API response)!")
                        success = True
                    else:
                        # Check page content as fallback
                        try:
                            page_content = await page.content()
                            if 'success' in page_content.lower() or 'valid' in page_content.lower():
                                logger.info("✅ Captcha submission successful (from page content)!")
                                success = True
                            else:
                                logger.warning("⚠️ Captcha submission response unclear")
                        except Exception as e:
                            logger.warning(f"⚠️ Could not check page content: {e}")
                    
                    # Build result with captured token
                    result = {
                        'selected_images': selected_images,
                        'captcha_data': captcha_data,
                        'submission_successful': success,
                        'captcha_token': captcha_response_token,  # The encrypted captcha token
                        'captcha_id': captcha_response_data.get('captchaId'),  # The captcha ID
                        'response': captcha_response_data  # Full response for future use
                    }
                    
                    # Store the captcha response for future use
                    if success and captcha_response_token:
                        logger.info("💾 Storing captcha token...")
                        await self._store_captcha_token(captcha_response_data)
                    
                    # Now close browser AFTER we have the response
                    logger.info("🔒 Closing browser after receiving response...")
                    await browser.close()
                    logger.info("✅ Browser closed")
                    
                    return success, result
                    
                except Exception as e:
                    logger.error(f"❌ Error submitting captcha: {e}")
                    await browser.close()
                    return False, {'error': str(e)}
                    
        except ImportError:
            logger.error("❌ Playwright not installed! Run: pip install playwright && playwright install chromium")
            return False, {'error': 'Playwright not installed'}
        except Exception as e:
            logger.error(f"❌ Error in browser captcha solver: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False, {'error': str(e)}
    
    async def _extract_captcha_data_from_page(self, page) -> Dict[str, str]:
        """Extract captcha form data from page (Id, Captcha, __RequestVerificationToken)"""
        try:
            # Extract hidden form fields using JavaScript
            form_data = await page.evaluate("""
                () => {
                    const data = {};
                    
                    // Get Id field
                    const idField = document.querySelector('input[name="Id"]');
                    if (idField) data.Id = idField.value;
                    
                    // Get Captcha field
                    const captchaField = document.querySelector('input[name="Captcha"]');
                    if (captchaField) data.Captcha = captchaField.value;
                    
                    // Get __RequestVerificationToken
                    const tokenField = document.querySelector('input[name="__RequestVerificationToken"]');
                    if (tokenField) data.__RequestVerificationToken = tokenField.value;
                    
                    // Get instruction text
                    const instruction = document.querySelector('.captcha-instruction, .instruction-text');
                    if (instruction) data.instruction = instruction.textContent.trim();
                    
                    return data;
                }
            """)
            
            logger.info(f"📋 Extracted form data from page:")
            for key, value in form_data.items():
                preview = str(value)[:50] if value else 'None'
                logger.info(f"   {key}: {preview}...")
            
            return form_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting captcha data: {e}")
            return {}
    
    async def _extract_captcha_images(self, page) -> List[Dict[str, str]]:
        """Extract captcha images (id, src) from page"""
        try:
            # Extract image data using JavaScript
            images = await page.evaluate("""
                () => {
                    const images = [];
                    const imgElements = document.querySelectorAll('.captcha-image-container img, img[data-image-id]');
                    
                    imgElements.forEach((img, index) => {
                        images.push({
                            id: img.getAttribute('data-image-id') || img.getAttribute('id') || `image_${index}`,
                            src: img.src,
                            alt: img.alt || ''
                        });
                    });
                    
                    return images;
                }
            """)
            
            logger.info(f"📸 Extracted {len(images)} images from page")
            return images
            
        except Exception as e:
            logger.error(f"❌ Error extracting images: {e}")
            return []
    
    async def _solve_with_nocaptcha(self, images: List[Dict[str, str]], instruction: str) -> List[str]:
        """Solve captcha using NoCaptcha API"""
        try:
            import httpx
            import base64
            
            logger.info(f"🤖 Sending {len(images)} images to NoCaptcha API...")
            logger.info(f"📝 Instruction: {instruction}")
            
            # Prepare images for API
            image_data_list = []
            for img in images:
                # Download image and convert to base64
                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        response = await client.get(img['src'])
                        if response.status_code == 200:
                            img_base64 = base64.b64encode(response.content).decode('utf-8')
                            image_data_list.append({
                                'id': img['id'],
                                'data': img_base64
                            })
                except Exception as e:
                    logger.warning(f"⚠️ Failed to download image {img['id']}: {e}")
            
            if not image_data_list:
                logger.error("❌ No images downloaded successfully")
                return []
            
            # Call NoCaptcha API
            api_url = "https://api.nocaptchaai.com/solve"
            payload = {
                "key": self.nocaptcha_api_key,
                "type": "image",
                "images": image_data_list,
                "instruction": instruction or "Select all images matching the instruction"
            }
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(api_url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        selected_ids = result.get('selected_images', [])
                        logger.info(f"✅ NoCaptcha API solved captcha: {selected_ids}")
                        return selected_ids
                    else:
                        logger.error(f"❌ NoCaptcha API failed: {result.get('error')}")
                        return []
                else:
                    logger.error(f"❌ NoCaptcha API request failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Error calling NoCaptcha API: {e}")
            return []
    
    def _parse_proxy_url(self, proxy_url: str) -> Dict[str, str]:
        """
        Parse proxy URL into Playwright proxy config
        Supports formats:
        - username:password@host:port
        - http://username:password@host:port
        - host:port
        - http://host:port
        """
        try:
            # Remove protocol if present
            if proxy_url.startswith('http://') or proxy_url.startswith('https://'):
                proxy_url = proxy_url.replace('http://', '').replace('https://', '')
            
            # Format: username:password@host:port or host:port
            if '@' in proxy_url:
                auth, server = proxy_url.split('@', 1)
                if ':' in auth:
                    username, password = auth.split(':', 1)
                else:
                    username = auth
                    password = ''
                
                if ':' in server:
                    host, port = server.rsplit(':', 1)
                else:
                    host = server
                    port = '80'
                
                config = {
                    'server': f'http://{host}:{port}',
                }
                
                if username:
                    config['username'] = username
                if password:
                    config['password'] = password
                
                logger.info(f"🔧 Parsed proxy: {host}:{port} (auth: {'yes' if username else 'no'})")
                return config
            else:
                # No authentication
                if ':' in proxy_url:
                    host, port = proxy_url.rsplit(':', 1)
                else:
                    host = proxy_url
                    port = '80'
                
                config = {
                    'server': f'http://{host}:{port}'
                }
                
                logger.info(f"🔧 Parsed proxy: {host}:{port} (no auth)")
                return config
                
        except Exception as e:
            logger.error(f"❌ Error parsing proxy URL '{proxy_url}': {e}")
            # Try to return a basic config anyway
            try:
                if proxy_url.startswith('http://') or proxy_url.startswith('https://'):
                    return {'server': proxy_url}
                else:
                    return {'server': f'http://{proxy_url}'}
            except:
                logger.error(f"❌ Completely failed to parse proxy URL")
                return None
    
    async def _store_captcha_token(self, response_data: Dict[str, any]) -> bool:
        """Store captcha response token for future use"""
        try:
            import json
            import os
            from datetime import datetime
            
            # Create tokens directory if it doesn't exist
            tokens_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'captcha_tokens')
            os.makedirs(tokens_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            token_file = os.path.join(tokens_dir, f'captcha_token_{timestamp}.json')
            
            # Prepare data to store
            storage_data = {
                'timestamp': timestamp,
                'success': response_data.get('success'),
                'captcha_token': response_data.get('captcha'),
                'captcha_id': response_data.get('captchaId'),
                'full_response': response_data
            }
            
            # Save to file
            with open(token_file, 'w', encoding='utf-8') as f:
                json.dump(storage_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Stored captcha token to: {token_file}")
            logger.info(f"🔑 Token: {storage_data['captcha_token'][:50]}...")
            logger.info(f"🆔 Captcha ID: {storage_data['captcha_id'][:50] if storage_data['captcha_id'] else 'None'}...")
            
            # Also store in a "latest" file for easy access
            latest_file = os.path.join(tokens_dir, 'latest_captcha_token.json')
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(storage_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Updated latest captcha token file")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing captcha token: {e}")
            return False
    
    async def _handle_waf_challenge(self, page, page_content: str, captcha_url: str) -> bool:
        """Handle AWS WAF challenge in browser"""
        try:
            # Check if we got a WAF challenge page
            if 'gokuProps' in page_content and 'challenge.js' in page_content:
                logger.info("🔍 AWS WAF challenge detected in browser!")
                
                # Extract challenge data using Python regex from page content (more reliable than JavaScript)
                import re
                import json
                
                # Try to extract gokuProps from the page content
                goku_props = None
                
                # Pattern 1: window.gokuProps = {...}
                patterns = [
                    r'window\.gokuProps\s*=\s*({[^;]+});',
                    r'window\.gokuProps\s*=\s*({.+?});',
                    r'gokuProps\s*=\s*({[^;]+});',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, page_content, re.DOTALL)
                    if match:
                        try:
                            goku_props = json.loads(match.group(1))
                            logger.info(f"✅ Extracted gokuProps with pattern: {pattern[:30]}...")
                            break
                        except json.JSONDecodeError as e:
                            logger.warning(f"⚠️ JSON decode failed for pattern {pattern[:30]}: {e}")
                            continue
                
                if not goku_props:
                    logger.warning("⚠️ Could not extract gokuProps from page content")
                    logger.info("📄 Page content preview:")
                    logger.info(page_content[:500] if len(page_content) > 500 else page_content)
                    return False
                
                challenge_data = {
                    'goku_props': goku_props,
                    'host': 'algeria.blsspainglobal.com'
                }
                
                if challenge_data and challenge_data.get('goku_props'):
                    logger.info("🔍 Extracted WAF challenge data from browser")
                    logger.info(f"🔍 gokuProps keys: {list(goku_props.keys())}")
                    
                    # Solve the WAF challenge using the same method as HTTP requests
                    try:
                        import sys
                        import os
                        
                        # Add awswaf path
                        awswaf_path = os.path.join(os.path.dirname(__file__), '..', '..', 'awswaf', 'python')
                        if awswaf_path not in sys.path:
                            sys.path.insert(0, awswaf_path)
                        
                        from awswaf.aws import AwsWaf
                        
                        # Use the proper extract method to get goku_props and host
                        extract_result = AwsWaf.extract(page_content)
                        
                        if isinstance(extract_result, tuple) and len(extract_result) == 2:
                            goku_props_extracted, host_extracted = extract_result
                        elif isinstance(extract_result, dict) and 'key' in extract_result and 'host' in extract_result:
                            goku_props_extracted = {
                                'key': extract_result['key'],
                                'iv': extract_result.get('iv'),
                                'context': extract_result.get('context')
                            }
                            host_extracted = extract_result['host']
                        else:
                            logger.warning(f"⚠️ Unexpected extract result format: {type(extract_result)}")
                            # Fallback to our extracted data
                            goku_props_extracted = challenge_data['goku_props']
                            host_extracted = challenge_data['host']
                        
                        logger.info(f"🔍 Using goku_props keys: {list(goku_props_extracted.keys()) if isinstance(goku_props_extracted, dict) else 'N/A'}")
                        logger.info(f"🔍 Using host: {host_extracted}")
                        
                        logger.info("🔄 Solving AWS WAF challenge in browser...")
                        import time
                        start = time.time()
                        
                        # Solve the challenge
                        token = AwsWaf(goku_props_extracted, host_extracted, "algeria.blsspainglobal.com")()
                        
                        end = time.time()
                        logger.info(f"✅ Challenge solved in {end - start:.2f} seconds!")
                        logger.info(f"🔑 Generated token: {token[:50] if token else 'None'}...")
                        
                        if not token:
                            logger.error("❌ Token generation returned None")
                            return False
                        
                        # Clean the token (remove trailing colons if any)
                        token = token.rstrip(':')
                        
                        # Set the AWS WAF token as a cookie in the browser
                        await page.context.add_cookies([{
                            'name': 'aws-waf-token',
                            'value': token,
                            'domain': '.blsspainglobal.com',
                            'path': '/'
                        }])
                        
                        logger.info(f"🔑 Set AWS WAF token cookie in browser: {token[:20]}...")
                        return True
                        
                    except Exception as e:
                        logger.error(f"❌ Error solving WAF challenge in browser: {e}")
                        import traceback
                        logger.error(f"📋 Traceback: {traceback.format_exc()}")
                        return False
                else:
                    logger.warning("⚠️ Could not extract WAF challenge data from browser")
                    return False
            
            # Check for CloudFront 403 error
            elif '403 ERROR' in page_content and 'CloudFront' in page_content:
                logger.warning("⚠️ CloudFront 403 error detected - this might be a WAF block")
                logger.info("💡 Try using a proxy or different IP address")
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error handling WAF challenge: {e}")
            return False


async def solve_bls_captcha_with_browser(
    captcha_url: str,
    cookies: Dict[str, str],
    proxy_url: str = None,
    headless: bool = False,
    nocaptcha_api_key: str = None
) -> Tuple[bool, Dict[str, any]]:
    """
    Convenience function to solve BLS captcha with browser
    
    Args:
        captcha_url: Full URL to captcha page (with data parameter)
        cookies: Session cookies (antiforgery, visitorId, aws-waf-token)
        proxy_url: Proxy URL in format "username:password@host:port"
        headless: Whether to run browser in headless mode
        nocaptcha_api_key: NoCaptcha API key
        
    Returns:
        Tuple of (success: bool, result: dict)
    """
    solver = BrowserCaptchaSolver(nocaptcha_api_key=nocaptcha_api_key)
    return await solver.solve_captcha_in_browser(captcha_url, cookies, proxy_url, headless)


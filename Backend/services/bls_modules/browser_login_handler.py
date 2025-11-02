"""
Browser-based login handler for BLS
Handles the complete login flow in browser including captcha solving and AWS WAF
"""

from typing import Dict, Any, Optional, Tuple
from loguru import logger
import asyncio
import random


class BrowserLoginHandler:
    """Handles full BLS login flow in browser with captcha solving"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        
    async def login_in_browser(
        self,
        login_url: str,
        email: str,
        password: str,
        cookies: Dict[str, str],
        proxy_url: str = None,
        headless: bool = False
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Complete the login flow in browser with automatic captcha solving
        
        Args:
            login_url: BLS login page URL
            email: User email
            password: User password
            cookies: Initial cookies (antiforgery, visitorId, aws-waf-token)
            proxy_url: Proxy in format "username:password@host:port"
            headless: Whether to run browser in headless mode
            
        Returns:
            Tuple of (success: bool, result: dict with login result)
        """
        try:
            from playwright.async_api import async_playwright
            
            logger.info(f"🌐 Starting browser-based BLS login for: {email}")
            
            # Step 0: Launch browser with proxy
            logger.info("🚀 Step 0: Launching browser...")
            playwright = await async_playwright().start()
            
            # Configure browser with stealth settings
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
            
            browser_options = {
                'headless': headless,
                'args': browser_args
            }
            
            if proxy_url:
                # Parse proxy URL
                proxy_parts = self._parse_proxy(proxy_url)
                browser_options['proxy'] = proxy_parts
                logger.info(f"🌐 Using proxy: {proxy_parts['server']}")
            
            self.browser = await playwright.chromium.launch(**browser_options)
            
            # Create context with comprehensive anti-bot headers
            context_options = {
                'viewport': {'width': 1366, 'height': 768},  # Normal desktop viewport
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'locale': 'es-ES',
                'timezone_id': 'Europe/Madrid',
                'permissions': [],
                'extra_http_headers': {
                    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'max-age=0',
                    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'DNT': '1',
                }
            }
            
            self.context = await self.browser.new_context(**context_options)
            self.page = await self.context.new_page()
            
            # Add comprehensive stealth JavaScript (anti-bot detection)
            await self.page.add_init_script("""
                // Remove webdriver flag
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                
                // Add realistic plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer'},
                        {name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                        {name: 'Native Client', description: '', filename: 'internal-nacl-plugin'}
                    ]
                });
                
                // Set Spanish locale
                Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en-US', 'en']});
                Object.defineProperty(navigator, 'language', {get: () => 'es-ES'});
                
                // Add realistic screen resolution
                Object.defineProperty(screen, 'width', {get: () => 1920});
                Object.defineProperty(screen, 'height', {get: () => 1080});
                Object.defineProperty(screen, 'availWidth', {get: () => 1920});
                Object.defineProperty(screen, 'availHeight', {get: () => 1040});
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            # Add initial cookies
            if cookies:
                await self.context.add_cookies([
                    {
                        'name': name,
                        'value': value,
                        'domain': '.blsspainglobal.com',
                        'path': '/'
                    }
                    for name, value in cookies.items()
                ])
                logger.info(f"🍪 Added {len(cookies)} cookies to browser context")
            
            # Step 1: Navigate to login page and handle AWS WAF
            logger.info("🔍 Step 1: Navigating to login page...")
            logger.info("💡 Browser will handle AWS WAF challenges automatically...")
            logger.info("⏳ This may take 1-3 minutes while WAF challenge is being solved...")
            try:
                # Use 'commit' instead of 'domcontentloaded' to allow WAF challenge to process
                response = await self.page.goto(login_url, wait_until='commit', timeout=180000)  # 3 minutes timeout
                logger.info(f"📡 Initial navigation committed with status: {response.status if response else 'unknown'}")
                
                # Wait for page to actually load after navigation (WAF might be processing)
                logger.info("⏳ Waiting for page to load completely (WAF might be processing)...")
                max_wait = 180  # 3 minutes
                wait_interval = 5  # 5 seconds
                elapsed = 0
                form_loaded = False
                
                while elapsed < max_wait:
                    await asyncio.sleep(wait_interval)
                    elapsed += wait_interval
                    
                    # Check if page has loaded by looking for the Verify button
                    try:
                        form_visible = await self.page.query_selector('#btnVerify')
                        if form_visible:
                            logger.info(f"✅ Login page loaded successfully after {elapsed}s!")
                            form_loaded = True
                            break
                        else:
                            # Check current URL to see if still on WAF challenge
                            current_url = self.page.url
                            if 'Login' in current_url:
                                logger.info(f"⏳ WAF challenge still processing... ({elapsed}s / {max_wait}s)")
                            else:
                                logger.info(f"⏳ Waiting for page... ({elapsed}s / {max_wait}s)")
                    except Exception as e:
                        logger.info(f"⏳ Still loading... ({elapsed}s / {max_wait}s)")
                
                # Final check
                if not form_loaded:
                    logger.error("❌ Login page did not load after 3 minutes")
                    # Try to get current page info for debugging
                    try:
                        current_url = self.page.url
                        logger.error(f"❌ Current URL: {current_url}")
                        page_title = await self.page.title()
                        logger.error(f"❌ Page title: {page_title}")
                    except:
                        pass
                    raise Exception("Page load timeout - WAF challenge may have failed")
                
                # Check for 403 error in page content
                try:
                    page_content = await self.page.content()
                    if '403' in page_content and 'ERROR' in page_content.upper():
                        logger.error("❌ Got 403 Forbidden in page content - CloudFront blocked the request")
                        logger.info("💡 This usually means: proxy is blocked, rate limiting, or IP banned")
                        raise Exception("CloudFront 403 error")
                except Exception as e:
                    if "403" in str(e):
                        raise
                        
            except Exception as e:
                logger.error(f"❌ Error loading login page: {e}")
                await self.browser.close()
                return False, {'error': f'Failed to load login page: {str(e)}'}
            
            # Step 2: Fill email address
            logger.info("📝 Step 2: Filling email address...")
            email_filled = await self._fill_email(email)
            
            if not email_filled:
                logger.error("❌ Failed to fill email address")
                await self.browser.close()
                return False, {'error': 'Failed to fill email'}
            
            # Step 3: Click Verify button (this navigates to captcha page)
            logger.info("🔍 Step 3: Clicking Verify button...")
            await self._click_verify_button()
            
            # Step 4: Validate password is provided
            if not password:
                logger.error("❌ Password is required for login")
                await self.browser.close()
                return False, {'error': 'Password is required'}
            
            # Step 5: Fill password on the captcha page
            logger.info("🔐 Step 5: Filling password on captcha page...")
            password_filled = await self._fill_password(password)
            
            if not password_filled:
                logger.error("❌ Failed to fill password")
                await self.browser.close()
                return False, {'error': 'Failed to fill password'}
            
            # Step 6: Automatically solve captcha on the captcha page
            logger.info("🤖 Step 6: Automatically solving captcha with NoCaptchaAI...")
            captcha_result = await self._solve_captcha_automatically()
            
            if not captcha_result:
                logger.error("❌ Captcha solving failed or timed out")
                await self.browser.close()
                return False, {'error': 'Captcha solving failed'}
            
            logger.info("✅ Captcha solved successfully!")
            
            # Step 7: Extract session cookies
            logger.info("🍪 Step 7: Extracting session cookies...")
            session_cookies = await self._extract_session_cookies()
            
            # Keep browser open for 1 minute for inspection
            logger.info("")
            logger.info("⏳ Keeping browser open for 60 seconds for inspection...")
            await asyncio.sleep(60)
            logger.info("✅ Inspection complete")
            
            await self.browser.close()
            await playwright.stop()
            
            return True, {
                'success': True,
                'message': 'Login successful',
                'cookies': session_cookies
            }
            
        except Exception as e:
            logger.error(f"❌ Error in browser login: {e}")
            if self.browser:
                await self.browser.close()
            return False, {'error': str(e)}
    
    def _parse_proxy(self, proxy_url: str) -> Dict[str, str]:
        """Parse proxy URL into browser format"""
        try:
            # Remove protocol if present
            clean_url = proxy_url.replace('http://', '').replace('https://', '')
            
            # Parse format: username:password@host:port
            if '@' in clean_url:
                auth_part, server_part = clean_url.split('@')
                username, password = auth_part.split(':')
                return {
                    'server': f'http://{server_part}',
                    'username': username,
                    'password': password
                }
            else:
                # Format: host:port
                return {
                    'server': f'http://{clean_url}'
                }
        except Exception as e:
            logger.error(f"❌ Failed to parse proxy: {e}")
            return None
    
    async def _fill_email(self, email: str) -> bool:
        """Fill email address in the login form"""
        try:
            # The IDs change dynamically, so we need to find the visible input field using JavaScript
            logger.info("🔍 Searching for visible email input field...")
            
            # Use JavaScript to find the visible input field (check parent div's computed style and dimensions)
            visible_field_id = await self.page.evaluate("""
                () => {
                    // Get all text inputs in the form
                    const inputs = document.querySelectorAll('input[type="text"].entry-disabled');
                    console.log(`Found ${inputs.length} text inputs with class 'entry-disabled'`);
                    
                    for (let input of inputs) {
                        // Check the parent div's computed style and dimensions
                        const parentDiv = input.closest('.mb-3');
                        if (parentDiv) {
                            const style = window.getComputedStyle(parentDiv);
                            // Check if parent is visible (display, visibility, and dimensions)
                            const isVisible = style.display !== 'none' && 
                                            style.visibility !== 'hidden' &&
                                            parentDiv.offsetWidth > 0 && 
                                            parentDiv.offsetHeight > 0;
                            
                            console.log(`Input ${input.id}: visible=${isVisible}, offsetWidth=${parentDiv.offsetWidth}, offsetHeight=${parentDiv.offsetHeight}`);
                            
                            if (isVisible) {
                                console.log(`Found visible input: ${input.id}`);
                                return input.id;
                            }
                        } else {
                            console.log(`Input ${input.id}: no .mb-3 parent found`);
                        }
                    }
                    return null;
                }
            """)
            
            if visible_field_id:
                logger.info(f"✅ Found visible email input field with ID: {visible_field_id}")
                await self.page.fill(f'#{visible_field_id}', email)
                logger.info(f"✅ Filled email: {email}")
                await asyncio.sleep(1)
                return True
            else:
                logger.error("❌ Could not find visible email input field")
                logger.info("💡 Taking screenshot for debugging...")
                try:
                    await self.page.screenshot(path="login_email_field_not_found.png")
                    logger.info("📸 Screenshot saved as login_email_field_not_found.png")
                except Exception as e:
                    logger.error(f"❌ Failed to take screenshot: {e}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error filling email: {e}")
            return False
    
    async def _click_verify_button(self):
        """Click the Verify button and wait for navigation to captcha page"""
        try:
            # User said: <button class="btn btn-primary" id="btnVerify" onclick="return OnSubmitVerify();">Verify</button>
            verify_selectors = [
                '#btnVerify',
                'button#btnVerify',
                'button.btn.btn-primary',
                'button[onclick*="OnSubmitVerify"]'
            ]
            
            for selector in verify_selectors:
                try:
                    verify_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if verify_button:
                        await verify_button.click()
                        logger.info("✅ Clicked Verify button")
                        
                        # Wait for navigation to captcha page (URL contains "logincaptcha")
                        logger.info("⏳ Waiting for navigation to captcha page...")
                        await asyncio.sleep(3)  # Give it time to redirect
                        
                        # Wait for navigation
                        try:
                            await self.page.wait_for_url('**/logincaptcha**', timeout=10000)
                            logger.info("✅ Navigated to captcha page")
                        except:
                            logger.info("ℹ️ Navigation timeout or captcha on same page, continuing...")
                        
                        await asyncio.sleep(2)  # Additional wait for captcha to load
                        return
                except:
                    continue
            
            logger.error("❌ Could not find Verify button")
            
        except Exception as e:
            logger.error(f"❌ Error clicking Verify button: {e}")
    
    async def _solve_captcha_automatically(self) -> bool:
        """Solve captcha automatically using NoCaptchaAI (same as registration)"""
        try:
            logger.info("🔍 Looking for captcha iframe...")
            iframe_element = None
            captcha_frame = None
            
            try:
                # Wait for iframe to be present (registration uses iframe)
                iframe_element = await self.page.wait_for_selector('iframe.k-content-frame', timeout=10000)
                logger.info("✅ Found captcha iframe")
                
                # Get the frame from the iframe element
                captcha_frame = await iframe_element.content_frame()
                if not captcha_frame:
                    logger.error("❌ Could not access iframe content")
                    return False
                
                logger.info("✅ Switched to captcha iframe context")
                frame_type = "iframe"
            except Exception as e:
                logger.info(f"ℹ️ No iframe found, captcha is on main page: {e}")
                captcha_frame = self.page  # Use main page
                frame_type = "main_page"
            
            # Wait for captcha to fully load (same logic as registration)
            logger.info("⏳ Waiting for captcha to fully load...")
            await asyncio.sleep(5)  # Wait for 54 images + CSS + positioning
            
            # Wait additional time
            logger.info("⏳ Waiting 5 more seconds to ensure captcha is fully settled...")
            await asyncio.sleep(5)
            logger.info(f"✅ Captcha should now be fully ready ({frame_type})!")
            
            # Extract captcha question and images
            logger.info("📸 Extracting captcha images and question...")
            captcha_data = await captcha_frame.evaluate("""
                () => {
                    // Get captcha question using z-index
                    function getQuestionByZIndex() {
                        const labels = [...document.querySelectorAll('.box-label')];
                        let maxZIndex = 0;
                        let foundLabel = null;
                        for (let label of labels) {
                            const style = window.getComputedStyle(label);
                            const zIndex = style.getPropertyValue('z-index');
                            const zIndexNum = parseInt(zIndex);
                            if (zIndex !== 'auto' && zIndexNum > maxZIndex) {
                                maxZIndex = zIndexNum;
                                foundLabel = label;
                            }
                        }
                        return foundLabel ? foundLabel.innerText.trim() : '';
                    }
                    
                    const question = getQuestionByZIndex();
                    
                    // Get visible images with position + z-index method
                    const gridPositions = [
                        {left: 0, top: 0},    // Grid 0
                        {left: 110, top: 0},  // Grid 1
                        {left: 220, top: 0},  // Grid 2
                        {left: 0, top: 110},  // Grid 3
                        {left: 110, top: 110}, // Grid 4
                        {left: 220, top: 110}, // Grid 5
                        {left: 0, top: 220},   // Grid 6
                        {left: 110, top: 220}, // Grid 7
                        {left: 220, top: 220}  // Grid 8
                    ];
                    
                    function findVisibleDivAtPosition(left, top) {
                        const allDivs = [...document.querySelectorAll('.col-4')].filter(d => d.getClientRects().length);
                        let maxZIndex = 0;
                        let foundDiv = null;
                        for (let div of allDivs) {
                            const style = window.getComputedStyle(div);
                            const divLeft = style.getPropertyValue('left');
                            const divTop = style.getPropertyValue('top');
                            const divZIndex = style.getPropertyValue('z-index');
                            if (divLeft === left + 'px' && divTop === top + 'px' && divZIndex !== 'auto') {
                                const zIndexNum = parseInt(divZIndex);
                                if (zIndexNum > maxZIndex) {
                                    maxZIndex = zIndexNum;
                                    foundDiv = div;
                                }
                            }
                        }
                        return foundDiv;
                    }
                    
                    const visibleImages = [];
                    for (let pos of gridPositions) {
                        const div = findVisibleDivAtPosition(pos.left, pos.top);
                        if (div) {
                            const img = div.querySelector('.captcha-img');
                            if (img) {
                                const imgSrc = img.src;
                                const onclick = img.getAttribute('onclick') || '';
                                const captchaIdMatch = onclick.match(/Select\('([^']+)'/);
                                const captchaId = captchaIdMatch ? captchaIdMatch[1] : '';
                                visibleImages.push({
                                    src: imgSrc,
                                    captchaId: captchaId
                                });
                            }
                        }
                    }
                    
                    return {
                        question: question,
                        images: visibleImages
                    };
                }
            """)
            
            if not captcha_data or not captcha_data.get('question') or len(captcha_data.get('images', [])) < 9:
                logger.error("❌ Failed to extract captcha data")
                return False
            
            question = captcha_data['question']
            images = captcha_data['images']
            
            logger.info(f"📋 Captcha question: {question}")
            logger.info(f"📷 Found {len(images)} visible images")
            
            # Send to NoCaptchaAI
            logger.info("🤖 Sending captcha to NoCaptchaAI...")
            try:
                from services.captcha_service import captcha_service
                
                # Extract base64 images
                image_bases = []
                for img in images:
                    if 'base64' in img['src']:
                        image_bases.append(img['src'].split(',')[1])
                
                if not image_bases:
                    logger.error("❌ No base64 images found")
                    return False
                
                solution = await captcha_service.solve_bls_images(image_bases)
                
                if not solution:
                    logger.error("❌ NoCaptchaAI failed to solve captcha")
                    return False
                
                logger.info(f"✅ NoCaptchaAI solution: {solution}")
                
            except Exception as e:
                logger.error(f"❌ Error calling NoCaptchaAI: {e}")
                return False
            
            # Click matching images
            logger.info("🖱️ Clicking matching images...")
            
            # Parse question to extract target number
            import re
            number_match = re.search(r'number\s+(\d+)', question, re.IGNORECASE)
            
            if not number_match:
                logger.error(f"❌ Could not parse target number from question: {question}")
                return False
            
            target_number = number_match.group(1)
            logger.info(f"🎯 Target number from question: {target_number}")
            
            # Get image texts from solution
            if isinstance(solution, list):
                image_texts = solution
            elif isinstance(solution, str):
                # Most numbers are 3 digits
                image_texts = [solution[i:i+3] for i in range(0, len(solution), 3)]
            else:
                logger.error(f"❌ Unexpected solution format: {type(solution)}")
                return False
            
            # Log all extracted texts with their grid positions and IDs
            logger.info(f"📋 All extracted image texts:")
            for idx, text in enumerate(image_texts):
                captcha_id = images[idx]['captchaId'] if idx < len(images) else 'unknown'
                logger.info(f"   Grid {idx} (ID: {captcha_id}): '{text}'")
            
            # Find indices of matching images
            correct_indices = []
            for idx, text in enumerate(image_texts):
                if text.strip() == target_number:
                    correct_indices.append(idx)
                    captcha_id = images[idx]['captchaId'] if idx < len(images) else 'unknown'
                    logger.info(f"✅ Grid position {idx} (ID: {captcha_id}) matches target: {text}")
            
            if not correct_indices:
                logger.warning(f"⚠️ No matching images found for target {target_number}")
                logger.info(f"📊 Summary: Target='{target_number}', Extracted={image_texts}")
                return False
            
            logger.info(f"✅ Found {len(correct_indices)} matching images")
            logger.info(f"📊 Will click {len(correct_indices)} out of 9 total images (only the ones matching '{target_number}')")
            
            # Click matching images using captcha IDs
            captcha_ids_to_click = []
            for idx in correct_indices:
                if idx < len(images):
                    captcha_id = images[idx]['captchaId']
                    captcha_ids_to_click.append(captcha_id)
                    logger.info(f"   Grid {idx} (text='{image_texts[idx]}') → Captcha ID: {captcha_id}")
            
            for captcha_id in captcha_ids_to_click:
                try:
                    clicked = await captcha_frame.evaluate(f"""
                        () => {{
                            const images = document.querySelectorAll('.captcha-img');
                            for (let img of images) {{
                                const onclick = img.getAttribute('onclick') || '';
                                if (onclick.includes('{captcha_id}')) {{
                                    console.log('Found image with ID {captcha_id}, dispatching mouse events...');
                                    const events = ['mouseover', 'mousedown', 'mouseup', 'click'];
                                    events.forEach(eventType => {{
                                        const event = new MouseEvent(eventType, {{
                                            bubbles: true,
                                            cancelable: true,
                                            view: window
                                        }});
                                        img.dispatchEvent(event);
                                    }});
                                    console.log('✅ Dispatched mouse events to image with captcha ID: {captcha_id}');
                                    return true;
                                }}
                            }}
                            console.log('❌ Could not find image with captcha ID: {captcha_id}');
                            return false;
                        }}
                    """)
                    await asyncio.sleep(0.5)
                    if clicked:
                        logger.info(f"✅ Clicked image with captcha ID: {captcha_id}")
                except Exception as e:
                    logger.warning(f"❌ Failed to click image with captcha ID {captcha_id}: {e}")
            
            # Wait before clicking submit
            await asyncio.sleep(1)
            
            # Click form submit button (which submits BOTH password and captcha together)
            logger.info("🖱️ Clicking form submit button to submit password + captcha...")
            submit_clicked = await captcha_frame.evaluate("""
                () => {
                    // Try to find the form submit button #btnVerify
                    let submitButton = document.querySelector('#btnVerify');
                    if (!submitButton) {
                        // Fallback to form submit button
                        submitButton = document.querySelector('#captchaForm button[type="submit"]');
                    }
                    if (submitButton) {
                        // Just click it normally - the onclick="return onSubmit()" handler will do the rest
                        submitButton.click();
                        return true;
                    }
                    return false;
                }
            """)
            
            if submit_clicked:
                logger.info("✅ Clicked form submit button")
            else:
                logger.warning("⚠️ Form submit button not found")
            
            await asyncio.sleep(2)  # Wait for submission
            
            # Verify captcha was solved (check if we navigated away from captcha page)
            captcha_solved = await self._verify_captcha_solved()
            
            if captcha_solved:
                logger.info("✅ Captcha solved successfully!")
                return True
            else:
                logger.warning("⚠️ Captcha verification failed")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error in automatic captcha solving: {e}")
            return False
    
    async def _verify_captcha_solved(self, max_wait: int = 15) -> bool:
        """Verify if captcha was successfully solved"""
        try:
            waited = 0
            check_interval = 0.5
            
            logger.info(f"🔍 Verifying captcha was solved (max {max_wait}s)...")
            
            while waited < max_wait:
                try:
                    # Check if we navigated away from captcha page (success)
                    current_url = self.page.url
                    if 'logincaptcha' not in current_url:
                        logger.info("✅ Navigated away from captcha page - login successful!")
                        await asyncio.sleep(1)
                        return True
                    
                    # Check if captcha images disappeared (captcha solved, but still on same page)
                    captcha_gone = await self.page.evaluate("""
                        () => {
                            const captchaImages = document.querySelectorAll('.captcha-img');
                            return captchaImages.length === 0;
                        }
                    """)
                    
                    if captcha_gone:
                        logger.info("✅ Captcha images disappeared - captcha solved!")
                        await asyncio.sleep(1)
                        return True
                    
                except Exception as e:
                    logger.debug(f"Check failed: {e}")
                
                await asyncio.sleep(check_interval)
                waited += check_interval
            
            logger.warning(f"⏱️ Verification timeout after {max_wait}s")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error verifying captcha: {e}")
            return False
    
    async def _wait_for_password_field(self, timeout: int = 30) -> bool:
        """Wait for password field to appear after captcha"""
        try:
            logger.info(f"⏳ Waiting for password field (max {timeout}s)...")
            
            # Use Playwright's is_visible() to find visible password fields
            password_selectors = [
                'input[type="password"].form-control.entry-disabled',
                'input[type="password"]'
            ]
            
            waited = 0
            check_interval = 0.5
            
            while waited < timeout:
                for selector in password_selectors:
                    try:
                        elements = await self.page.query_selector_all(selector)
                        for element in elements:
                            if await element.is_visible():
                                logger.info(f"✅ Password field found and visible: {selector}")
                                return True
                    except:
                        continue
                
                await asyncio.sleep(check_interval)
                waited += check_interval
            
            logger.error("❌ Password field not found or not visible")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error waiting for password field: {e}")
            return False
    
    async def _fill_password(self, password: str) -> bool:
        """Fill password field on captcha page"""
        try:
            # Find visible password field using the same approach as email
            logger.info("🔍 Searching for visible password input field using Playwright's is_visible()...")
            
            # Get all potential password fields
            potential_password_inputs = await self.page.query_selector_all('input[type="password"].form-control.entry-disabled')
            
            visible_field_id = None
            for input_element in potential_password_inputs:
                # Use Playwright's built-in is_visible() method
                if await input_element.is_visible():
                    visible_field_id = await input_element.get_attribute('id')
                    if visible_field_id:
                        break
            
            if visible_field_id:
                logger.info(f"✅ Found visible password input field with ID: {visible_field_id}")
                await self.page.fill(f'#{visible_field_id}', password)
                logger.info("✅ Filled password")
                await asyncio.sleep(1)
                return True
            else:
                logger.error("❌ Could not find any visible password input field")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error filling password: {e}")
            return False
    
    async def _extract_session_cookies(self) -> Dict[str, str]:
        """Extract session cookies from logged-in page"""
        try:
            cookies = await self.context.cookies()
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            logger.info(f"🍪 Extracted {len(cookie_dict)} cookies")
            return cookie_dict
            
        except Exception as e:
            logger.error(f"❌ Error extracting cookies: {e}")
            return {}
    
    async def _handle_waf_challenge(self) -> bool:
        """Handle AWS WAF challenge on login page"""
        try:
            logger.info("🔍 Detecting AWS WAF challenge...")
            
            # Wait for WAF challenge to appear
            await asyncio.sleep(3)
            
            # Check if challenge is present
            page_content = await self.page.content()
            
            if 'challenge-platform' in page_content or 'gokuProps' in page_content:
                logger.info("🛡️ AWS WAF challenge detected")
                
                try:
                    from awswaf.aws import AwsWaf
                    
                    logger.info("🔍 Extracting WAF challenge data...")
                    goku_props, host = AwsWaf.extract(page_content)
                    
                    if goku_props and host:
                        logger.info("✅ Extracted WAF challenge data")
                        
                        logger.info("🔄 Solving AWS WAF challenge...")
                        waf_token = AwsWaf.solve_challenge(goku_props, host)
                        logger.info(f"✅ Generated WAF token")
                        
                        # Add token as cookie
                        await self.context.add_cookies([{
                            'name': 'aws-waf-token',
                            'value': waf_token,
                            'domain': '.blsspainglobal.com',
                            'path': '/'
                        }])
                        logger.info("🔑 Added WAF token to cookies")
                        
                        # Reload page
                        logger.info("🔄 Reloading page with WAF token...")
                        await asyncio.sleep(2)
                        await self.page.reload(wait_until='domcontentloaded', timeout=60000)
                        await asyncio.sleep(3)
                        
                        logger.info("✅ WAF challenge solved")
                        return True
                    else:
                        logger.error("❌ Failed to extract WAF challenge data")
                        return False
                        
                except Exception as e:
                    logger.error(f"❌ Error solving WAF challenge: {e}")
                    return False
            else:
                logger.info("✅ No WAF challenge detected")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error handling WAF challenge: {e}")
            return False


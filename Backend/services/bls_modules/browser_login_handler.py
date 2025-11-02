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
            
            # Configure browser with proxy
            browser_options = {
                'headless': headless,
                'timeout': 30000
            }
            
            if proxy_url:
                # Parse proxy URL
                proxy_parts = self._parse_proxy(proxy_url)
                browser_options['proxy'] = proxy_parts
                logger.info(f"🌐 Using proxy: {proxy_parts['server']}")
            
            self.browser = await playwright.chromium.launch(**browser_options)
            self.context = await self.browser.new_context(
                viewport={'width': 1366, 'height': 768},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
            )
            self.page = await self.context.new_page()
            
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
            response = await self.page.goto(login_url, wait_until='domcontentloaded', timeout=60000)
            
            if not response or response.status != 200:
                logger.error(f"❌ Failed to load login page: {response.status if response else 'timeout'}")
                await self.browser.close()
                return False, {'error': 'Failed to load login page'}
            
            logger.info(f"✅ Login page loaded: {response.status}")
            
            # Handle AWS WAF challenge if present
            page_content = await self.page.content()
            if 'x-amzn-waf-action' in response.headers or 'challenge-platform' in page_content:
                logger.info("🛡️ AWS WAF challenge detected, solving...")
                waf_solved = await self._handle_waf_challenge()
                if not waf_solved:
                    logger.error("❌ Failed to solve AWS WAF challenge")
                    await self.browser.close()
                    return False, {'error': 'WAF challenge failed'}
            
            # Wait for page to fully load
            await asyncio.sleep(3)
            
            # Step 2: Fill email address
            logger.info("📝 Step 2: Filling email address...")
            email_filled = await self._fill_email(email)
            
            if not email_filled:
                logger.error("❌ Failed to fill email address")
                await self.browser.close()
                return False, {'error': 'Failed to fill email'}
            
            # Step 3: Click Verify button (this triggers captcha)
            logger.info("🔍 Step 3: Clicking Verify button...")
            await self._click_verify_button()
            
            # Step 4: Automatically solve captcha
            logger.info("🤖 Step 4: Automatically solving captcha with NoCaptchaAI...")
            captcha_result = await self._solve_captcha_automatically()
            
            if not captcha_result:
                logger.error("❌ Captcha solving failed or timed out")
                await self.browser.close()
                return False, {'error': 'Captcha solving failed'}
            
            logger.info("✅ Captcha solved successfully!")
            
            # Step 5: Wait for password field to appear
            logger.info("🔒 Step 5: Waiting for password field...")
            password_appeared = await self._wait_for_password_field()
            
            if not password_appeared:
                logger.error("❌ Password field did not appear")
                await self.browser.close()
                return False, {'error': 'Password field not found'}
            
            # Step 6: Fill password and submit
            logger.info("🔐 Step 6: Filling password and submitting...")
            login_success = await self._fill_password_and_submit(password)
            
            if not login_success:
                logger.error("❌ Login failed")
                await self.browser.close()
                return False, {'error': 'Login failed'}
            
            logger.info("✅ Login successful!")
            
            # Step 7: Extract session cookies
            logger.info("🍪 Step 7: Extracting session cookies...")
            session_cookies = await self._extract_session_cookies()
            
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
            # Try to find email input field
            # The user said: <input autocomplete="off" id="ldmao" name="ldmao"
            email_selectors = [
                '#ldmao',
                'input[name="ldmao"]',
                'input[type="text"]',
                'input[name*="email"]',
                'input[id*="email"]'
            ]
            
            for selector in email_selectors:
                try:
                    email_field = await self.page.wait_for_selector(selector, timeout=5000)
                    if email_field:
                        await email_field.fill(email)
                        logger.info(f"✅ Filled email: {email}")
                        await asyncio.sleep(1)  # Small delay
                        return True
                except:
                    continue
            
            logger.error("❌ Could not find email input field")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error filling email: {e}")
            return False
    
    async def _click_verify_button(self):
        """Click the Verify button"""
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
                        await asyncio.sleep(2)  # Wait for captcha to load
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
            
            try:
                # Wait for iframe to be present
                iframe_element = await self.page.wait_for_selector('iframe.k-content-frame', timeout=10000)
                logger.info("✅ Found captcha iframe")
            except Exception as e:
                logger.error(f"❌ Captcha iframe not found: {e}")
                return False
            
            # Get the frame from the iframe element
            captcha_frame = await iframe_element.content_frame()
            if not captcha_frame:
                logger.error("❌ Could not access iframe content")
                return False
            
            logger.info("✅ Switched to captcha iframe context")
            
            # Wait for captcha to fully load (same logic as registration)
            logger.info("⏳ Waiting for captcha to fully load...")
            await asyncio.sleep(5)  # Wait for 54 images + CSS + positioning
            
            # Wait additional time
            logger.info("⏳ Waiting 5 more seconds to ensure iframe is fully settled...")
            await asyncio.sleep(5)
            logger.info("✅ Captcha iframe should now be fully ready!")
            
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
                
                solution = await captcha_service.solve_bls_images(question, image_bases)
                
                if not solution:
                    logger.error("❌ NoCaptchaAI failed to solve captcha")
                    return False
                
                logger.info(f"✅ NoCaptchaAI solution: {solution}")
                
            except Exception as e:
                logger.error(f"❌ Error calling NoCaptchaAI: {e}")
                return False
            
            # Click matching images
            logger.info("🖱️ Clicking matching images...")
            target_number = question.strip()
            
            # Get image texts from solution
            if isinstance(solution, str):
                # Most numbers are 3 digits
                image_texts = [solution[i:i+3] for i in range(0, len(solution), 3)]
            else:
                logger.error(f"❌ Unexpected solution format: {type(solution)}")
                return False
            
            # Find indices of matching images
            correct_indices = []
            for idx, text in enumerate(image_texts):
                if text.strip() == target_number:
                    correct_indices.append(idx)
            
            if not correct_indices:
                logger.warning(f"⚠️ No matching images found for target {target_number}")
                return False
            
            # Click matching images using captcha IDs
            captcha_ids_to_click = []
            for idx in correct_indices:
                if idx < len(images):
                    captcha_id = images[idx]['captchaId']
                    captcha_ids_to_click.append(captcha_id)
                    logger.info(f"   Will click captcha ID: {captcha_id}")
            
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
            
            # Click submit button
            logger.info("🖱️ Clicking captcha submit button...")
            submit_clicked = await captcha_frame.evaluate("""
                () => {
                    let submitButton = document.querySelector('#submit');
                    if (!submitButton) {
                        submitButton = document.querySelector('#captchaForm .img-actions > div:nth-child(3)');
                    }
                    if (!submitButton) {
                        submitButton = document.querySelector('.img-action.img-active[title="Submit Selection"]');
                    }
                    if (submitButton) {
                        const events = ['mouseover', 'mousedown', 'mouseup', 'click'];
                        events.forEach(eventType => {
                            const event = new MouseEvent(eventType, {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            submitButton.dispatchEvent(event);
                        });
                        return true;
                    }
                    return false;
                }
            """)
            
            if submit_clicked:
                logger.info("✅ Clicked submit button")
            else:
                logger.warning("⚠️ Submit button not found")
            
            await asyncio.sleep(2)  # Wait for submission
            
            # Verify captcha was solved
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
                    # Check if password field appeared (means captcha passed)
                    has_password_field = await self.page.evaluate("""
                        () => {
                            const passwordField = document.querySelector('input[type="password"]');
                            return passwordField !== null;
                        }
                    """)
                    
                    if has_password_field:
                        logger.info("✅ Password field appeared - captcha solved!")
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
            
            password_selectors = [
                'input[type="password"]',
                'input[name*="password"]',
                'input[id*="password"]'
            ]
            
            for selector in password_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=timeout)
                    logger.info(f"✅ Password field found: {selector}")
                    return True
                except:
                    continue
            
            logger.error("❌ Password field not found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error waiting for password field: {e}")
            return False
    
    async def _fill_password_and_submit(self, password: str) -> bool:
        """Fill password field and submit login form"""
        try:
            # Find password field
            password_field = await self.page.query_selector('input[type="password"]')
            if not password_field:
                logger.error("❌ Password field not found")
                return False
            
            await password_field.fill(password)
            logger.info("✅ Filled password")
            await asyncio.sleep(1)
            
            # Find and click submit button
            submit_selectors = [
                'button[type="submit"]',
                'button.btn-primary',
                'input[type="submit"]',
                'button#btnLogin'
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = await self.page.query_selector(selector)
                    if submit_button:
                        await submit_button.click()
                        logger.info("✅ Clicked submit button")
                        await asyncio.sleep(3)
                        return True
                except:
                    continue
            
            logger.error("❌ Submit button not found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error filling password and submitting: {e}")
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


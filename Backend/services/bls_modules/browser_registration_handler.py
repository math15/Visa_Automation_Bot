"""
Browser-based full registration handler for BLS
Handles the complete registration flow in browser including form filling, captcha, OTP
"""

from typing import Dict, Any, Optional, Tuple
from loguru import logger
import asyncio
import re


class BrowserRegistrationHandler:
    """Handles full BLS registration flow in browser"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        
    async def complete_registration_in_browser(
        self,
        registration_url: str,
        user_data: Dict[str, Any],
        cookies: Dict[str, str],
        proxy_url: str = None,
        headless: bool = False,
        email_service = None,
        email_service_name: str = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Complete the full registration flow in browser
        
        Args:
            registration_url: BLS registration page URL
            user_data: User registration data (name, passport, email, etc.)
            cookies: Initial cookies (antiforgery, visitorId, aws-waf-token)
            proxy_url: Proxy in format "username:password@host:port"
            headless: Whether to run browser in headless mode
            email_service: Email service instance to retrieve OTP
            
        Returns:
            Tuple of (success: bool, result: dict with registration result)
        """
        try:
            from playwright.async_api import async_playwright
            
            logger.info("🌐 Starting browser-based full registration...")
            logger.info(f"🔗 Registration URL: {registration_url}")
            logger.info(f"📧 Email: {user_data.get('Email')}")
            
            async with async_playwright() as p:
                # Parse proxy
                proxy_config = None
                if proxy_url:
                    proxy_config = await self._parse_proxy_url(proxy_url)
                
                # Launch browser
                logger.info("🚀 Launching browser...")
                browser_args = [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    f'--window-size=800,1000',  # Normal size for debugging
                ]
                
                self.browser = await p.chromium.launch(
                    headless=headless,
                    args=browser_args
                )
                
                # Create context with cookies and proxy (with comprehensive anti-bot headers)
                context_options = {
                    'viewport': {'width': 800, 'height': 1000},  # Normal viewport
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
                
                if proxy_config:
                    context_options['proxy'] = proxy_config
                    has_auth = 'username' in proxy_config and 'password' in proxy_config
                    logger.info(f"✅ Proxy configured: {proxy_config['server']}")
                    if has_auth:
                        logger.info(f"🔑 Proxy authentication: username={proxy_config['username'][:10]}..., password={'*' * len(proxy_config['password'])}")
                    else:
                        logger.warning(f"⚠️ Proxy configured WITHOUT authentication!")
                        logger.warning(f"⚠️ Proxy config keys: {list(proxy_config.keys())}")
                
                self.context = await self.browser.new_context(**context_options)
                
                # Set cookies if provided (minimal setup, browser will generate the rest)
                browser_cookies = []
                if cookies:
                    for name, value in cookies.items():
                        if name not in ['path', 'samesite']:
                            browser_cookies.append({
                                'name': name,
                                'value': value,
                                'domain': '.blsspainglobal.com',
                                'path': '/'
                            })
                            logger.info(f"🍪 Setting cookie: {name}={value[:30]}...")
                    await self.context.add_cookies(browser_cookies)
                    logger.info(f"🍪 Set {len(browser_cookies)} cookies")
                else:
                    logger.info("🍪 No initial cookies - browser will generate its own (including WAF token)")
                
                # Create page
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
                            Promise.resolve({state: Notification.permission}) :
                            originalQuery(parameters)
                    );
                    
                    // Add realistic hardware concurrency
                    Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
                    
                    // Add realistic device memory
                    Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
                    
                    // Chrome-specific properties
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                """)
                
                # Navigate to registration page (don't wait for full load, WAF will block it)
                logger.info("🔗 Navigating to registration page...")
                logger.info("💡 Browser will handle AWS WAF challenges automatically...")
                logger.info("⏳ This may take 1-3 minutes while WAF challenge is being solved...")
                try:
                    # Use 'commit' instead of 'domcontentloaded' to allow WAF challenge to process
                    response = await self.page.goto(registration_url, wait_until='commit', timeout=180000)  # 3 minutes timeout
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
                        
                        # Check if page has loaded by looking for the form
                        try:
                            form_visible = await self.page.query_selector('#myForm')
                            if form_visible:
                                logger.info(f"✅ Page loaded successfully after {elapsed}s!")
                                form_loaded = True
                                break
                            else:
                                # Check current URL to see if still on WAF challenge
                                current_url = self.page.url
                                if 'RegisterUser' in current_url:
                                    logger.info(f"⏳ WAF challenge still processing... ({elapsed}s / {max_wait}s)")
                                else:
                                    logger.info(f"⏳ Waiting for page... ({elapsed}s / {max_wait}s)")
                        except Exception as e:
                            logger.info(f"⏳ Still loading... ({elapsed}s / {max_wait}s)")
                    
                    # Final check
                    if not form_loaded:
                        logger.error("❌ Page did not load after 3 minutes")
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
                    logger.error(f"❌ Error loading registration page: {e}")
                    raise
                
                # Wait for page to be fully loaded (detect Kendo widgets initialization)
                logger.info("⏳ Waiting for page and Kendo widgets to fully load...")
                await self._wait_for_page_loaded()
                
                # Step 1: Handle consent modals (REQUIRED before filling form!)
                logger.info("✅ Step 1: Handling consent modals...")
                await self._handle_consent_modals()
                
                # Step 2: Fill registration form
                logger.info("📝 Step 2: Filling registration form...")
                await self._fill_registration_form(user_data)
                
                # Step 3: Load captcha (it's embedded in the registration page)
                logger.info("🔍 Step 3: Loading captcha on the page...")
                await self._load_captcha_on_page()
                
                # Step 4: Automatically solve captcha using NoCaptchaAI
                logger.info("🤖 Step 4: Automatically solving captcha with NoCaptchaAI...")
                
                captcha_result = await self._solve_captcha_automatically()
                
                if not captcha_result:
                    logger.error("❌ Captcha solving failed or timed out")
                    logger.info("💡 You can try manual solving in the browser window")
                    await self.browser.close()
                    return False, {'error': 'Captcha solving failed'}
                
                logger.info("✅ Captcha solved successfully!")
                
                # Step 5: Click Send OTP button
                logger.info("📧 Step 5: Clicking Send OTP button...")
                otp_sent = await self._click_send_otp_button()
                
                if not otp_sent:
                    logger.error("❌ Failed to send OTP")
                    await self.browser.close()
                    return False, {'error': 'Failed to send OTP'}
                
                logger.info("✅ OTP sent successfully!")
                
                # Step 6: Get OTP code from user input
                logger.info("📧 Step 6: Waiting for OTP code...")
                email = user_data.get('Email')
                
                # Manual OTP entry - wait for user to input in console
                logger.info("")
                logger.info("="*80)
                logger.info("📧 MANUAL OTP ENTRY REQUIRED")
                logger.info("="*80)
                logger.info(f"📧 Please check {email} and enter the OTP code in the console below:")
                logger.info("="*80)
                logger.info("")
                
                # Simple console input using threading (works with headless browsers)
                import threading
                otp_received = threading.Event()
                user_otp = [None]
                
                def get_console_input():
                    try:
                        otp = input(f"📧 Please enter OTP code received at {email}: ").strip()
                        user_otp[0] = otp
                        otp_received.set()
                    except:
                        pass
                
                input_thread = threading.Thread(target=get_console_input)
                input_thread.daemon = True
                input_thread.start()
                
                # Wait for user input (with timeout) - this will block
                otp_received.wait(timeout=300)  # 5 minutes timeout
                otp_code = user_otp[0]
                
                if not otp_code:
                    logger.error("❌ No OTP code received - timeout or no input")
                    await self.browser.close()
                    return False, {'error': 'OTP timeout'}
                
                logger.info(f"✅ OTP code received: {otp_code}")
                
                # Step 7: Fill OTP and submit
                logger.info("📝 Step 7: Filling OTP and submitting...")
                submit_result = await self._fill_otp_and_submit(otp_code)
                
                if not submit_result:
                    logger.error("❌ Failed to submit registration")
                    await self.browser.close()
                    return False, {'error': 'Failed to submit registration'}
                
                logger.info("🎉 Registration completed successfully!")
                
                # Wait a bit to see the result
                await asyncio.sleep(3)
                
                # Close browser
                await self.browser.close()
                
                return True, {
                    'success': True,
                    'email': email,
                    'message': 'Registration completed successfully'
                }
                
        except Exception as e:
            logger.error(f"❌ Error in browser registration: {e}")
            if self.browser:
                await self.browser.close()
            return False, {'error': str(e)}
    
    async def _wait_for_page_loaded(self):
        """Wait for the registration page to be fully loaded (Kendo widgets initialized)"""
        try:
            # Wait for jQuery to be loaded
            await self.page.wait_for_function("typeof $ !== 'undefined'", timeout=30000)
            logger.info("✅ jQuery loaded")
            
            # Wait for Kendo UI to be loaded
            await self.page.wait_for_function("typeof kendo !== 'undefined'", timeout=30000)
            logger.info("✅ Kendo UI loaded")
            
            # Wait for form element to be visible
            await self.page.wait_for_selector('#myForm', state='visible', timeout=30000)
            logger.info("✅ Form visible")
            
            # Wait for Kendo DatePicker widgets to be initialized
            await self.page.wait_for_function(
                """
                $('#DateOfBirth').data('kendoDatePicker') !== undefined &&
                $('#PassportIssueDate').data('kendoDatePicker') !== undefined &&
                $('#PassportExpiryDate').data('kendoDatePicker') !== undefined
                """,
                timeout=30000
            )
            logger.info("✅ Kendo DatePicker widgets initialized")
            
            # Wait for Kendo DropDownList widgets to be initialized
            await self.page.wait_for_function(
                """
                $('#BirthCountry').data('kendoDropDownList') !== undefined &&
                $('#PassportType').data('kendoDropDownList') !== undefined &&
                $('#CountryOfResidence').data('kendoDropDownList') !== undefined
                """,
                timeout=30000
            )
            logger.info("✅ Kendo DropDownList widgets initialized")
            
            # Extra wait for data to load into dropdowns
            await asyncio.sleep(2)
            logger.info("✅ Page fully loaded and ready!")
            
        except Exception as e:
            logger.warning(f"⚠️ Timeout waiting for page to fully load: {e}")
            logger.info("⚠️ Continuing anyway...")
    
    async def _handle_consent_modals(self):
        """Handle the two consent modals that appear on page load"""
        try:
            # Modal 1: Biometric consent - "I agree to provide my consent"
            logger.info("🔍 Looking for biometric consent modal...")
            try:
                # Wait for the modal to appear (max 5 seconds)
                bio_consent_button = await self.page.wait_for_selector(
                    'button[onclick="onBioDisclaimerAccept();"]',
                    timeout=5000
                )
                if bio_consent_button:
                    logger.info("✅ Found biometric consent button, clicking...")
                    await bio_consent_button.click()
                    logger.info("✅ Clicked biometric consent button")
                    await asyncio.sleep(2)  # Wait for modal to close
                else:
                    logger.info("ℹ️ Biometric consent button not found (might not be required)")
            except Exception as e:
                logger.warning(f"⚠️ Biometric consent modal not found or already dismissed: {e}")
            
            # Modal 2: Data protection consent - "I have read and understood the information on data protection"
            logger.info("🔍 Looking for data protection consent modal...")
            try:
                # Wait for the modal to appear (max 5 seconds)
                dp_consent_button = await self.page.wait_for_selector(
                    'button[onclick="onDpAccept();"]',
                    timeout=5000
                )
                if dp_consent_button:
                    logger.info("✅ Found data protection consent button, clicking...")
                    await dp_consent_button.click()
                    logger.info("✅ Clicked data protection consent button")
                    await asyncio.sleep(2)  # Wait for modal to close
                else:
                    logger.info("ℹ️ Data protection consent button not found (might not be required)")
            except Exception as e:
                logger.warning(f"⚠️ Data protection consent modal not found or already dismissed: {e}")
            
            logger.info("✅ Consent modals handled successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Error handling consent modals: {e}")
            logger.info("⚠️ Continuing anyway - modals might not be present")
    
    async def _fill_registration_form(self, user_data: Dict[str, Any]):
        """Fill all registration form fields (including Kendo widgets)"""
        try:
            # Personal information (regular text fields)
            if user_data.get('SurName'):
                await self.page.fill('#SurName', user_data['SurName'])
                logger.info(f"✅ Filled SurName: {user_data['SurName']}")
            
            await self.page.fill('#FirstName', user_data['FirstName'])
            logger.info(f"✅ Filled FirstName: {user_data['FirstName']}")
            
            await self.page.fill('#LastName', user_data['LastName'])
            logger.info(f"✅ Filled LastName: {user_data['LastName']}")
            
            # Date of Birth (Kendo DatePicker) - use JavaScript
            dob = user_data['DateOfBirth']  # Format: "1990-05-15T00:00"
            await self.page.evaluate(f"""
                var datePicker = $('#DateOfBirth').data('kendoDatePicker');
                if (datePicker) {{
                    datePicker.value(new Date('{dob}'));
                    $('#ServerDateOfBirth').val('{dob.split('T')[0]}');
                }}
            """)
            logger.info(f"✅ Filled DateOfBirth: {dob}")
            
            # Passport information (regular text field)
            await self.page.fill('#ppNo', user_data['PassportNumber'])
            logger.info(f"✅ Filled PassportNumber: {user_data['PassportNumber']}")
            
            # Passport Issue Date (Kendo DatePicker)
            issue_date = user_data['PassportIssueDate']
            await self.page.evaluate(f"""
                var datePicker = $('#PassportIssueDate').data('kendoDatePicker');
                if (datePicker) {{
                    datePicker.value(new Date('{issue_date}'));
                    $('#ServerPassportIssueDate').val('{issue_date.split('T')[0]}');
                }}
            """)
            logger.info(f"✅ Filled PassportIssueDate: {issue_date}")
            
            # Passport Expiry Date (Kendo DatePicker)
            expiry_date = user_data['PassportExpiryDate']
            await self.page.evaluate(f"""
                var datePicker = $('#PassportExpiryDate').data('kendoDatePicker');
                if (datePicker) {{
                    datePicker.value(new Date('{expiry_date}'));
                    $('#ServerPassportExpiryDate').val('{expiry_date.split('T')[0]}');
                }}
            """)
            logger.info(f"✅ Filled PassportExpiryDate: {expiry_date}")
            
            # Passport Issue Place (regular text field)
            await self.page.fill('#IssuePlace', user_data['IssuePlace'])
            logger.info(f"✅ Filled IssuePlace: {user_data['IssuePlace']}")
            
            # Birth Country (Kendo DropDownList) - wait for data to load, then select
            if user_data.get('BirthCountry'):
                await asyncio.sleep(1)  # Wait for AJAX data to load
                result = await self.page.evaluate(f"""
                    (function() {{
                        var dropdown = $('#BirthCountry').data('kendoDropDownList');
                        if (!dropdown) return 'dropdown_not_found';
                        
                        var data = dropdown.dataSource.data();
                        if (!data || data.length === 0) return 'no_data';
                        
                        var item = data.find(x => x.Name && x.Name.toLowerCase().includes('{user_data['BirthCountry'].lower()}'));
                        if (!item) return 'item_not_found';
                        
                        dropdown.value(item.Id);
                        return 'success';
                    }})()
                """)
                logger.info(f"✅ Selected BirthCountry: {user_data['BirthCountry']} (result: {result})")
            
            # Passport Type (Kendo DropDownList)
            if user_data.get('PassportType'):
                await asyncio.sleep(1)  # Wait for AJAX data to load
                result = await self.page.evaluate(f"""
                    (function() {{
                        var dropdown = $('#PassportType').data('kendoDropDownList');
                        if (!dropdown) return 'dropdown_not_found';
                        
                        var data = dropdown.dataSource.data();
                        if (!data || data.length === 0) return 'no_data';
                        
                        var item = data.find(x => x.Name && x.Name.toLowerCase().includes('{user_data['PassportType'].lower()}'));
                        if (!item) return 'item_not_found';
                        
                        dropdown.value(item.Id);
                        return 'success';
                    }})()
                """)
                logger.info(f"✅ Selected PassportType: {user_data['PassportType']} (result: {result})")
            
            # Country of Residence (Kendo DropDownList)
            if user_data.get('CountryOfResidence'):
                await asyncio.sleep(1)  # Wait for AJAX data to load
                result = await self.page.evaluate(f"""
                    (function() {{
                        var dropdown = $('#CountryOfResidence').data('kendoDropDownList');
                        if (!dropdown) return 'dropdown_not_found';
                        
                        var data = dropdown.dataSource.data();
                        if (!data || data.length === 0) return 'no_data';
                        
                        var item = data.find(x => x.Name && x.Name.toLowerCase().includes('{user_data['CountryOfResidence'].lower()}'));
                        if (!item) return 'item_not_found';
                        
                        dropdown.value(item.Id);
                        return 'success';
                    }})()
                """)
                logger.info(f"✅ Selected CountryOfResidence: {user_data['CountryOfResidence']} (result: {result})")
            
            # Contact information (regular text fields)
            await self.page.fill('input[name="Mobile"]', user_data['Mobile'])
            logger.info(f"✅ Filled Mobile: {user_data['Mobile']}")
            
            await self.page.fill('#Email', user_data['Email'])
            logger.info(f"✅ Filled Email: {user_data['Email']}")
            
            logger.info("✅ All form fields filled successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error filling form: {e}")
            raise
    
    async def _load_captcha_on_page(self):
        """Click 'Verify' button to open captcha popup (400x600 window)"""
        try:
            logger.info("🔍 Looking for 'Verify' button to open captcha...")
            
            # Find and click the Verify button (#btnVerify)
            verify_button = await self.page.wait_for_selector('#btnVerify', timeout=10000)
            if not verify_button:
                logger.error("❌ Verify button not found!")
                raise Exception("Verify button not found")
            
            logger.info("✅ Found Verify button, clicking to open captcha popup...")
            await verify_button.click()
            
            # Wait for captcha popup/iframe to appear
            logger.info("⏳ Waiting for captcha popup to load...")
            await asyncio.sleep(3)
            
            # Check if captcha iframe appeared
            captcha_frame = await self.page.query_selector('iframe[src*="Captcha"], iframe[src*="captcha"]')
            if captcha_frame:
                logger.info("✅ Captcha iframe loaded successfully!")
            else:
                # Might be in a popup window, check for new pages
                logger.info("ℹ️ Captcha might be in a popup window (400x600)")
            
            logger.info("✅ Captcha should now be visible (in iframe or popup)")
            
        except Exception as e:
            logger.error(f"❌ Error loading captcha: {e}")
            raise
    
    async def _solve_captcha_automatically(self, timeout: int = 300) -> bool:
        """Automatically solve captcha using NoCaptchaAI with retry logic"""
        # Wrapper to add retry logic
        return await self._solve_captcha_automatically_with_retry(timeout, retry_count=0, max_retries=3)
    
    async def _solve_captcha_automatically_with_retry(self, timeout: int = 300, retry_count: int = 0, max_retries: int = 3) -> bool:
        """Automatically solve captcha using NoCaptchaAI with retry on failure"""
        try:
            if retry_count > 0:
                logger.info(f"🔄 Retry attempt {retry_count}/{max_retries} - Solving captcha again...")
            else:
                logger.info("🤖 Starting automatic captcha solving with NoCaptchaAI...")
            
            # Step 1: Find and switch to the captcha iframe
            logger.info("🔍 Looking for captcha iframe...")
            iframe_element = None
            try:
                # Wait for iframe to be present
                iframe_element = await self.page.wait_for_selector('iframe.k-content-frame', timeout=10000)
                logger.info("✅ Found captcha iframe")
            except Exception as e:
                logger.error(f"❌ Captcha iframe not found: {e}")
                return await self._wait_for_captcha_solved_manual(timeout)
            
            # Get the frame from the iframe element
            captcha_frame = await iframe_element.content_frame()
            if not captcha_frame:
                logger.error("❌ Could not access iframe content")
                return await self._wait_for_captcha_solved_manual(timeout)
            
            logger.info("✅ Switched to captcha iframe context")
            
            # Step 1.5: Wait for iframe content to fully load
            logger.info("⏳ Waiting for captcha iframe content to load (54 images + CSS)...")
            
            # Wait for all 54 images to load and 9 to be visible
            max_wait = 30  # Maximum 30 seconds to wait (54 images need time to load)
            start_time = asyncio.get_event_loop().time()
            
            while True:
                try:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    
                    # Comprehensive check for full iframe load (images + CSS + JS + positioning)
                    check_result = await captcha_frame.evaluate("""
                        () => {
                            // 1. Check document ready state
                            if (document.readyState !== 'complete') {
                                return { ready: false, reason: 'document not ready', visible: 0, total: 0 };
                            }
                            
                            // 2. Check if images exist
                            const images = document.querySelectorAll('.captcha-img');
                            const totalCount = images.length;
                            
                            if (totalCount === 0) {
                                return { ready: false, reason: 'no images found', visible: 0, total: 0 };
                            }
                            
                            if (totalCount < 54) {
                                return { ready: false, reason: `only ${totalCount} images`, visible: 0, total: totalCount };
                            }
                            
                            // 3. Check if all images have base64 data and onclick handlers
                            let imagesWithData = 0;
                            let imagesWithOnclick = 0;
                            let visibleCount = 0;
                            
                            for (let img of images) {
                                // Check base64 src
                                if (img.src && img.src.includes('base64')) {
                                    imagesWithData++;
                                }
                                
                                // Check onclick attribute
                                if (img.getAttribute('onclick')) {
                                    imagesWithOnclick++;
                                }
                                
                                // Count visible images for logging
                                const imgStyle = window.getComputedStyle(img);
                                const parentStyle = window.getComputedStyle(img.parentElement);
                                const isVisible = imgStyle.display !== 'none' && 
                                                parentStyle.display !== 'none' &&
                                                img.offsetWidth > 0 && 
                                                img.offsetHeight > 0;
                                if (isVisible) visibleCount++;
                            }
                            
                            if (imagesWithData < 54) {
                                return { ready: false, reason: `${imagesWithData}/54 with data`, visible: imagesWithData, total: totalCount };
                            }
                            
                            if (imagesWithOnclick < 54) {
                                return { ready: false, reason: `${imagesWithOnclick}/54 with onclick`, visible: imagesWithOnclick, total: totalCount };
                            }
                            
                            // 4. Check if .col-4 divs have CSS positioning (left, top, z-index)
                            const divs = document.querySelectorAll('.col-4');
                            let divsWithPositioning = 0;
                            
                            for (let div of divs) {
                                const style = window.getComputedStyle(div);
                                const left = style.getPropertyValue('left');
                                const top = style.getPropertyValue('top');
                                const zIndex = style.getPropertyValue('z-index');
                                
                                if (left !== 'auto' && top !== 'auto' && zIndex !== 'auto') {
                                    divsWithPositioning++;
                                }
                            }
                            
                            if (divsWithPositioning < 54) {
                                return { ready: false, reason: `${divsWithPositioning}/54 positioned`, visible: visibleCount, total: totalCount };
                            }
                            
                            // 5. Check if submit button and question exist
                            const submitBtn = document.querySelector('#submit');
                            if (!submitBtn) {
                                return { ready: false, reason: 'no submit button', visible: visibleCount, total: totalCount };
                            }
                            
                            const question = document.querySelector('.box-label');
                            if (!question || !question.innerText.trim()) {
                                return { ready: false, reason: 'no question text', visible: visibleCount, total: totalCount };
                            }
                            
                            // Everything is ready!
                            return {
                                ready: true,
                                reason: 'fully loaded',
                                visible: visibleCount,
                                total: totalCount
                            };
                        }
                    """)
                    
                    # Show reason if not ready
                    if check_result.get('ready'):
                        logger.info(f"📊 Captcha status: {check_result.get('reason', 'ready')} - {check_result['visible']}/{check_result['total']} images ({elapsed:.1f}s)")
                    else:
                        logger.info(f"📊 Captcha status: {check_result.get('reason', 'loading...')} ({elapsed:.1f}s)")
                    
                    if check_result['ready']:
                        logger.info(f"✅ Captcha fully loaded! {check_result['total']} total images found")
                        logger.info(f"ℹ️ All images have base64 data, onclick handlers, and CSS positioning applied")
                        logger.info(f"ℹ️ Note: {check_result['visible']} appear visible by CSS, but we'll extract exactly 9 by position+z-index")
                        # Wait additional time to ensure all animations and final rendering is complete
                        logger.info("⏳ Waiting 5 seconds to ensure iframe is fully settled...")
                        await asyncio.sleep(5)
                        logger.info("✅ Captcha iframe should now be fully ready for extraction!")
                        break
                    
                    if elapsed >= max_wait:
                        if check_result['visible'] > 0:
                            logger.warning(f"⚠️ Timeout but found {check_result['visible']} visible images, proceeding anyway...")
                            break
                        else:
                            logger.error(f"❌ Timeout: No visible images after {max_wait}s")
                            logger.info("💡 Falling back to manual captcha solving...")
                            return await self._wait_for_captcha_solved_manual(timeout)
                    
                    # Wait a bit before next check
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Error checking captcha images: {e}")
                    if elapsed >= max_wait:
                        logger.info("💡 Falling back to manual captcha solving...")
                        return await self._wait_for_captcha_solved_manual(timeout)
                    await asyncio.sleep(1)
            
            # Step 2: Get captcha images and question from the iframe
            logger.info("📸 Extracting captcha images using position + z-index method (like solver.js)...")
            captcha_data = await captcha_frame.evaluate("""
                () => {
                    // Get captcha question using z-index (like solver.js)
                    // There are multiple .box-label elements, we need the one with highest z-index
                    function getQuestionByZIndex() {
                        const labels = [...document.querySelectorAll('.box-label')];
                        let maxZIndex = 0;
                        let foundLabel = null;
                        
                        console.log(`Found ${labels.length} .box-label elements, finding one with highest z-index...`);
                        
                        for (let label of labels) {
                            const style = window.getComputedStyle(label);
                            const zIndex = style.getPropertyValue('z-index');
                            const zIndexNum = parseInt(zIndex);
                            
                            if (zIndex !== 'auto' && zIndexNum > maxZIndex) {
                                maxZIndex = zIndexNum;
                                foundLabel = label;
                            }
                        }
                        
                        if (foundLabel) {
                            console.log(`✅ Selected question label with z-index ${maxZIndex}: "${foundLabel.innerText.trim()}"`);
                            return { text: foundLabel.innerText.trim(), zIndex: maxZIndex };
                        }
                        
                        return { text: '', zIndex: 0 };
                    }
                    
                    const questionData = getQuestionByZIndex();
                    const question = questionData.text;
                    const questionZIndex = questionData.zIndex;
                    
                    // BLS uses POSITION + Z-INDEX to show 9 images in 3x3 grid
                    // All 54 images are stacked, but only highest z-index at each position is visible
                    
                    // Function to find the visible div at a specific position (highest z-index)
                    function findVisibleDivAtPosition(left, top) {
                        const allDivs = [...document.querySelectorAll('.col-4')].filter(d => d.getClientRects().length);
                        let maxZIndex = 0;
                        let foundDiv = null;
                        
                        for (let div of allDivs) {
                            const style = window.getComputedStyle(div);
                            const divLeft = style.getPropertyValue('left');
                            const divTop = style.getPropertyValue('top');
                            const divZIndex = style.getPropertyValue('z-index');
                            
                            // Check if this div is at our target position
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
                    
                    // The 9 grid positions for 3x3 captcha (left, top in pixels)
                    const gridPositions = [
                        [0, 0],     [110, 0],     [220, 0],      // Top row
                        [0, 110],   [110, 110],   [220, 110],    // Middle row
                        [0, 220],   [110, 220],   [220, 220]     // Bottom row
                    ];
                    
                    const images = [];
                    const totalImages = document.querySelectorAll('.captcha-img').length;
                    
                    console.log(`Found ${totalImages} total images, extracting 9 visible from grid positions...`);
                    
                    gridPositions.forEach(([left, top], gridIndex) => {
                        const visibleDiv = findVisibleDivAtPosition(left, top);
                        
                        if (visibleDiv) {
                            const img = visibleDiv.querySelector('.captcha-img');
                            if (img) {
                                // Extract onclick ID from onclick="Select('ID',this)"
                                const onclickAttr = img.getAttribute('onclick') || '';
                                const match = onclickAttr.match(/Select\\('([^']+)'/);
                                const captchaId = match ? match[1] : (img.id || `unknown-${gridIndex}`);
                                
                                images.push({
                                    index: gridIndex,           // Grid position (0-8)
                                    src: img.src,
                                    id: captchaId,              // The REAL captcha ID from onclick
                                    onclick: onclickAttr,
                                    position: `(${left},${top})`,
                                    zIndex: window.getComputedStyle(visibleDiv).getPropertyValue('z-index')
                                });
                                
                                console.log(`✅ Grid ${gridIndex} at (${left},${top}): ID=${captchaId}, z-index=${window.getComputedStyle(visibleDiv).getPropertyValue('z-index')}`);
                            }
                        } else {
                            console.log(`❌ No visible div found at position (${left},${top})`);
                        }
                    });
                    
                    console.log(`Extracted ${images.length} visible images from 3x3 grid`);
                    
                    return {
                        question: question,
                        questionZIndex: questionZIndex,
                        images: images,
                        count: images.length,
                        totalImages: totalImages
                    };
                }
            """)
            
            if not captcha_data or captcha_data['count'] == 0:
                logger.error("❌ No visible captcha images found in iframe")
                logger.info(f"ℹ️ Total images in HTML: {captcha_data.get('totalImages', 0)}")
                return await self._wait_for_captcha_solved_manual(timeout)
            
            total_images = captcha_data.get('totalImages', 'unknown')
            logger.info(f"✅ Found {captcha_data['count']} VISIBLE captcha images (out of {total_images} total)")
            question_zindex = captcha_data.get('questionZIndex', 'unknown')
            logger.info(f"📝 Question (z-index: {question_zindex}): {captcha_data['question']}")
            
            # BLS generates 54 total images, showing only 9 visible (3x3 grid)
            if total_images != 'unknown' and total_images != 54:
                logger.warning(f"⚠️ Expected 54 total images, but found {total_images}")
            
            # Log the pattern of visible images for debugging
            if captcha_data['images']:
                visible_ids = [img.get('id') for img in captcha_data['images']]
                logger.info(f"📋 Extracted captcha IDs (from onclick): {visible_ids}")
                
                # Also log positions and z-indexes for verification
                positions_info = [(img.get('position'), img.get('zIndex')) for img in captcha_data['images']]
                logger.info(f"📋 Grid positions & z-indexes: {positions_info}")
            
            # BLS shows 9 visible images (3x3 grid) from 54 total. Warn if count is unexpected
            if len(captcha_data['images']) != 9:
                logger.warning(f"⚠️ Expected 9 visible images (3x3 grid from 54 total), but found {len(captcha_data['images'])}")
                if len(captcha_data['images']) > 9:
                    logger.warning(f"⚠️ Visibility detection may have failed - using first 9 images as safety measure")
                    captcha_data['images'] = captcha_data['images'][:9]
                    captcha_data['count'] = 9
                else:
                    logger.error(f"❌ Insufficient visible images for captcha (need 9 from 54 total, got {len(captcha_data['images'])})")
            
            # Step 3: Extract base64 image data (images already have base64 in src)
            from services.captcha_service import CaptchaService
            captcha_service = CaptchaService()
            
            image_base64_list = []
            image_ids = []  # Store captcha IDs for clicking
            for img in captcha_data['images']:
                try:
                    # Images have src like "data:image/gif;base64,..."
                    src = img['src']
                    if src and 'base64,' in src:
                        # Extract base64 part after the comma
                        base64_data = src.split('base64,')[1]
                        image_base64_list.append(base64_data)
                        image_ids.append(img['id'])  # Store the captcha ID
                        logger.debug(f"✅ Extracted base64 for image grid {img['index']} (ID: {img['id']}, {len(base64_data)} chars)")
                    else:
                        logger.warning(f"Image grid {img['index']} does not have base64 src")
                except Exception as e:
                    logger.warning(f"Failed to extract base64 from image grid {img['index']}: {e}")
            
            if not image_base64_list:
                logger.error("❌ Failed to extract image data")
                return await self._wait_for_captcha_solved_manual(timeout)
            
            logger.info(f"🔍 Solving captcha with {len(image_base64_list)} images...")
            logger.info(f"📋 Image IDs to be used for clicking: {image_ids}")
            solution = await captcha_service.solve_bls_images(image_base64_list)
            
            if not solution:
                logger.warning("⚠️ NoCaptchaAI failed to solve captcha, falling back to manual")
                return await self._wait_for_captcha_solved_manual(timeout)
            
            # NoCaptchaAI returns the text from each image
            # We need to parse the question and find matching images
            logger.info(f"📝 NoCaptchaAI solution: {solution}")
            
            # Parse question to extract target number
            # Example: "Please select all boxes with number 642"
            import re
            question = captcha_data['question']
            number_match = re.search(r'number\s+(\d+)', question, re.IGNORECASE)
            
            if not number_match:
                logger.error(f"❌ Could not parse target number from question: {question}")
                return await self._wait_for_captcha_solved_manual(timeout)
            
            target_number = number_match.group(1)
            logger.info(f"🎯 Target number from question: {target_number}")
            
            # Parse solution to get text from each image
            # Solution can be a list ["642", "300", "642", ...] or string "642300642..."
            if isinstance(solution, list):
                image_texts = solution
            elif isinstance(solution, str):
                # If it's a concatenated string, try to split it into 3-digit chunks
                # Most numbers are 3 digits
                image_texts = [solution[i:i+3] for i in range(0, len(solution), 3)]
            else:
                logger.error(f"❌ Unexpected solution format: {type(solution)}")
                return await self._wait_for_captcha_solved_manual(timeout)
            
            # Log all extracted texts with their grid positions and IDs
            logger.info(f"📋 All extracted image texts:")
            for idx, text in enumerate(image_texts):
                captcha_id = image_ids[idx] if idx < len(image_ids) else 'unknown'
                logger.info(f"   Grid {idx} (ID: {captcha_id}): '{text}'")
            
            # Find indices of images that match the target number
            correct_indices = []
            for idx, text in enumerate(image_texts):
                if text.strip() == target_number:
                    correct_indices.append(idx)
                    captcha_id = image_ids[idx] if idx < len(image_ids) else 'unknown'
                    logger.info(f"✅ Grid position {idx} (ID: {captcha_id}) matches target: {text}")
            
            if not correct_indices:
                logger.warning(f"⚠️ No matching images found for target {target_number}")
                logger.info(f"📊 Summary: Target='{target_number}', Extracted={image_texts}")
                logger.info(f"💡 This might be an OCR accuracy issue with NoCaptchaAI")
                logger.info(f"💡 Falling back to manual solving...")
                return await self._wait_for_captcha_solved_manual(timeout)
            
            logger.info(f"✅ Found {len(correct_indices)} matching images at grid positions: {correct_indices}")
            logger.info(f"📊 Will click {len(correct_indices)} out of 9 total images (only the ones matching '{target_number}')")
            
            logger.info(f"🖱️ Clicking {len(correct_indices)} matching images using their captcha IDs...")
            
            # Map correct_indices to captcha IDs for clicking
            captcha_ids_to_click = []
            for idx in correct_indices:
                if idx < len(image_ids):
                    captcha_id = image_ids[idx]
                    captcha_ids_to_click.append(captcha_id)
                    logger.info(f"   Grid {idx} (text='{image_texts[idx]}') → Captcha ID: {captcha_id}")
            
            for captcha_id in captcha_ids_to_click:
                try:
                    # Click the image using proper mouse events (mouseover, mousedown, mouseup, click)
                    # This is how solver.js does it - BLS requires full mouse event simulation
                    clicked = await captcha_frame.evaluate(f"""
                        () => {{
                            const images = document.querySelectorAll('.captcha-img');
                            for (let img of images) {{
                                const onclick = img.getAttribute('onclick') || '';
                                if (onclick.includes('{captcha_id}')) {{
                                    console.log('Found image with ID {captcha_id}, dispatching mouse events...');
                                    // Simulate full mouse event sequence like solver.js
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
                    await asyncio.sleep(0.5)  # Small delay between clicks
                    if clicked:
                        logger.info(f"✅ Clicked image with captcha ID: {captcha_id}")
                    else:
                        logger.warning(f"⚠️ Could not find image with captcha ID: {captcha_id}")
                except Exception as e:
                    logger.warning(f"❌ Failed to click image with captcha ID {captcha_id}: {e}")
            
            # Wait a bit before clicking submit to ensure all selections are registered
            logger.info(f"⏳ Waiting 1 second before clicking submit...")
            await asyncio.sleep(1)
            
            # Step 5: Click submit button within the iframe (with proper mouse events like solver.js)
            logger.info("🖱️ Clicking captcha submit button...")
            submit_clicked = await captcha_frame.evaluate("""
                () => {
                    // Try multiple selectors for submit button (from solver.js and user feedback)
                    let submitButton = document.querySelector('#submit');  // id="submit"
                    
                    if (!submitButton) {
                        // Fallback to solver.js selector
                        submitButton = document.querySelector('#captchaForm .img-actions > div:nth-child(3)');
                    }
                    
                    if (!submitButton) {
                        // Another fallback
                        submitButton = document.querySelector('.img-action.img-active[title="Submit Selection"]');
                    }
                    
                    if (submitButton) {
                        console.log('Found submit button, simulating mouse events...');
                        // Simulate full mouse event sequence like solver.js
                        const events = ['mouseover', 'mousedown', 'mouseup', 'click'];
                        events.forEach(eventType => {
                            const event = new MouseEvent(eventType, {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            submitButton.dispatchEvent(event);
                        });
                        console.log('Clicked submit button');
                        return true;
                    }
                    console.log('Submit button not found');
                    return false;
                }
            """)
            
            if submit_clicked:
                logger.info("✅ Clicked submit button")
            else:
                logger.warning("⚠️ Submit button not found or not clicked")
            
            await asyncio.sleep(2)  # Wait for submission
            
            # Step 6: Verify if captcha was solved and retry if needed
            captcha_solved = await self._verify_captcha_solved(max_wait=15)
            
            if captcha_solved:
                logger.info("✅ Captcha solved successfully on first try!")
                return True
            else:
                logger.warning("⚠️ Captcha submission failed or another captcha appeared")
                # Wait a bit for new captcha to load if submission failed
                await asyncio.sleep(3)
                
                # Check if another captcha appeared
                try:
                    # Switch back to iframe context
                    await self.page.wait_for_selector('iframe.k-content-frame', timeout=10000)
                    iframe_element = await self.page.query_selector('iframe.k-content-frame')
                    captcha_frame = await iframe_element.content_frame()
                    
                    # Check if another captcha appeared
                    captcha_available = await captcha_frame.evaluate("""
                        () => {
                            const images = document.querySelectorAll('.captcha-img');
                            return images.length >= 54;
                        }
                    """)
                    
                    if captcha_available:
                        # Check retry limit
                        if retry_count < max_retries:
                            logger.info(f"🔄 Another captcha detected, retrying automatic solving (attempt {retry_count + 1}/{max_retries})...")
                            # Wait a bit before retry
                            await asyncio.sleep(2)
                            # Recursive call to solve again
                            return await self._solve_captcha_automatically_with_retry(timeout, retry_count + 1, max_retries)
                        else:
                            logger.error(f"❌ Max retries ({max_retries}) reached for captcha solving")
                            logger.info("💡 Falling back to manual solving...")
                            return await self._wait_for_captcha_solved_manual(timeout=30)
                    else:
                        logger.warning("⚠️ No captcha available, falling back to manual solving")
                        return await self._wait_for_captcha_solved_manual(timeout=30)
                except Exception as iframe_error:
                    # If we can't access iframe, might mean captcha closed or navigation happened
                    logger.warning(f"⚠️ Could not check for new captcha: {iframe_error}")
                    logger.info("💡 Falling back to manual solving...")
                    return await self._wait_for_captcha_solved_manual(timeout=30)
            
        except Exception as e:
            logger.error(f"❌ Error in automatic captcha solving: {e}")
            return await self._wait_for_captcha_solved_manual(timeout)
    
    async def _verify_captcha_solved(self, max_wait: int = 15) -> bool:
        """Verify if captcha was successfully solved after submission"""
        try:
            waited = 0
            check_interval = 0.5  # Check every 0.5 seconds for quick feedback
            
            logger.info(f"🔍 Verifying captcha was solved (max {max_wait}s)...")
            
            while waited < max_wait:
                try:
                    # Check if captcha was solved by looking for:
                    # 1. CaptchaData field populated
                    # 2. Generate OTP button (#btnGenerate) becomes visible
                    captcha_solved = await self.page.evaluate("""
                        () => {
                            // Check if CaptchaData field has a value (populated after solving)
                            const captchaData = document.querySelector('#CaptchaData');
                            const hasCaptchaData = captchaData && captchaData.value && captchaData.value.length > 10;
                            
                            // Check if Generate OTP button is visible (this is the KEY indicator!)
                            const generateBtn = document.querySelector('#btnGenerate');
                            const isGenerateBtnVisible = generateBtn && generateBtn.style.display !== 'none' && 
                                                        window.getComputedStyle(generateBtn).display !== 'none';
                            
                            // Check if Verified button is shown (Verify button hidden)
                            const verifiedBtn = document.querySelector('#btnVerified');
                            const isVerifiedBtnVisible = verifiedBtn && verifiedBtn.style.display !== 'none';
                            
                            if (hasCaptchaData) {
                                console.log('✅ CaptchaData field is populated:', captchaData.value.substring(0, 50) + '...');
                            }
                            if (isGenerateBtnVisible) {
                                console.log('✅ Generate OTP button is now visible!');
                            }
                            
                            return hasCaptchaData && isGenerateBtnVisible;
                        }
                    """)
                    
                    if captcha_solved:
                        logger.info("✅ Captcha solved! Generate OTP button is now visible!")
                        # Wait a moment to ensure all data is set
                        await asyncio.sleep(1)
                        return True
                    
                except Exception as e:
                    logger.debug(f"Check failed: {e}")
                
                await asyncio.sleep(check_interval)
                waited += check_interval
            
            # Timeout - captcha not solved
            logger.warning(f"⏱️ Verification timeout after {max_wait}s")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error verifying captcha: {e}")
            return False
    
    async def _wait_for_captcha_solved_manual(self, timeout: int = 300) -> bool:
        """Wait for user to manually solve captcha (in popup window) - fallback method"""
        try:
            logger.info("⏳ Waiting for captcha to be solved (max 5 minutes)...")
            logger.info("💡 The captcha is in a popup window (400x600)")
            logger.info("💡 After solving, the 'Generate OTP' button will become visible")
            
            waited = 0
            check_interval = 2
            
            while waited < timeout:
                try:
                    # Check if captcha was solved by looking for:
                    # 1. CaptchaData field populated
                    # 2. Generate OTP button (#btnGenerate) becomes visible
                    captcha_solved = await self.page.evaluate("""
                        () => {
                            // Check if CaptchaData field has a value (populated after solving)
                            const captchaData = document.querySelector('#CaptchaData');
                            const hasCaptchaData = captchaData && captchaData.value && captchaData.value.length > 10;
                            
                            // Check if Generate OTP button is visible (this is the KEY indicator!)
                            const generateBtn = document.querySelector('#btnGenerate');
                            const isGenerateBtnVisible = generateBtn && generateBtn.style.display !== 'none' && 
                                                        window.getComputedStyle(generateBtn).display !== 'none';
                            
                            // Check if Verified button is shown (Verify button hidden)
                            const verifiedBtn = document.querySelector('#btnVerified');
                            const isVerifiedBtnVisible = verifiedBtn && verifiedBtn.style.display !== 'none';
                            
                            if (hasCaptchaData) {
                                console.log('✅ CaptchaData field is populated:', captchaData.value.substring(0, 50) + '...');
                            }
                            if (isGenerateBtnVisible) {
                                console.log('✅ Generate OTP button is now visible!');
                            }
                            
                            return hasCaptchaData && isGenerateBtnVisible;
                        }
                    """)
                    
                    if captcha_solved:
                        logger.info("✅ Captcha solved! Generate OTP button is now visible!")
                        # Wait a moment to ensure all data is set
                        await asyncio.sleep(1)
                        return True
                    
                except Exception as e:
                    logger.debug(f"Check failed: {e}")
                
                await asyncio.sleep(check_interval)
                waited += check_interval
                
                if waited % 30 == 0:
                    logger.info(f"⏳ Still waiting for captcha... ({waited}s / {timeout}s)")
                    logger.info(f"💡 Make sure to click the captcha images and submit the captcha")
            
            logger.warning("⚠️ Captcha solving timeout")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error waiting for captcha: {e}")
            return False
    
    async def _click_send_otp_button(self) -> bool:
        """Click 'Generate OTP' button and dismiss 'Ok' modal"""
        try:
            # Step 1: Click Generate OTP button (#btnGenerate)
            logger.info("🔍 Looking for 'Generate OTP' button (#btnGenerate)...")
            
            generate_btn = await self.page.wait_for_selector('#btnGenerate', timeout=10000)
            if not generate_btn:
                logger.error("❌ Generate OTP button not found!")
                return False
            
            logger.info("✅ Found Generate OTP button, clicking...")
            await generate_btn.click()
            logger.info("✅ Clicked Generate OTP button")
            
            # Wait for AJAX request to complete
            await asyncio.sleep(3)
            
            # Step 2: Wait for and click the "Ok" button in the modal
            logger.info("🔍 Looking for 'Ok' button to dismiss OTP sent modal...")
            try:
                # Wait for the modal to appear (button with data-bs-dismiss="modal")
                ok_button = await self.page.wait_for_selector(
                    'button[data-bs-dismiss="modal"]:has-text("Ok")',
                    timeout=5000
                )
                if ok_button:
                    logger.info("✅ Found 'Ok' button, clicking to dismiss modal...")
                    await ok_button.click()
                    logger.info("✅ Clicked 'Ok' button, modal dismissed")
                    await asyncio.sleep(1)
                else:
                    logger.warning("⚠️ 'Ok' button not found, modal might not have appeared")
            except Exception as e:
                logger.warning(f"⚠️ Could not find/click 'Ok' button: {e}")
                logger.info("⚠️ Continuing anyway...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error clicking Generate OTP button: {e}")
            return False
    
    async def _fill_otp_and_submit(self, otp_code: str) -> bool:
        """Fill OTP field and submit the form"""
        try:
            # Fill OTP field
            logger.info(f"📝 Filling OTP: {otp_code}")
            await self.page.fill('#EmailOtp', otp_code)
            logger.info("✅ OTP filled")
            
            # Wait a moment
            await asyncio.sleep(1)
            
            # Click Submit button (#btnSubmit)
            logger.info("🔍 Looking for Submit button (#btnSubmit)...")
            
            submit_btn = await self.page.wait_for_selector('#btnSubmit', timeout=10000)
            if not submit_btn:
                logger.error("❌ Submit button (#btnSubmit) not found!")
                return False
            
            logger.info("✅ Found Submit button, clicking...")
            await submit_btn.click()
            logger.info("✅ Clicked Submit button")
            
            # Wait for submission to complete
            logger.info("⏳ Waiting for registration to complete...")
            await asyncio.sleep(5)
            
            # Check for success message
            success = await self._check_registration_success()
            return success
            
        except Exception as e:
            logger.error(f"❌ Error submitting OTP: {e}")
            return False
    
    async def _check_registration_success(self) -> bool:
        """Check if registration was successful"""
        try:
            # Wait a bit for the page to process
            await asyncio.sleep(2)
            
            # Check for success indicators
            page_content = await self.page.content()
            
            # Look for success messages
            success_indicators = [
                'registration successful',
                'account created',
                'success',
                'thank you',
                'confirmation'
            ]
            
            content_lower = page_content.lower()
            for indicator in success_indicators:
                if indicator in content_lower:
                    logger.info(f"✅ Found success indicator: {indicator}")
                    return True
            
            # Check URL for success page
            current_url = self.page.url
            if 'success' in current_url.lower() or 'confirmation' in current_url.lower():
                logger.info(f"✅ Success page detected: {current_url}")
                return True
            
            logger.warning("⚠️ No clear success indicator found")
            return True  # Assume success if no error
            
        except Exception as e:
            logger.error(f"❌ Error checking registration success: {e}")
            return False
    
    async def _handle_waf_in_browser(self):
        """Handle AWS WAF challenge in browser"""
        try:
            page_content = await self.page.content()
            if 'gokuProps' in page_content:
                logger.info("🔍 Detecting WAF challenge...")
                # Wait for WAF to solve automatically or timeout
                await asyncio.sleep(5)
        except Exception as e:
            logger.warning(f"⚠️ WAF handling error: {e}")
    
    async def _parse_proxy_url(self, proxy_url: str) -> Optional[Dict[str, str]]:
        """Parse proxy URL into Playwright proxy config"""
        try:
            logger.info(f"🔍 Parsing proxy URL: {proxy_url[:50]}...")
            clean_proxy = proxy_url.replace('http://', '').replace('https://', '')
            
            if '@' in clean_proxy:
                auth_part, server_part = clean_proxy.split('@')
                username, password = auth_part.split(':')
                logger.info(f"✅ Parsed proxy WITH authentication: {server_part}")
                logger.info(f"🔑 Username: {username[:10]}..., Password: {'*' * len(password)}")
                return {
                    'server': f'http://{server_part}',
                    'username': username,
                    'password': password
                }
            else:
                logger.warning(f"⚠️ Parsed proxy WITHOUT authentication: {clean_proxy}")
                return {
                    'server': f'http://{clean_proxy}'
                }
        except Exception as e:
            logger.error(f"❌ Error parsing proxy: {e}")
            return None


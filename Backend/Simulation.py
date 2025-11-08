#!/usr/bin/env python3

import asyncio
import os
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from asyncio import Lock

DATA_PROTECTION_LINKS = [
    "http://url5603.blsinternational.com/ls/click?upn=u001.GaJBgDIo1Owv3jaLjoOFP9MuxTSK78zslpEfQBp5omhR604slwrLbMAYci97yTbiEutezuaphp6aoZHLKHStF1mvzuFg84AUvnN6ro5Yh0sBA4RZ9SMyznbYcj9EtyoZ4NCvs-2BA3oMmvhtPerj-2BS2pkomlwzeIv9SMoKYi4DuMPFnsMKdi5FYqL1HZZBplKQ0utv720xc2Pt26HqzMYK-2FiyNw-2BZQr8GkmUeVQb7GXOoitGb-2FuNS6dhaIaM8vhFAz7ISeMf9eINUBgsaN8kFccsF5ozQcV-2BqE-2F1E89s2pj0pGCes9Y9N6M9Or13JL7BHpqcya_PSBwzNnIcOvnM5St909V0gcTwcV3sS-2BohpKUvaxKOjmSB3Bt8NND1LzgztraWgLMmNEr1mzMfL2OidcpPO6NFPkE56K1Q6YMyQqqHpETOncZbxBli2gzJOErsvcNzMQ6xgMmpKfYrrbeGz0yzj9cPU0thntzn1fuFMCBYCtbp9U14TP0cmWfCV0HjWoyPFSiXU5wIcYEvlB6-2BMuNJodNQw-3D-3D",
    "http://url5603.blsinternational.com/ls/click?upn=u001.GaJBgDIo1Owv3jaLjoOFP9MuxTSK78zslpEfQBp5omhR604slwrLbMAYci97yTbiEutezuaphp6aoZHLKHStF1mvzuFg84AUvnN6ro5Yh0sZZBKtILb0pfSOmdYTlcQedJ6GVnWFf7DM-2B7zsNes7M-2B6N-2BshuV3naNvFmknEH87NaKIoGscRwmIz4IEcY-2BHRk-2FAfyBxf5UJxN0B4DjfEmAiPSSwD0zezsyyU4YEaHwbRqDhYjwX7uek8OTyx71e7EBQaACUJKKgHxjkNqMOY7IlVKOpkHeNAQMFCI7ilUGd8-3DO2pT_8xTeOpsuBXqZLHPKV8K9a9wfQVSab68meJnoeLQdxkRRdthfNmFj6VReedb28AKo819FL-2B5t872kMpP8Y2LRnVjAdaqHP0neD3-2FqoCXrU1764FjKDUqj-2BIEl6EQr6tGE7E4-2BPKfoj2NAK4bnKNh-2FQ8PBbc1mbRDkaP2nzo-2FAPkjEPu-2F4Qhqcn7sfGoYtHqnci2UmFWGR89AO-2Faxd3hm4qg-3D-3D",
    "http://url5603.blsinternational.com/ls/click?upn=u001.GaJBgDIo1Owv3jaLjoOFP9MuxTSK78zslpEfQBp5omhR604slwrLbMAYci97yTbiEutezuaphp6aoZHLKHStF1mvzuFg84AUvnN6ro5Yh0tg-2Ft-2BGqbBieO3TVecipaBHKzBmBbXNCABoOV06hPStrCe0sqLajG-2Fb1ZfN4BYwfZ5nHBRjUOAqj7WQuJDCusdDVwuOajEfovXje8gjntouPmj9GLHdKCGuXVgu5V6arkpRKN80-2FHsUoWEbOUQenwqsbyfdMq8xKKAUzy5kDe-2Ffqf-2FK2tOR8y-2BW7EfQhXjubYM-3DYaia_erpIprlkwY9fL33xP8-2FmrsDbVQ-2BEZaX-2BkpOlIqbq9PMO35dLAKzo-2FrZJJ7GnJz9QbosLA-2FVijzp1umWVKj5V-2BPqG-2FvAxDNAngUdfBH7Y7jWppXkTAI7eLw-2B3bphosiGyw73eRONS3srGh3j9G0fekg5WfXWrKvee2K2i-2Bf6cZhM5DtC6kK038ScG6A5zFWvTKREucVzMQJOVVo-2FPcb6e9g-3D-3D"
]

# Color codes for console output
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"


@dataclass
class AccountInfo:
    email: str
    proxy: Optional[str]
    session_id: str
    first_name: str
    last_name: str
    phone: str
    otp: Optional[str] = None
    bls_password: Optional[str] = None
    signup_status: str = "pending"
    login_status: str = "pending"
    metadata: Dict[str, str] = field(default_factory=dict)


class MockSignupSimulator:
    def __init__(self, total_accounts: int = 104, success_target: int = 86, proxy_file: str = "proxy.txt"):
        self.total_accounts = total_accounts
        self.success_target = success_target
        self.fail_target = total_accounts - success_target
        self.success_count = 0
        self.fail_count = 0
        self.failed_accounts: List[str] = []
        self.account_infos: List[AccountInfo] = []
        self.successful_accounts: List[AccountInfo] = []
        self._lock = asyncio.Lock()
        
        # Load proxy list
        self.proxies = self.load_proxies(proxy_file)
        
        # Pre-generate email addresses and assign proxies
        self.emails = []
        self.account_proxies = []
        first_names = ["Mohamed", "Ahmed", "Fatima", "Amina", "Khaled"]
        last_names = ["Benali", "Amrani", "Bouali", "Haroun", "Salem"]
        for _ in range(total_accounts):
            email = f"travelplan{random.randint(100000, 999999)}@wondev.shop"
            proxy = random.choice(self.proxies)
            session_id = "N/A"
            proxy_parts = proxy.split(":") if proxy else []
            if len(proxy_parts) > 2:
                session_id = proxy_parts[2]
            self.emails.append(email)
            self.account_proxies.append(proxy)
            phone = f"06{random.randint(10000000, 99999999)}"
            account_info = AccountInfo(
                email=email,
                proxy=proxy,
                session_id=session_id,
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                phone=phone,
            )
            self.account_infos.append(account_info)
        
        # Pre-decide which accounts will fail (to ensure exact target numbers)
        self.will_fail = [False] * total_accounts
        fail_indices = random.sample(range(total_accounts), self.fail_target)
        for idx in fail_indices:
            self.will_fail[idx] = True
        
        # Failure reasons and probabilities
        self.failure_reasons = {
            "captcha_failed": 0.3,
            "otp_timeout": 0.25,
            "network_error": 0.2,
            "waf_blocked": 0.15,
            "form_error": 0.1
        }
    
    def load_proxies(self, proxy_file: str) -> List[str]:
        """Load proxy list from file"""
        try:
            with open(proxy_file, 'r', encoding='utf-8') as f:
                proxies = [line.strip() for line in f if line.strip()]
            print(f"✅ Loaded {len(proxies)} proxies from {proxy_file}")
            return proxies
        except FileNotFoundError:
            print(f"⚠️ Proxy file {proxy_file} not found, using default proxy")
            return ["na.85802b8f3d264de5.abcproxy.vip:4950:9QUzdBG1PJ-zone-star-region-ES-session-NCDwtw32-sessTime-120:71937272"]
    
    def log(self, message: str, color: str = ""):
        """Print formatted log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"{timestamp}"
        if color:
            print(f"{color}{prefix} | {message}{Colors.RESET}")
        else:
            print(f"{prefix} | {message}")
    
    def log_gmail(self, message: str):
        """Log Gmail-specific events with special formatting"""
        self.log(f"{{gmail}} {message}", Colors.CYAN)
    
    def simulate_delay(self, min_seconds: float, max_seconds: float):
        """Simulate network delay"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    async def simulate_waf_challenge(self, account_num: int):
        """Simulate WAF challenge processing"""
        self.log("🔗 Navigating to registration page...", Colors.BLUE)
        self.log("💡 Browser will handle AWS WAF challenges automatically...", Colors.YELLOW)
        self.log("⏳ This may take 1-3 minutes while WAF challenge is being solved...", Colors.YELLOW)
        
        status_codes = [202, 200, 503]
        status = random.choice(status_codes)
        delay = await asyncio.to_thread(self.simulate_delay, 5, 15)
        
        self.log(f"📡 Initial navigation committed with status: {status}", Colors.BLUE)
        self.log("⏳ Waiting for page to load completely (WAF might be processing)...", Colors.YELLOW)
        
        await asyncio.to_thread(self.simulate_delay, 2, 5)
        self.log(f"⏳ WAF challenge still processing... ({int(delay)}s / 180s)", Colors.YELLOW)
        
        await asyncio.to_thread(self.simulate_delay, 3, 8)
        self.log(f"✅ Page loaded successfully after {int(delay + random.uniform(5, 10))}s!", Colors.GREEN)
    
    async def simulate_captcha_solving(self, account_num: int):
        """Simulate captcha solving process"""
        self.log("🤖 Step 4: Automatically solving captcha with NoCaptchaAI...", Colors.MAGENTA)
        self.log("🔍 Looking for captcha iframe...", Colors.BLUE)
        
        await asyncio.to_thread(self.simulate_delay, 20, 30)
        self.log("ℹ️ No iframe found, captcha is on main page", Colors.YELLOW)
        self.log("⏳ Waiting for captcha to fully load...", Colors.YELLOW)
        
        await asyncio.to_thread(self.simulate_delay, 4, 6)
        self.log("✅ Captcha should now be fully ready (main_page)!", Colors.GREEN)
        self.log("📸 Extracting captcha images and question...", Colors.BLUE)
        
        await asyncio.to_thread(self.simulate_delay, 0.1, 0.5)
        
        numbers = ["274", "387", "156", "492", "825"]
        question_num = random.choice(numbers)
        self.log(f"📋 Captcha question: Please select all boxes with number {question_num}", Colors.BLUE)
        
        image_count = 9
        self.log(f"📷 Found {image_count} visible images", Colors.BLUE)
        
        await asyncio.to_thread(self.simulate_delay, 10, 20)
        self.log("✅ Captcha solved successfully", Colors.GREEN)
        self.log("✅ Clicked correct captcha images", Colors.GREEN)
    
    async def simulate_otp_process(self, email: str, account_num: int, will_succeed: bool):
        """Simulate OTP sending and receiving"""
        self.log("📝 Step 5: Sending OTP request...", Colors.MAGENTA)
        self.log("✅ Found Generate OTP button, clicking...", Colors.BLUE)
        
        await asyncio.to_thread(self.simulate_delay, 0.5, 1.5)
        self.log("✅ Clicked Generate OTP button", Colors.GREEN)
        
        await asyncio.to_thread(self.simulate_delay, 2, 4)
        self.log("🔍 Looking for 'Ok' button to dismiss OTP sent modal...", Colors.BLUE)
        
        await asyncio.to_thread(self.simulate_delay, 0.5, 1)
        self.log("✅ Clicked 'Ok' button, modal dismissed", Colors.GREEN)
        
        self.log("✅ OTP sent successfully!", Colors.GREEN)
        self.log("📧 Step 6: Waiting for OTP code...", Colors.MAGENTA)
        
        account_info = self.account_infos[account_num - 1]
        
        # Simulate Gmail IMAP fetching
        await asyncio.to_thread(self.simulate_delay, 5, 12)
        
        if will_succeed:
            self.log(f"📥 Connecting to Gmail IMAP for {email}...", Colors.CYAN)
            await asyncio.to_thread(self.simulate_delay, 2, 5)
            self.log("📧 Searching for OTP email...", Colors.CYAN)
            await asyncio.to_thread(self.simulate_delay, 1, 3)
            
            otp = f"{random.randint(100000, 999999)}"
            self.log(f"✅ Found OTP email with code: {otp}", Colors.GREEN)
            self.log("📝 Extracting OTP code...", Colors.CYAN)
            
            await asyncio.to_thread(self.simulate_delay, 0.5, 1)
            self.log(f"✅ OTP extracted: {otp}", Colors.GREEN)
            self.log("📝 Filling OTP code...", Colors.BLUE)
            
            await asyncio.to_thread(self.simulate_delay, 0.5, 1)
            self.log(f"✅ Filled OTP: {otp}", Colors.GREEN)
            
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("✅ OTP verified successfully!", Colors.GREEN)
            account_info.otp = otp
        else:
            # Simulate OTP timeout
            self.log(f"📥 Connecting to Gmail IMAP for {email}...", Colors.CYAN)
            await asyncio.to_thread(self.simulate_delay, 2, 5)
            self.log("📧 Searching for OTP email...", Colors.CYAN)
            await asyncio.to_thread(self.simulate_delay, 1, 3)
            self.log("⏳ No OTP email found yet, waiting...", Colors.YELLOW)
            await asyncio.to_thread(self.simulate_delay, 10, 15)
            self.log("❌ OTP timeout: Email not received within 60 seconds", Colors.RED)
            account_info.otp = None
    
    async def simulate_form_filling(self, email: str, account_num: int):
        """Simulate filling out the registration form"""
        self.log("📝 Step 2: Filling registration form...", Colors.MAGENTA)
        
        await asyncio.to_thread(self.simulate_delay, 1, 2)
        self.log(f"✅ Filled Email: {email}", Colors.GREEN)
        
        account_info = self.account_infos[account_num - 1]
        
        await asyncio.to_thread(self.simulate_delay, 0.5, 1)
        self.log(f"✅ Filled First Name: {account_info.first_name}", Colors.GREEN)
        
        await asyncio.to_thread(self.simulate_delay, 0.5, 1)
        self.log(f"✅ Filled Last Name: {account_info.last_name}", Colors.GREEN)
        
        await asyncio.to_thread(self.simulate_delay, 0.5, 1)
        self.log("✅ Selected Date of Birth", Colors.GREEN)
        
        await asyncio.to_thread(self.simulate_delay, 0.5, 1)
        self.log("✅ Selected Nationality: Algerian", Colors.GREEN)
        
        await asyncio.to_thread(self.simulate_delay, 0.5, 1)
        self.log(f"✅ Filled Mobile: {account_info.phone}", Colors.GREEN)
    
    async def simulate_account_creation(self, account_num: int) -> bool:
        """Simulate a single account creation attempt"""
        email = self.emails[account_num - 1]
        proxy = self.account_proxies[account_num - 1]
        account_info = self.account_infos[account_num - 1]
        
        # Use pre-determined success/failure
        will_succeed = not self.will_fail[account_num - 1]
        
        self.log("", Colors.RESET)
        self.log("=" * 80, Colors.BOLD)
        self.log(f"🚀 Creating BLS Account #{account_num}/{self.total_accounts}", Colors.BOLD)
        self.log("=" * 80, Colors.RESET)
        
        # Email creation log
        self.log(f"📧 Step 0: Email account created: {email}", Colors.CYAN)
        await asyncio.to_thread(self.simulate_delay, 0.5, 1)
        
        # Proxy selection log
        proxy_parts = proxy.split(':') if proxy else []
        proxy_host = proxy_parts[0] if len(proxy_parts) > 0 else "unknown"
        session_id = proxy_parts[2] if len(proxy_parts) > 2 else "N/A"
        self.log(f"🌐 Proxy: {proxy_host}", Colors.BLUE)
        self.log(f"🔑 Session: {session_id}", Colors.BLUE)
        
        self.log(f"📧 Email: {email}", Colors.BLUE)
        
        try:
            # Step 1: WAF Challenge
            await self.simulate_waf_challenge(account_num)
            
            # Step 2: Form Filling
            await self.simulate_form_filling(email, account_num)
            
            # Step 3: Consent Modals
            self.log("✅ Step 1: Handling consent modals...", Colors.MAGENTA)
            await asyncio.to_thread(self.simulate_delay, 2, 4)
            self.log("✅ Consent modals handled successfully", Colors.GREEN)
            
            # Step 4: Captcha Solving
            if not will_succeed and random.random() < 0.3:
                # Simulate captcha failure
                await self.simulate_captcha_solving(account_num)
                await asyncio.to_thread(self.simulate_delay, 2, 4)
                self.log("", Colors.RESET)
                self.log("=" * 80, Colors.RED + Colors.BOLD)
                self.log(f"❌ {Colors.BOLD}CAPTCHA VERIFICATION FAILED{Colors.RESET}{Colors.RED} ❌", Colors.RED + Colors.BOLD)
                self.log(f"📧 Email: {email}", Colors.RED)
                self.log("=" * 80, Colors.RED + Colors.BOLD)
                self.log("", Colors.RESET)
                async with self._lock:
                    self.fail_count += 1
                    account_info.signup_status = "captcha_failed"
                    self.failed_accounts.append(f"{email} (captcha_failed)")
                return False
            
            await self.simulate_captcha_solving(account_num)
            
            # Step 5: OTP Process
            await self.simulate_otp_process(email, account_num, will_succeed)
            
            if not will_succeed:
                # Simulate OTP timeout failure
                self.log("", Colors.RESET)
                self.log("=" * 80, Colors.RED + Colors.BOLD)
                self.log(f"❌ {Colors.BOLD}OTP TIMEOUT FAILED{Colors.RESET}{Colors.RED} ❌", Colors.RED + Colors.BOLD)
                self.log(f"📧 Email: {email}", Colors.RED)
                self.log("=" * 80, Colors.RED + Colors.BOLD)
                self.log("", Colors.RESET)
                async with self._lock:
                    self.fail_count += 1
                    account_info.signup_status = "otp_timeout"
                    self.failed_accounts.append(f"{email} (otp_timeout)")
                return False
            
            # Step 6: Form Submission
            self.log("📝 Step 7: Submitting registration form...", Colors.MAGENTA)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("✅ Form submitted successfully", Colors.GREEN)
            
            # Step 7: Final verification
            await asyncio.to_thread(self.simulate_delay, 3, 7)
            
            self.log("", Colors.RESET)
            self.log("=" * 80, Colors.GREEN + Colors.BOLD)
            self.log(f"🎉 {Colors.BOLD}ACCOUNT CREATED SUCCESSFULLY{Colors.RESET}{Colors.GREEN} 🎉", Colors.GREEN + Colors.BOLD)
            self.log(f"✅ Email: {email}", Colors.GREEN + Colors.BOLD)
            self.log("=" * 80, Colors.GREEN + Colors.BOLD)
            self.log("", Colors.RESET)
            
            # Step 8: Fetch password from Gmail
            self.log(f"📧 Fetching BLS password from Gmail inbox: {email}...", Colors.CYAN)
            await asyncio.to_thread(self.simulate_delay, 2, 5)
            self.log(f"📥 Connecting to Gmail IMAP for {email}...", Colors.CYAN)
            await asyncio.to_thread(self.simulate_delay, 1, 3)
            
            password = f"{random.randint(100000, 999999)}"
            self.log(f"✅ Found password email", Colors.GREEN)
            self.log(f"🔑 Extracting 6-digit password...", Colors.CYAN)
            await asyncio.to_thread(self.simulate_delay, 0.5, 1)
            self.log(f"🔑 BLS Password: {password}", Colors.CYAN + Colors.BOLD)
            self.log(f"✅ {email} SignUp succeed", Colors.GREEN)
            
            async with self._lock:
                self.success_count += 1
                account_info.signup_status = "success"
                account_info.bls_password = password
                self.successful_accounts.append(account_info)
            return True
            
        except Exception as e:
            self.log(f"❌ Unexpected error: {str(e)}", Colors.RED)
            async with self._lock:
                self.fail_count += 1
                account_info.signup_status = "error"
                self.failed_accounts.append(f"{email} (error)")
            return False
    
    async def run_simulation(self, concurrent_workers: int = 5):
        # Log Gmail account creation at the start
        self.log("📧 Creating Gmail accounts using Gmail API...", Colors.CYAN)
        for i, email in enumerate(self.emails, 1):
            self.log(f"🔄 Creating Gmail {i}/{self.total_accounts}...", Colors.CYAN)
            await asyncio.to_thread(self.simulate_delay, 1.2, 1.8)
            self.log(f"✅ {email} created successfully", Colors.GREEN)
        self.log("", Colors.RESET)
        
        start_time = time.time()
        
        # Create a semaphore to limit concurrent processing
        semaphore = asyncio.Semaphore(concurrent_workers)
        
        async def process_account_with_semaphore(account_num: int):
            async with semaphore:
                return await self.simulate_account_creation(account_num)
        
        # Create all tasks
        tasks = [process_account_with_semaphore(i) for i in range(1, self.total_accounts + 1)]
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks)
        
        elapsed_time = time.time() - start_time
        
        # Print summary
        self.log("", Colors.RESET)
        self.log("=" * 80, Colors.BOLD)
        self.log("📊 SIMULATION SUMMARY", Colors.BOLD)
        self.log("=" * 80, Colors.RESET)
        self.log(f"✅ Successful Accounts: {self.success_count}/{self.total_accounts}", Colors.GREEN)
        self.log(f"❌ Failed Accounts: {self.fail_count}/{self.total_accounts}", Colors.RED)
        self.log(f"⏱️  Total Time: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)", Colors.BLUE)
        self.log("", Colors.RESET)
        
        if self.failed_accounts:
            self.log("❌ Failed Account Details:", Colors.RED)
            for failed_account in self.failed_accounts:
                self.log(f"   • {failed_account}", Colors.RED)
        
        self.log("", Colors.RESET)


OTP_CODE_POOL = ["726883", "352983", "684922", "593426", "258322"]


class MockLoginSimulator(MockSignupSimulator):
    def __init__(
        self,
        accounts: List[AccountInfo],
        success_target: Optional[int] = None,
        proxy_file: str = "proxy.txt",
    ):
        total_attempts = len(accounts)
        if success_target is None:
            success_target = total_attempts
        super().__init__(total_accounts=total_attempts, success_target=success_target, proxy_file=proxy_file)
        self.login_failure_reasons = {
            "invalid_password": 0.35,
            "captcha_failed": 0.25,
            "session_timeout": 0.15,
            "network_error": 0.15,
            "account_locked": 0.10,
        }
        self.accounts = accounts
        self.emails = [account.email for account in accounts]
        self.account_proxies = [account.proxy or random.choice(self.proxies) for account in accounts]
        self.account_infos = accounts
        self.successful_accounts = []
        self.failed_login_accounts: List[AccountInfo] = []
        self.otp_codes_available = OTP_CODE_POOL.copy()

    def _choose_failure_reason(self) -> str:
        reasons, weights = zip(*self.login_failure_reasons.items())
        return random.choices(reasons, weights=weights, k=1)[0]

    async def simulate_login_attempt(self, attempt_num: int) -> bool:
        email = self.emails[attempt_num - 1]
        proxy = self.account_proxies[attempt_num - 1]
        account_info = self.account_infos[attempt_num - 1]
        will_succeed = not self.will_fail[attempt_num - 1]

        self.log("", Colors.RESET)
        self.log("=" * 80, Colors.BOLD)
        self.log(
            f"🔐 Attempting BLS Login #{attempt_num}/{self.total_accounts}",
            Colors.BOLD,
        )
        self.log("=" * 80, Colors.RESET)

        proxy_parts = proxy.split(":") if proxy else []
        proxy_host = proxy_parts[0] if len(proxy_parts) > 0 else "unknown"
        session_id = proxy_parts[2] if len(proxy_parts) > 2 else "N/A"

        self.log(f"🌐 Proxy: {proxy_host}", Colors.BLUE)
        self.log(f"🔑 Session: {session_id}", Colors.BLUE)
        self.log(f"📧 Email: {email}", Colors.BLUE)

        try:
            await self.simulate_waf_challenge(attempt_num)

            self.log("🔑 Step 1: Opening login page...", Colors.MAGENTA)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("✅ Login page loaded", Colors.GREEN)

            self.log("📝 Step 2: Filling login form...", Colors.MAGENTA)
            await asyncio.to_thread(self.simulate_delay, 0.5, 1.5)
            self.log("✅ Entered email address", Colors.GREEN)
            await asyncio.to_thread(self.simulate_delay, 0.4, 0.8)
            password_display = account_info.bls_password or "******"
            await asyncio.to_thread(self.simulate_delay, 0.4, 0.8)
            self.log(f"✅ Entered password ({password_display})", Colors.GREEN)

            await asyncio.to_thread(self.simulate_delay, 0.5, 1)
            self.log("🔍 Checking Remember Me status", Colors.BLUE)
            await asyncio.to_thread(self.simulate_delay, 0.2, 0.4)
            self.log("✅ Remember Me left unchecked", Colors.GREEN)

            await self.simulate_captcha_solving(attempt_num)

            self.log("🚪 Step 3: Submitting login form...", Colors.MAGENTA)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("⏳ Waiting for server response...", Colors.YELLOW)

            await asyncio.to_thread(self.simulate_delay, 2, 4)

            if not will_succeed:
                reason = self._choose_failure_reason()
                self.log("", Colors.RESET)
                self.log("=" * 80, Colors.RED + Colors.BOLD)
                if reason == "invalid_password":
                    self.log(
                        f"❌ {Colors.BOLD}LOGIN FAILED - INVALID CREDENTIALS{Colors.RESET}{Colors.RED} ❌",
                        Colors.RED + Colors.BOLD,
                    )
                    self.log("⚠️ Server response: Password does not match", Colors.RED)
                elif reason == "captcha_failed":
                    self.log(
                        f"❌ {Colors.BOLD}LOGIN FAILED - CAPTCHA ERROR{Colors.RESET}{Colors.RED} ❌",
                        Colors.RED + Colors.BOLD,
                    )
                    self.log("⚠️ Captcha validation failed", Colors.RED)
                elif reason == "session_timeout":
                    self.log(
                        f"❌ {Colors.BOLD}LOGIN FAILED - SESSION TIMEOUT{Colors.RESET}{Colors.RED} ❌",
                        Colors.RED + Colors.BOLD,
                    )
                    self.log("⚠️ Session expired while waiting for response", Colors.RED)
                elif reason == "network_error":
                    self.log(
                        f"❌ {Colors.BOLD}LOGIN FAILED - NETWORK ISSUE{Colors.RESET}{Colors.RED} ❌",
                        Colors.RED + Colors.BOLD,
                    )
                    self.log("⚠️ Network error while submitting login", Colors.RED)
                else:
                    self.log(
                        f"❌ {Colors.BOLD}LOGIN FAILED - ACCOUNT LOCKED{Colors.RESET}{Colors.RED} ❌",
                        Colors.RED + Colors.BOLD,
                    )
                    self.log("⚠️ Too many attempts, account temporarily locked", Colors.RED)

                self.log(f"📧 Email: {email}", Colors.RED)
                self.log("=" * 80, Colors.RED + Colors.BOLD)
                self.log("", Colors.RESET)

                async with self._lock:
                    self.fail_count += 1
                    account_info.login_status = reason
                    self.failed_accounts.append(f"{email} ({reason})")
                    self.failed_login_accounts.append(account_info)
                return False

            self.log("⚠️ Password expired event detected. Updating password...", Colors.YELLOW)
            await asyncio.to_thread(self.simulate_delay, 5, 10)
            self.log("✅ Password updated successfully.", Colors.GREEN)

            self.log("", Colors.RESET)
            self.log("=" * 80, Colors.GREEN + Colors.BOLD)
            self.log(
                f"✅ {Colors.BOLD}LOGIN SUCCESSFUL{Colors.RESET}{Colors.GREEN} ✅",
                Colors.GREEN + Colors.BOLD,
            )
            self.log(f"📧 Email: {email}", Colors.GREEN + Colors.BOLD)
            self.log("=" * 80, Colors.GREEN + Colors.BOLD)
            self.log("", Colors.RESET)
            self.log(f"Now {email} succeed to login.", Colors.GREEN)

            await self.simulate_dashboard_booking_flow(account_info, attempt_num)

            await asyncio.to_thread(self.simulate_delay, 1, 2)

            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("📅 Checking appointment availability...", Colors.BLUE)
            await asyncio.to_thread(self.simulate_delay, 1, 3)
            self.log("✅ Dashboard loaded successfully", Colors.GREEN)

            async with self._lock:
                self.success_count += 1
                account_info.login_status = "success"
                self.successful_accounts.append(account_info)
            return True

        except Exception as exc:
            self.log(f"❌ Unexpected login error: {exc}", Colors.RED)
            async with self._lock:
                self.fail_count += 1
                account_info.login_status = "error"
                self.failed_accounts.append(f"{email} (error)")
                self.failed_login_accounts.append(account_info)
            return False

    async def simulate_dashboard_booking_flow(self, account_info: AccountInfo, attempt_num: int):
        email = account_info.email

        async def book_new_appointment(include_date_slot: bool, include_final_otp: bool):
            self.log("🖱️ Clicking 'Book New Appointment' button...", Colors.MAGENTA)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("🔄 Waiting for appointment booking page to load...", Colors.YELLOW)
            await asyncio.to_thread(self.simulate_delay, 1, 2)

            self.log("🤖 Step 5: Captcha encountered on appointment page", Colors.MAGENTA)
            self.log("🔍 Locating captcha iframe...", Colors.BLUE)
            await asyncio.to_thread(self.simulate_delay, 2, 3)
            self.log("📸 Capturing captcha images and question...", Colors.BLUE)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("🧠 Sending captcha payload to solver...", Colors.YELLOW)
            await asyncio.to_thread(self.simulate_delay, 4, 6)
            self.log("✅ Captcha solver returned solution", Colors.GREEN)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log(f"✅ Appointment captcha solved for {email}.", Colors.GREEN)

            self.log("⏳ Waiting for appointment form to fully load...", Colors.YELLOW)
            await asyncio.to_thread(self.simulate_delay, 2, 3)

            self.log("📝 Selecting Category: Prime Time", Colors.BLUE)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("📝 Selecting Location: Algiers", Colors.BLUE)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("📝 Selecting Visa Type: Visa Renewal", Colors.BLUE)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("📝 Selecting Visa Sub Type: ALG 4", Colors.BLUE)
            await asyncio.to_thread(self.simulate_delay, 1, 2)

            self.log("🖱️ Clicking Submit on appointment form...", Colors.MAGENTA)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("✅ Appointment form submitted successfully!", Colors.GREEN)

            if include_date_slot:
                self.log("⏳ Waiting for appointment availability page to load...", Colors.YELLOW)
                await asyncio.to_thread(self.simulate_delay, 2, 3)

                self.log("🪧 Selecting appointment date...", Colors.BLUE)
                await asyncio.to_thread(self.simulate_delay, 3, 5)
                selected_date = random.choice(["November 25", "November 30"])
                self.log(f"📅 Appointment Date chosen: {selected_date}", Colors.BLUE)

                self.log("🕠 Selecting appointment slot...", Colors.BLUE)
                await asyncio.to_thread(self.simulate_delay, 3, 5)
                slot = "08:30 - 09:15" if selected_date == "November 25" else "09:15 - 10:00"
                self.log(f"🕘 Appointment Slot: {slot}", Colors.BLUE)

                self.log("🖱️ Confirming selected appointment slot...", Colors.MAGENTA)
                await asyncio.to_thread(self.simulate_delay, 1, 2)
                self.log("✅ Appointment slot submitted for processing.", Colors.GREEN)

            if include_date_slot and include_final_otp:
                self.log("⏳ Waiting for slot confirmation page to load...", Colors.YELLOW)
                await asyncio.to_thread(self.simulate_delay, 3, 5)
                self.log("✅ Slot confirmation page ready.", Colors.GREEN)

                self.log("🛡️ Displaying consent popup for OTP.", Colors.YELLOW)
                await asyncio.to_thread(self.simulate_delay, 1, 2)
                self.log("✅ 'I agree to provide my consent' clicked.", Colors.GREEN)

                self.log("📬 Fetching OTP email for slot confirmation...", Colors.CYAN)
                await asyncio.to_thread(self.simulate_delay, 3, 5)
                otp_code = account_info.metadata.get("otp_code")
                if not otp_code:
                    if self.otp_codes_available:
                        otp_code = self.otp_codes_available.pop(0)
                    else:
                        otp_code = f"{random.randint(100000, 999999)}"
                    account_info.metadata["otp_code"] = otp_code
                self.log(f"✅ OTP email received with code: {otp_code}", Colors.GREEN)
                self.log("📝 Filling OTP into confirmation form...", Colors.BLUE)
                await asyncio.to_thread(self.simulate_delay, 1, 2)
                self.log("✅ OTP verification successful.", Colors.GREEN)

                self.log("🌐 Opening browser for manual confirmation review...", Colors.BLUE)
                await asyncio.to_thread(self.simulate_delay, 2, 4)
                self.log("✅ Browser ready for manual processing.", Colors.GREEN)

                account_info.metadata["appointment_captcha"] = "solved"

        async def handle_manage_appointments_edit():
            self.log("🌐 Navigating to Manage Appointments page...", Colors.BLUE)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("🛡️ AWS WAF challenge detected on Manage Appointments. Solving...", Colors.MAGENTA)
            await asyncio.to_thread(self.simulate_delay, 3, 5)
            self.log("✅ AWS WAF cleared for Manage Appointments.", Colors.GREEN)
            self.log("⏳ Waiting for Manage Appointments page to fully load...", Colors.YELLOW)
            await asyncio.to_thread(self.simulate_delay, 4, 7)

            self.log("🖱️ Clicking 'Edit' button for the first appointment entry...", Colors.MAGENTA)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("✅ Edit dialog opened successfully.", Colors.GREEN)
            self.log("⏳ Waiting for edit form iframe to fully load...", Colors.YELLOW)
            await asyncio.to_thread(self.simulate_delay, 4, 6)

            self.log("📝 Updating applicant details inside edit form...", Colors.BLUE)
            await asyncio.to_thread(self.simulate_delay, 2, 3)
            self.log("📝 Verifying mandatory fields and attachments...", Colors.BLUE)
            await asyncio.to_thread(self.simulate_delay, 2, 3)

            self.log("🖱️ Clicking Submit on edit form...", Colors.MAGENTA)
            await asyncio.to_thread(self.simulate_delay, 1, 2)
            self.log("✅ Appointment edit submitted successfully!", Colors.GREEN)

        # Stage 1: Terms & Conditions acceptance
        self.log(
            f"🌐 Redirecting {email} to main dashboard (https://algeria.blsspainglobal.com/dza/home/index)...",
            Colors.BLUE,
        )
        await asyncio.to_thread(self.simulate_delay, 1, 2)

        self.log("🖱️ Clicking 'Book New Appointment' button...", Colors.MAGENTA)
        await asyncio.to_thread(self.simulate_delay, 1, 2)
        self.log("📄 Terms and conditions dialog detected.", Colors.YELLOW)
        await asyncio.to_thread(self.simulate_delay, 2, 3)
        self.log("✅ Accepted data protection terms.", Colors.GREEN)

        self.log("📬 Fetching 'Accept Data Protection' email link...", Colors.CYAN)
        await asyncio.to_thread(self.simulate_delay, 3, 4)
        accept_link = random.choice(DATA_PROTECTION_LINKS)
        self.log(f"📨 Link retrieved: {accept_link}", Colors.CYAN)

        self.log("🌐 Opening data protection acceptance link...", Colors.BLUE)
        await asyncio.to_thread(self.simulate_delay, 1, 2)
        self.log("🔐 Step 2: Encountered AWS WAF challenge on acceptance link", Colors.MAGENTA)
        await asyncio.to_thread(self.simulate_delay, 2, 4)
        self.log("🔍 Inspecting WAF challenge iframe...", Colors.BLUE)
        await asyncio.to_thread(self.simulate_delay, 1, 2)
        self.log("🧠 Sending WAF payload to solver...", Colors.YELLOW)
        await asyncio.to_thread(self.simulate_delay, 4, 6)
        self.log("✅ Clearance token received for data protection page", Colors.GREEN)
        await asyncio.to_thread(self.simulate_delay, 1, 2)
        self.log("✅ Data protection acceptance confirmed.", Colors.GREEN)

        self.log("🏠 Clicking 'Go to Home' button...", Colors.MAGENTA)
        await asyncio.to_thread(self.simulate_delay, 1, 2)
        self.log("🔄 Returning to dashboard...", Colors.YELLOW)
        await asyncio.to_thread(self.simulate_delay, 1, 2)

        # Stage 2: Booking without date (leads to manage appointments)
        await book_new_appointment(include_date_slot=False, include_final_otp=False)
        await handle_manage_appointments_edit()

        self.log("🌐 Returning to main dashboard...", Colors.BLUE)
        await asyncio.to_thread(self.simulate_delay, 2, 3)

        # Stage 3: Final booking with date/slot and OTP handoff
        await book_new_appointment(include_date_slot=True, include_final_otp=True)
        return

    async def run_login_simulation(self, concurrent_workers: int = 5):
        self.log("", Colors.RESET)
        self.log("=" * 80, Colors.BOLD)
        self.log("=" * 80, Colors.RESET)

        start_time = time.time()
        semaphore = asyncio.Semaphore(concurrent_workers)

        async def process_attempt(attempt_num: int):
            async with semaphore:
                return await self.simulate_login_attempt(attempt_num)

        tasks = [process_attempt(i) for i in range(1, self.total_accounts + 1)]
        await asyncio.gather(*tasks)

        elapsed_time = time.time() - start_time

        self.log("", Colors.RESET)
        self.log("=" * 80, Colors.BOLD)
        self.log("📊 LOGIN SIMULATION SUMMARY", Colors.BOLD)
        self.log("=" * 80, Colors.RESET)
        self.log(
            f"✅ Successful Logins: {self.success_count}/{self.total_accounts}",
            Colors.GREEN,
        )
        self.log(
            f"❌ Failed Logins: {self.fail_count}/{self.total_accounts}",
            Colors.RED,
        )
        self.log(
            f"⏱️  Total Time: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)",
            Colors.BLUE,
        )
        self.log("", Colors.RESET)

        if self.failed_accounts:
            self.log("❌ Failed Login Details:", Colors.RED)
            for failed_account in self.failed_accounts:
                self.log(f"   • {failed_account}", Colors.RED)

        self.log("", Colors.RESET)


DEFAULT_SUCCESS_RATE = 0.83


def resolve_proxy_file() -> str:
    proxy_path = "../proxy.txt"
    if not os.path.exists(proxy_path):
        proxy_path = "proxy.txt"
    return proxy_path


def calculate_success_target(total_accounts: int, success_rate: float = DEFAULT_SUCCESS_RATE) -> int:
    if total_accounts <= 0:
        return 0

    estimated = int(round(total_accounts * success_rate))
    if estimated <= 0 and total_accounts > 0:
        estimated = 1

    return min(estimated, total_accounts)


def prompt_confirmation(message: str) -> bool:
    while True:
        response = input(f"{message} (yes/no): ").strip().lower()
        if response in {"yes", "y"}:
            return True
        if response in {"no", "n"}:
            return False
        print("Please respond with 'yes' or 'no'.")


def prompt_positive_int(message: str, max_value: Optional[int] = None) -> int:
    while True:
        raw_value = input(message).strip()
        try:
            value = int(raw_value)
        except ValueError:
            print("Please enter a valid positive integer.")
            continue

        if value <= 0:
            print("Please enter a value greater than zero.")
            continue

        if max_value is not None and value > max_value:
            print(f"Please enter a value less than or equal to {max_value}.")
            continue

        return value


def run_signup_simulation(
    total_accounts: int,
    proxy_file: str,
    concurrent_workers: int = 10,
    success_target: Optional[int] = None,
) -> MockSignupSimulator:
    if success_target is None:
        success_target = calculate_success_target(total_accounts)
    simulator = MockSignupSimulator(
        total_accounts=total_accounts,
        success_target=success_target,
        proxy_file=proxy_file,
    )
    asyncio.run(simulator.run_simulation(concurrent_workers=concurrent_workers))
    return simulator


def run_login_simulation(
    accounts: List[AccountInfo],
    proxy_file: str,
    concurrent_workers: int = 8,
) -> MockLoginSimulator:
    success_target = calculate_success_target(len(accounts))
    simulator = MockLoginSimulator(
        accounts=accounts,
        success_target=success_target,
        proxy_file=proxy_file,
    )
    asyncio.run(simulator.run_login_simulation(concurrent_workers=concurrent_workers))
    return simulator


def interactive_console():
    signup_ready_accounts: List[AccountInfo] = []
    login_failed_accounts: List[AccountInfo] = []
    logged_in_accounts: List[AccountInfo] = []
    proxy_file = resolve_proxy_file()
    signup_quota_remaining = 104

    while True:
        print("\n==============================")
        print("BLS Automation Console Board")
        print("==============================")
        print(
            f"1. Create account: How many account will you create (Signup backlog : {signup_quota_remaining})"
        )
        print(
            f"   Login retry backlog : {len(login_failed_accounts)}"
        )
        print(
            f"2. Booking Visa now : How many account will you use (Ready for login : {len(signup_ready_accounts)})"
        )
        print(
            f"   Logged-in accounts ready for booking : {len(logged_in_accounts)}"
        )
        print("3. Exit")

        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            if not prompt_confirmation("Confirm you want to create accounts"):
                continue

            total_accounts = prompt_positive_int("Enter number of accounts to create: ")
            if total_accounts > signup_quota_remaining:
                print(
                    f"⚠️ Requested {total_accounts} accounts but only {signup_quota_remaining} remain in backlog."
                )
                continue

            simulator = run_signup_simulation(total_accounts, proxy_file)
            new_accounts = simulator.successful_accounts
            signup_ready_accounts.extend(new_accounts)
            signup_quota_remaining -= total_accounts
            if signup_quota_remaining < 0:
                signup_quota_remaining = 0

            if login_failed_accounts and new_accounts:
                replacement_count = min(len(login_failed_accounts), len(new_accounts))
                if replacement_count:
                    print(
                        f"🔄 Replacing {replacement_count} previously failed login accounts with new signups."
                    )
                    login_failed_accounts = login_failed_accounts[replacement_count:]

            print(
                f"✅ {simulator.success_count} accounts created successfully. Ready for login : {len(signup_ready_accounts)}"
            )
            if simulator.fail_count:
                print(f"❌ {simulator.fail_count} signups failed during creation.")
                signup_quota_remaining += simulator.fail_count
            if login_failed_accounts:
                print(
                    f"⚠️ Login backlog awaiting replacement: {len(login_failed_accounts)} accounts."
                )

        elif choice == "2":
            if len(signup_ready_accounts) <= 0:
                print("⚠️ No available accounts. Please create accounts first.")
                continue

            if not prompt_confirmation("Confirm you want to book visas using available accounts"):
                continue

            accounts_to_use = prompt_positive_int(
                f"Enter number of accounts to use (max {len(signup_ready_accounts)}): ",
                max_value=len(signup_ready_accounts),
            )
            selected_accounts = signup_ready_accounts[:accounts_to_use]
            simulator = run_login_simulation(selected_accounts, proxy_file)
            # Remove attempted accounts from the available pool
            signup_ready_accounts = signup_ready_accounts[accounts_to_use:]

            failed_attempts = [acc for acc in selected_accounts if acc.login_status != "success"]
            if failed_attempts:
                login_failed_accounts.extend(failed_attempts)

            logged_in_accounts.extend(simulator.successful_accounts)
            print(
                f"✅ Login processed for {simulator.success_count} accounts. Ready for login : {len(signup_ready_accounts)}"
            )
            if simulator.fail_count:
                print(
                    f"❌ {simulator.fail_count} login attempts failed and moved to backlog."
                )
            if login_failed_accounts:
                print(
                    f"⚠️ Login backlog requires attention: {len(login_failed_accounts)} accounts."
                )
            print(f"🔐 Total logged-in accounts ready for booking: {len(logged_in_accounts)}")

        elif choice == "3":
            print("👋 Exiting console. Goodbye!")
            break

        else:
            print("Invalid selection. Please choose 1, 2, or 3.")


def main():
    interactive_console()


if __name__ == "__main__":
    main()

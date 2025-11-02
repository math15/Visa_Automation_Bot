"""
Interactive Visa Booking CLI
Run this file to manually book visas using the CLI
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.bls_modules.browser_login_handler import BrowserLoginHandler
from services.proxy_service import ProxyService
from models.database import Account
from database.config import SessionLocal
from loguru import logger

async def run_interactive_mode():
    """Run interactive CLI mode for visa booking"""
    try:
        logger.info("="*80)
        logger.info("📋 VISA RESERVATION SYSTEM")
        logger.info("="*80)
        logger.info("")
        
        # Step 1: Ask if user wants to book visa
        print("\n" + "="*80)
        response = await asyncio.to_thread(input, "❓ Do you want to book a Visa now? (yes/no): ")
        response = response.strip().lower()
        print("="*80 + "\n")
        
        if response not in ['yes', 'y']:
            logger.info("👋 Booking cancelled. Exiting interactive mode.")
            return
        
        # Step 2: Count available accounts in database (with email AND password)
        db = SessionLocal()
        try:
            account_count = db.query(Account).filter(
                Account.email.isnot(None),
                Account.password.isnot(None),
                Account.password != ''
            ).count()
            
            if account_count == 0:
                logger.warning("⚠️ No accounts found in database with both email and password!")
                logger.info("💡 Please create accounts with valid passwords using the frontend at http://localhost:3000/create-account")
                return
            
            logger.info(f"✅ Found {account_count} available account(s) with valid credentials in database")
            logger.info("")
            
            # Step 3: Ask how many accounts to use
            print("="*80)
            num_accounts_str = await asyncio.to_thread(input, f"❓ How many accounts do you want to use? (1-{account_count}): ")
            num_accounts_str = num_accounts_str.strip()
            print("="*80 + "\n")
            
            try:
                num_accounts = int(num_accounts_str)
                if num_accounts < 1 or num_accounts > account_count:
                    logger.error(f"❌ Invalid number. Please enter a number between 1 and {account_count}")
                    return
            except ValueError:
                logger.error("❌ Invalid input. Please enter a valid number.")
                return
            
            logger.info(f"✅ Will use {num_accounts} account(s) for booking")
            logger.info("")
            
            # Step 4: Get accounts from database (only with email AND password)
            accounts = db.query(Account).filter(
                Account.email.isnot(None),
                Account.password.isnot(None),
                Account.password != ''
            ).limit(num_accounts).all()
            
            if not accounts:
                logger.warning("⚠️ No accounts found with both email and password!")
                logger.info("💡 Please ensure accounts have valid passwords in the database")
                return
            
            logger.info(f"📋 Processing {len(accounts)} account(s) with valid credentials...")
            logger.info("")
            
            # Step 5: Ask for actual BLS password
            print("="*80)
            bls_password = await asyncio.to_thread(input, "🔒 Enter your BLS password: ")
            bls_password = bls_password.strip()
            print("="*80 + "\n")
            
            if not bls_password:
                logger.error("❌ Password is required!")
                return
            
            logger.info("✅ Password received")
            logger.info("")
            
            # Step 6: Try to login with each account
            proxy_service = ProxyService()
            login_handler = BrowserLoginHandler()
            
            for idx, account in enumerate(accounts, 1):
                logger.info(f"\n{'='*80}")
                logger.info(f"🔐 LOGIN ATTEMPT {idx}/{len(accounts)}")
                logger.info(f"{'='*80}")
                logger.info(f"📧 Email: {account.email}")
                logger.info("")
                
                # Get proxy for this account
                proxy_config = await proxy_service.get_algerian_proxy(db, avoid_recent=True)
                proxy_url = None
                if proxy_config:
                    if proxy_config.get('username') and proxy_config.get('password'):
                        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}"
                    else:
                        proxy_url = f"http://{proxy_config['host']}:{proxy_config['port']}"
                    logger.info(f"🌐 Using proxy: {proxy_config['host']}:{proxy_config['port']}")
                
                # Generate random visitor ID
                import random
                cookies = {
                    'visitorId_current': str(random.randint(10000000, 99999999))
                }
                
                # Try to login with user-provided BLS password
                try:
                    login_result = await login_handler.login_in_browser(
                        login_url="https://algeria.blsspainglobal.com/dza/account/Login",
                        email=account.email,
                        password=bls_password,  # Use user-provided BLS password
                        cookies=cookies,
                        proxy_url=proxy_url,
                        headless=True  # Run in background
                    )
                    
                    if login_result[0]:
                        logger.info(f"✅ Login successful for {account.email}!")
                    else:
                        logger.error(f"❌ Login failed for {account.email}: {login_result[1].get('error')}")
                except Exception as e:
                    logger.error(f"❌ Error during login: {e}")
                
                logger.info("")
            
            logger.info("")
            logger.info("="*80)
            logger.info("✅ LOGIN PHASE COMPLETE")
            logger.info("="*80)
            logger.info("💡 Next: Implement booking functionality")
            logger.info("="*80)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error in interactive mode: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(run_interactive_mode())
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


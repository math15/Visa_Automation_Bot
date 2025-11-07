"""
Main Interactive CLI for BLS Account Management
Run this file to create BLS accounts or book visas using the CLI
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.bls_modules.browser_login_handler import BrowserLoginHandler
from services.proxy_service import ProxyService
from services.bls_modules import BLSAccountCreator
from models.database import Account
from database.config import SessionLocal
from main import BLSAccountCreate
from datetime import datetime
from loguru import logger

async def main_menu():
    """Main interactive menu for BLS operations"""
    try:
        logger.info("="*80)
        logger.info("🚀 BLS ACCOUNT MANAGEMENT SYSTEM")
        logger.info("="*80)
        logger.info("")
        logger.info("📋 Available Options:")
        logger.info("   1. Create BLS Accounts")
        logger.info("   2. Book Visa")
        logger.info("   0. Exit")
        logger.info("")
        
        # Get user choice
        print("="*80)
        choice = await asyncio.to_thread(input, "❓ Choose an option (1/2/0): ")
        choice = choice.strip()
        print("="*80 + "\n")
        
        if choice == "1":
            await create_bls_accounts_menu()
        elif choice == "2":
            await book_visa_menu()
        elif choice == "0":
            logger.info("👋 Exiting...")
            return
        else:
            logger.error("❌ Invalid option. Please choose 1, 2, or 0.")
            logger.info("💡 Returning to main menu...")
            await main_menu()
            
    except Exception as e:
        logger.error(f"❌ Error in main menu: {e}")
        import traceback
        traceback.print_exc()

async def create_bls_accounts_menu():
    """Interactive menu for creating BLS accounts"""
    try:
        logger.info("="*80)
        logger.info("📝 CREATE BLS ACCOUNTS")
        logger.info("="*80)
        logger.info("")
        
        # Count available accounts in database
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
                await main_menu()
                return
            
            logger.info(f"✅ Found {account_count} available account(s) in database")
            logger.info("")
            
            # Ask how many accounts to create
            print("="*80)
            num_accounts_str = await asyncio.to_thread(input, f"❓ How many BLS accounts do you want to create? (1-{account_count}): ")
            num_accounts_str = num_accounts_str.strip()
            print("="*80 + "\n")
            
            try:
                num_accounts = int(num_accounts_str)
                if num_accounts < 1 or num_accounts > account_count:
                    logger.error(f"❌ Invalid number. Please enter a number between 1 and {account_count}")
                    await main_menu()
                    return
            except ValueError:
                logger.error("❌ Invalid input. Please enter a valid number.")
                await main_menu()
                return
            
            logger.info(f"✅ Will create {num_accounts} BLS account(s)")
            logger.info("")
            
            # Get accounts from database
            accounts = db.query(Account).filter(
                Account.email.isnot(None),
                Account.password.isnot(None),
                Account.password != ''
            ).limit(num_accounts).all()
            
            if not accounts:
                logger.warning("⚠️ No accounts found with both email and password!")
                logger.info("💡 Please ensure accounts have valid passwords in the database")
                await main_menu()
                return
            
            logger.info(f"📋 Processing {len(accounts)} account(s)...")
            logger.info("")
            
            # Create BLS accounts
            bls_creator = BLSAccountCreator()
            
            for idx, account in enumerate(accounts, 1):
                logger.info(f"\n{'='*80}")
                logger.info(f"🔄 CREATING BLS ACCOUNT {idx}/{len(accounts)}")
                logger.info(f"{'='*80}")
                logger.info(f"📧 Email: {account.email}")
                logger.info("")
                
                # Add delay between requests to avoid rate limiting (5-10 seconds)
                if idx > 1:
                    import random
                    delay = random.uniform(5, 10)
                    logger.info(f"⏱️  Waiting {delay:.1f}s before creating account (rate limiting prevention)...")
                    await asyncio.sleep(delay)
                
                # Convert Account to BLSAccountCreate
                account_data = BLSAccountCreate(
                    first_name=account.first_name,
                    last_name=account.last_name,
                    family_name=account.family_name or '',
                    date_of_birth=datetime.strptime(account.date_of_birth, "%Y-%m-%d"),
                    gender=account.gender,
                    marital_status=account.marital_status,
                    passport_number=account.passport_number,
                    passport_type=account.passport_type,
                    passport_issue_date=datetime.strptime(account.passport_issue_date, "%Y-%m-%d"),
                    passport_expiry_date=datetime.strptime(account.passport_expiry_date, "%Y-%m-%d"),
                    passport_issue_place=account.passport_issue_place,
                    passport_issue_country=account.passport_issue_country,
                    email=account.email,
                    mobile=account.mobile,
                    phone_country_code=account.phone_country_code,
                    birth_country=account.birth_country,
                    country_of_residence=account.country_of_residence,
                    number_of_members=account.number_of_members,
                    relationship=account.relationship,
                    primary_applicant=account.primary_applicant,
                    password=account.password
                )
                
                # Create BLS account
                try:
                    result = await bls_creator.create_account_with_browser(
                        account_data=account_data,
                        db=db
                    )
                    
                    if result.success:
                        logger.info(f"✅ BLS account created successfully for {account.email}!")
                    else:
                        logger.error(f"❌ Failed to create BLS account for {account.email}: {result.error_message}")
                except Exception as e:
                    logger.error(f"❌ Error during BLS account creation: {e}")
                
                logger.info("")
            
            logger.info("")
            logger.info("="*80)
            logger.info("✅ BLS ACCOUNT CREATION COMPLETE")
            logger.info("="*80)
            
        finally:
            db.close()
        
        # Return to main menu
        await main_menu()
            
    except Exception as e:
        logger.error(f"❌ Error in create accounts menu: {e}")
        import traceback
        traceback.print_exc()
        await main_menu()

async def book_visa_menu():
    """Interactive menu for booking visas (from interactive_booking.py)"""
    try:
        logger.info("="*80)
        logger.info("📋 VISA RESERVATION SYSTEM")
        logger.info("="*80)
        logger.info("")
        
        # Count available accounts in database (with email AND password)
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
                await main_menu()
                return
            
            logger.info(f"✅ Found {account_count} available account(s) with valid credentials in database")
            logger.info("")
            
            # Ask how many accounts to use
            print("="*80)
            num_accounts_str = await asyncio.to_thread(input, f"❓ How many accounts do you want to use? (1-{account_count}): ")
            num_accounts_str = num_accounts_str.strip()
            print("="*80 + "\n")
            
            try:
                num_accounts = int(num_accounts_str)
                if num_accounts < 1 or num_accounts > account_count:
                    logger.error(f"❌ Invalid number. Please enter a number between 1 and {account_count}")
                    await main_menu()
                    return
            except ValueError:
                logger.error("❌ Invalid input. Please enter a valid number.")
                await main_menu()
                return
            
            logger.info(f"✅ Will use {num_accounts} account(s) for booking")
            logger.info("")
            
            # Get accounts from database (only with email AND password)
            accounts = db.query(Account).filter(
                Account.email.isnot(None),
                Account.password.isnot(None),
                Account.password != ''
            ).limit(num_accounts).all()
            
            if not accounts:
                logger.warning("⚠️ No accounts found with both email and password!")
                logger.info("💡 Please ensure accounts have valid passwords in the database")
                await main_menu()
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
                await main_menu()
                return
            
            logger.info("✅ Password received")
            logger.info("")
            
            # Try to login with each account
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
                        headless=False  # Show browser window
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
        
        # Return to main menu
        await main_menu()
            
    except Exception as e:
        logger.error(f"❌ Error in booking menu: {e}")
        import traceback
        traceback.print_exc()
        await main_menu()

if __name__ == "__main__":
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


"""
Test script for BLS login functionality
Run this to test your BLS login implementation
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.bls_modules.browser_login_handler import BrowserLoginHandler
from services.proxy_service import ProxyService
from database.config import SessionLocal
from loguru import logger

async def test_login():
    """Test BLS login with real credentials"""
    
    print("=" * 80)
    print("   BLS Login Test")
    print("=" * 80)
    print()
    
    # Get credentials from user
    email = input("📧 Enter your BLS email: ").strip()
    password = input("🔒 Enter your password (optional, press Enter to skip): ").strip()
    
    if not email:
        print("❌ Email is required!")
        return
    
    print()
    print("🚀 Starting login test...")
    print()
    
    # Get proxy
    db = SessionLocal()
    try:
        proxy_service = ProxyService()
        proxy_config = await proxy_service.get_algerian_proxy(db, avoid_recent=True)
        
        proxy_url = None
        if proxy_config:
            if proxy_config.get('username') and proxy_config.get('password'):
                proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}"
            else:
                proxy_url = f"http://{proxy_config['host']}:{proxy_config['port']}"
            print(f"🌐 Using proxy: {proxy_config['host']}:{proxy_config['port']}")
        else:
            print("⚠️  No proxy available, using direct connection")
        
        print()
        
        # Generate random visitor ID
        import random
        cookies = {
            'visitorId_current': str(random.randint(10000000, 99999999))
        }
        
        # Test login
        login_handler = BrowserLoginHandler()
        
        print("⏳ Opening browser... (this may take a moment)")
        print()
        
        login_result = await login_handler.login_in_browser(
            login_url="https://algeria.blsspainglobal.com/dza/account/Login",
            email=email,
            password=password,
            cookies=cookies,
            proxy_url=proxy_url,
            headless=False  # Show browser so you can watch it
        )
        
        print()
        print("=" * 80)
        
        if login_result[0]:
            print("✅ LOGIN SUCCESSFUL!")
            print()
            print(f"📧 Email: {email}")
            print(f"🍪 Session cookies: {len(login_result[1].get('cookies', {}))} cookies")
            print()
            print("🎉 Your BLS login is working correctly!")
        else:
            print("❌ LOGIN FAILED")
            print()
            print(f"📧 Email: {email}")
            print(f"❌ Error: {login_result[1].get('error')}")
            print()
            print("💡 Check the logs above for details")
        
        print("=" * 80)
        
        # Keep browser open for 5 minutes for inspection
        print()
        print("⏳ Browser will stay open for 5 minutes for inspection...")
        await asyncio.sleep(300)
        print("✅ Test completed")
        
    finally:
        db.close()

if __name__ == "__main__":
    try:
        asyncio.run(test_login())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        logger.exception("Test failed")


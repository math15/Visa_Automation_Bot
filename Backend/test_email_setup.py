"""
Quick test script to verify email domain setup is working
Run this after configuring your Namecheap domain and Gmail
"""
import asyncio
import os
from dotenv import load_dotenv
from services.email_service import real_email_service

# Load environment variables
load_dotenv()

async def test_email_setup():
    print("🧪 Testing Email Domain Setup\n")
    
    # Check environment variables
    gmail_address = os.getenv('GMAIL_ADDRESS', '')
    gmail_app_password = os.getenv('GMAIL_APP_PASSWORD', '')
    
    print("📋 Configuration Check:")
    print(f"   Gmail Address: {gmail_address if gmail_address else '❌ NOT SET'}")
    print(f"   App Password: {'✅ SET' if gmail_app_password else '❌ NOT SET'}")
    print()
    
    if not gmail_address or not gmail_app_password:
        print("❌ ERROR: Gmail credentials not configured!")
        print("\n📝 Please add to Backend/.env:")
        print("   GMAIL_ADDRESS=admin@blsvisa.shop")
        print("   GMAIL_APP_PASSWORD=your-16-char-app-password")
        return False
    
    # Test email generation
    print("📧 Step 1: Testing email generation...")
    try:
        email, service = await real_email_service.generate_real_email()
        print(f"   ✅ Generated: {email}")
        print(f"   ✅ Service: {service}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    print()
    print("📬 Step 2: Email reception test")
    print(f"   📧 Generated Email: {email}")
    print()
    print("💡 Please:")
    print("   1. Open your email (the Gmail address you configured)")
    print("   2. Send a test email to: {email}")
    print("   3. In the subject or body, include: 'Your OTP is 123456'")
    print()
    
    input("   Press Enter after sending the test email...")
    print()
    
    # Test OTP retrieval
    print("📥 Step 3: Testing OTP retrieval...")
    try:
        otp = await real_email_service.wait_for_otp(email, service_name=service, timeout_seconds=30)
        
        if otp:
            print(f"   ✅ OTP Retrieved: {otp}")
            print()
            print("🎉 SUCCESS! Your email setup is working correctly!")
            print()
            print("✨ Your BLS registration will now:")
            print("   1. Generate custom domain emails automatically")
            print("   2. Receive BLS OTP emails")
            print("   3. Retrieve OTP via IMAP")
            print("   4. Complete registration automatically!")
            return True
        else:
            print("   ⚠️  No OTP found in email")
            print()
            print("💡 Possible issues:")
            print("   - Email not received yet (wait 30-60 seconds)")
            print("   - Catch-all forwarding not configured")
            print("   - DNS not propagated (wait 24-48 hours)")
            print("   - IMAP connection failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
        print("💡 Check:")
        print("   - App password is correct")
        print("   - 2-Step Verification is enabled")
        print("   - Domain is verified in Google Workspace")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("   BLS Email Domain Setup Test")
    print("=" * 60)
    print()
    
    success = asyncio.run(test_email_setup())
    
    print()
    print("=" * 60)
    if success:
        print("✅ Test PASSED - Ready for BLS registration!")
    else:
        print("❌ Test FAILED - Check configuration")
    print("=" * 60)


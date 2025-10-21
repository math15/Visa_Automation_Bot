#!/usr/bin/env python3
"""
Test the main app's captcha URL to see if it works
"""

import sys
import os
import time
from loguru import logger

# Add the awswaf python module to path
awswaf_path = os.path.join(os.path.dirname(__file__), '..', '..', 'awswaf', 'python')
sys.path.insert(0, awswaf_path)

logger.info(f"🔍 Adding awswaf path: {awswaf_path}")

# Check if path exists
if not os.path.exists(awswaf_path):
    logger.error(f"❌ AWS WAF path does not exist: {awswaf_path}")
    sys.exit(1)

try:
    from awswaf.aws import AwsWaf
    logger.info("✅ Successfully imported AwsWaf")
except ImportError as e:
    logger.error(f"❌ Failed to import awswaf: {e}")
    sys.exit(1)

def test_main_app_captcha_url():
    """Test the main app's captcha URL"""
    
    logger.info("🧪 Testing main app's captcha URL...")
    
    try:
        from curl_cffi import requests
        
        # Setup session with proxy (same as working registration page)
        session = requests.Session(impersonate="chrome")
        
        # Use proxy (same as working example)
        session.proxies = {
            'http': 'http://7929b5ffffe8ef9be2d0__cr.es:18b90548041f7f87@gw.dataimpulse.com:10000',
            'https': 'http://7929b5ffffe8ef9be2d0__cr.es:18b90548041f7f87@gw.dataimpulse.com:10000'
        }
        
        # Algerian headers (same as working registration page)
        session.headers = {
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
            # Algerian IP spoofing (same as working example)
            'X-Forwarded-For': '41.200.0.1',
            'X-Real-IP': '41.200.0.1',
            'X-Client-IP': '41.200.0.1',
            'CF-IPCountry': 'DZ',
        }
        
        # Test the main app's captcha URL (from logs)
        captcha_url = "https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha?data=ZdxAC%2f9E0jASzia1tlK2jx3oUlXRDmDZvrvO2u%2fOzS1C53GSOHvXE4sSkzn14VPEvHdcJ0Gy%2fdXib%2brc4Ln1vbwN0IrMB7OAqgK2U0k%2fMjo%3d"
        
        logger.info(f"🌐 Getting main app captcha page: {captcha_url}")
        response = session.get(captcha_url)
        
        logger.info(f"📡 Main app captcha response: {response.status_code}")
        logger.info(f"📄 Main app captcha content length: {len(response.text)}")
        
        # Save initial response
        timestamp = int(time.time())
        debug_file = f"main_app_captcha_response_{timestamp}.html"
        try:
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Main App Captcha Response -->\n")
                f.write(f"<!-- Timestamp: {timestamp} -->\n")
                f.write(f"<!-- URL: {captcha_url} -->\n")
                f.write(f"<!-- Status: {response.status_code} -->\n")
                f.write(f"<!-- Content Length: {len(response.text)} -->\n")
                f.write(response.text)
            logger.info(f"💾 Saved main app response to {debug_file}")
        except Exception as e:
            logger.warning(f"⚠️ Could not save main app response: {e}")
        
        # Check if we got a challenge
        if 'gokuProps' in response.text and 'challenge.js' in response.text:
            logger.info("🔍 AWS WAF challenge detected!")
            
            # Extract challenge data
            goku, host = AwsWaf.extract(response.text)
            
            logger.info(f"🔑 Goku props: {str(goku)[:100]}...")
            logger.info(f"🌐 Host: {host}")
            
            # Solve challenge
            logger.info("🔄 Solving AWS WAF challenge...")
            start = time.time()
            
            token = AwsWaf(goku, host, "algeria.blsspainglobal.com")()
            
            end = time.time()
            
            logger.info(f"✅ Challenge solved!")
            logger.info(f"🔑 Token: {token[:50]}...{token[-50:]}")
            logger.info(f"⏱️ Solve time: {end - start:.2f} seconds")
            
            # Test with token (make NEW request with token)
            logger.info("🌐 Testing with token...")
            session.headers.update({
                "cookie": "aws-waf-token=" + token
            })
            
            solved_response = session.get(captcha_url)
            logger.info(f"📡 Solved response: {solved_response.status_code}")
            logger.info(f"📄 Solved content length: {len(solved_response.text)}")
            
            # Save solved response
            debug_file_solved = f"main_app_captcha_solved_{timestamp}.html"
            try:
                with open(debug_file_solved, 'w', encoding='utf-8') as f:
                    f.write(f"<!-- Main App Solved Captcha Response -->\n")
                    f.write(f"<!-- Timestamp: {timestamp} -->\n")
                    f.write(f"<!-- URL: {captcha_url} -->\n")
                    f.write(f"<!-- Status: {solved_response.status_code} -->\n")
                    f.write(f"<!-- Content Length: {len(solved_response.text)} -->\n")
                    f.write(f"<!-- WAF Token: {token} -->\n")
                    f.write(solved_response.text)
                logger.info(f"💾 Saved main app solved response to {debug_file_solved}")
            except Exception as e:
                logger.warning(f"⚠️ Could not save main app solved response: {e}")
            
            # Check if we got actual captcha content
            if len(solved_response.text) > 100:
                logger.info(f"✅ Successfully bypassed WAF! Content length: {len(solved_response.text)}")
                
                # Check for captcha elements
                has_images = 'img' in solved_response.text.lower()
                has_captcha = 'captcha' in solved_response.text.lower()
                has_form = 'form' in solved_response.text.lower()
                has_html = '<html' in solved_response.text.lower() or '<!doctype' in solved_response.text.lower()
                
                logger.info(f"🔍 Content analysis:")
                logger.info(f"   - Has images: {has_images}")
                logger.info(f"   - Has captcha: {has_captcha}")
                logger.info(f"   - Has form: {has_form}")
                logger.info(f"   - Has HTML: {has_html}")
                
                # Show content preview
                logger.info(f"📄 Content preview (first 500 chars):")
                logger.info(f"{solved_response.text[:500]}...")
                
                return True
            else:
                logger.warning(f"⚠️ Bypass may have failed. Content length: {len(solved_response.text)}")
                return False
                
        else:
            logger.info("ℹ️ No AWS WAF challenge detected - direct access works")
            
            # Check if we got actual captcha content
            if len(response.text) > 100:
                logger.info(f"✅ Direct access successful! Content length: {len(response.text)}")
                return True
            else:
                logger.warning(f"⚠️ Direct access failed. Content length: {len(response.text)}")
                return False
            
    except Exception as e:
        logger.error(f"💥 Error testing main app captcha URL: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    logger.info("🧪 Testing Main App Captcha URL")
    logger.info("=" * 50)
    
    success = test_main_app_captcha_url()
    
    logger.info("\n" + "=" * 50)
    logger.info(f"🏁 Test Result: {'✅ Success' if success else '❌ Failed'}")
    logger.info("🏁 Test completed!")

if __name__ == "__main__":
    main()

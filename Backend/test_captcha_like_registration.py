#!/usr/bin/env python3
"""
Test script for captcha page WAF bypass - following the working registration page pattern
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

def test_captcha_page_like_registration(captcha_url=None):
    """Test captcha page using the same approach as working registration page"""
    
    logger.info("🧪 Testing captcha page WAF bypass using registration page approach...")
    
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
        
        # Use provided URL or default test URL
        if not captcha_url:
            captcha_url = "https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha?data=FRgSx1tL9%2f0G%2bD9EfeIZa81YXF6HZDO3BhxYtLDzyTOAF%2f4dZSNfsnPjwSpA7bFnzLUMcWuQmmMULXnB2iGIobnBCsP6QmCKJ6yMVLmXFpA%3d"
        
        logger.info(f"🌐 Getting captcha page: {captcha_url}")
        response = session.get(captcha_url)
        
        logger.info(f"📡 Captcha response: {response.status_code}")
        logger.info(f"📄 Captcha content length: {len(response.text)}")
        
        # Save initial response
        timestamp = int(time.time())
        debug_file = f"captcha_initial_response_{timestamp}.html"
        try:
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Initial Captcha Response -->\n")
                f.write(f"<!-- Timestamp: {timestamp} -->\n")
                f.write(f"<!-- URL: {captcha_url} -->\n")
                f.write(f"<!-- Status: {response.status_code} -->\n")
                f.write(f"<!-- Content Length: {len(response.text)} -->\n")
                f.write(response.text)
            logger.info(f"💾 Saved initial response to {debug_file}")
        except Exception as e:
            logger.warning(f"⚠️ Could not save initial response: {e}")
        
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
            debug_file_solved = f"captcha_solved_response_{timestamp}.html"
            try:
                with open(debug_file_solved, 'w', encoding='utf-8') as f:
                    f.write(f"<!-- Solved Captcha Response -->\n")
                    f.write(f"<!-- Timestamp: {timestamp} -->\n")
                    f.write(f"<!-- URL: {captcha_url} -->\n")
                    f.write(f"<!-- Status: {solved_response.status_code} -->\n")
                    f.write(f"<!-- Content Length: {len(solved_response.text)} -->\n")
                    f.write(f"<!-- WAF Token: {token} -->\n")
                    f.write(solved_response.text)
                logger.info(f"💾 Saved solved response to {debug_file_solved}")
            except Exception as e:
                logger.warning(f"⚠️ Could not save solved response: {e}")
            
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
                
                return {
                    'success': True,
                    'content': solved_response.text,
                    'waf_token': token
                }
            else:
                logger.warning(f"⚠️ Bypass may have failed. Content length: {len(solved_response.text)}")
                return {
                    'success': False,
                    'content': solved_response.text,
                    'waf_token': None
                }
                
        else:
            logger.info("ℹ️ No AWS WAF challenge detected - direct access works")
            
            # Check if we got actual captcha content
            if len(response.text) > 100:
                logger.info(f"✅ Direct access successful! Content length: {len(response.text)}")
                
                # Check for captcha elements
                has_images = 'img' in response.text.lower()
                has_captcha = 'captcha' in response.text.lower()
                has_form = 'form' in response.text.lower()
                has_html = '<html' in response.text.lower() or '<!doctype' in response.text.lower()
                
                logger.info(f"🔍 Content analysis:")
                logger.info(f"   - Has images: {has_images}")
                logger.info(f"   - Has captcha: {has_captcha}")
                logger.info(f"   - Has form: {has_form}")
                logger.info(f"   - Has HTML: {has_html}")
                
                return {
                    'success': True,
                    'content': response.text,
                    'waf_token': None
                }
            else:
                logger.warning(f"⚠️ Direct access failed. Content length: {len(response.text)}")
                return {
                    'success': False,
                    'content': response.text,
                    'waf_token': None
                }
            
    except Exception as e:
        logger.error(f"💥 Error testing captcha page WAF bypass: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'content': '',
            'waf_token': None
        }

def test_registration_page_for_comparison():
    """Test registration page for comparison"""
    
    logger.info("🔄 Testing registration page for comparison...")
    
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
        
        # Test registration URL
        register_url = "https://algeria.blsspainglobal.com/dza/account/RegisterUser"
        
        logger.info(f"🌐 Getting registration page: {register_url}")
        response = session.get(register_url)
        
        logger.info(f"📡 Registration response: {response.status_code}")
        logger.info(f"📄 Registration content length: {len(response.text)}")
        
        # Save registration response
        timestamp = int(time.time())
        debug_file = f"registration_response_{timestamp}.html"
        try:
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Registration Response -->\n")
                f.write(f"<!-- Timestamp: {timestamp} -->\n")
                f.write(f"<!-- URL: {register_url} -->\n")
                f.write(f"<!-- Status: {response.status_code} -->\n")
                f.write(f"<!-- Content Length: {len(response.text)} -->\n")
                f.write(response.text)
            logger.info(f"💾 Saved registration response to {debug_file}")
        except Exception as e:
            logger.warning(f"⚠️ Could not save registration response: {e}")
        
        if len(response.text) > 1000:
            logger.info(f"✅ Registration page access successful! Content length: {len(response.text)}")
            return True
        else:
            logger.warning(f"⚠️ Registration page access failed. Content length: {len(response.text)}")
            return False
            
    except Exception as e:
        logger.error(f"💥 Error testing registration page: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    logger.info("🧪 Starting Captcha Page Test (Registration Page Approach)")
    logger.info("=" * 70)
    
    # Test 1: Registration page for comparison
    logger.info("\n🔄 Test 1: Registration page for comparison")
    reg_success = test_registration_page_for_comparison()
    
    logger.info("\n" + "=" * 70)
    
    # Test 2: Captcha page using same approach
    logger.info("\n🔄 Test 2: Captcha page using registration page approach")
    captcha_success = test_captcha_page_like_registration()
    
    logger.info("\n" + "=" * 70)
    logger.info("🏁 Test Results:")
    logger.info(f"   Registration page: {'✅ Success' if reg_success else '❌ Failed'}")
    logger.info(f"   Captcha page: {'✅ Success' if captcha_success else '❌ Failed'}")
    logger.info("🏁 Test completed!")

if __name__ == "__main__":
    main()

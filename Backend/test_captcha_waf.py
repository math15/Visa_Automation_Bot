#!/usr/bin/env python3
"""
Test script for accessing captcha page with WAF bypass
Tests the specific captcha URL with proxy support
"""

import asyncio
import sys
import os
import time
from loguru import logger

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.bls_modules.waf_bypass import WAFBypassHandler

async def test_captcha_waf_bypass():
    """Test WAF bypass for captcha page"""
    
    # Configuration
    base_url = "https://algeria.blsspainglobal.com"
    captcha_url = "/dza/CaptchaPublic/GenerateCaptcha?data=FRgSx1tL9%2f0G%2bD9EfeIZa81YXF6HZDO3BhxYtLDzyTOAF%2f4dZSNfsnPjwSpA7bFnzLUMcWuQmmMULXnB2iGIobnBCsP6QmCKJ6yMVLmXFpA%3d"
    visitor_id = "22615162"
    
    # Proxy configuration (you can modify this)
    # Example proxy formats:
    # proxy_url = "http://user:pass@host:port"
    # proxy_url = "http://84.120.69.83:50100"  # Direct IP proxy
    proxy_url = "http://84.120.69.83:50100"  # Using proxy from logs
    
    logger.info("🚀 Starting captcha page WAF bypass test")
    logger.info(f"📍 Target URL: {base_url}{captcha_url}")
    logger.info(f"🆔 Visitor ID: {visitor_id}")
    logger.info(f"🌐 Proxy: {proxy_url or 'None (direct connection)'}")
    
    try:
        # Create WAF bypass handler
        waf_handler = WAFBypassHandler(base_url, captcha_url, visitor_id)
        
        # Prepare headers (matching browser request)
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'es-ES,es;q=0.9',
            'cache-control': 'max-age=0',
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
        }
        
        logger.info("🔄 Attempting comprehensive WAF bypass...")
        
        # Try comprehensive bypass
        bypass_result = await waf_handler.try_comprehensive_bypass(proxy_url, headers)
        
        if bypass_result and bypass_result.get('success'):
            logger.info("✅ WAF bypass successful!")
            
            content = bypass_result.get('content', '')
            waf_token = bypass_result.get('waf_token')
            
            logger.info(f"📊 Content length: {len(content)}")
            logger.info(f"🔑 WAF token: {waf_token[:50] if waf_token else 'None'}...")
            
            # Save response to file
            timestamp = int(time.time())
            debug_file = f"test_captcha_response_{timestamp}.html"
            
            try:
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(f"<!-- Test Captcha Response -->\n")
                    f.write(f"<!-- Timestamp: {timestamp} -->\n")
                    f.write(f"<!-- URL: {base_url}{captcha_url} -->\n")
                    f.write(f"<!-- WAF Token: {waf_token} -->\n")
                    f.write(f"<!-- Content Length: {len(content)} -->\n")
                    f.write(f"<!-- Headers: {headers} -->\n")
                    f.write(content)
                logger.info(f"💾 Saved response to {debug_file}")
            except Exception as e:
                logger.warning(f"⚠️ Could not save response: {e}")
            
            # Analyze content
            if len(content) > 0:
                logger.info("✅ Got non-empty content!")
                
                # Check for captcha elements
                has_images = 'img' in content.lower()
                has_captcha = 'captcha' in content.lower()
                has_form = 'form' in content.lower()
                has_html = '<html' in content.lower() or '<!doctype' in content.lower()
                
                logger.info(f"🔍 Content analysis:")
                logger.info(f"   - Has images: {has_images}")
                logger.info(f"   - Has captcha: {has_captcha}")
                logger.info(f"   - Has form: {has_form}")
                logger.info(f"   - Has HTML: {has_html}")
                
                # Show content preview
                logger.info(f"📄 Content preview (first 500 chars):")
                logger.info(f"{content[:500]}...")
                
            else:
                logger.warning("⚠️ Got empty content despite successful bypass")
                
        else:
            logger.error("❌ WAF bypass failed")
            logger.error(f"Bypass result: {bypass_result}")
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

async def test_direct_request():
    """Test direct request without WAF bypass for comparison"""
    
    logger.info("\n🔄 Testing direct request for comparison...")
    
    try:
        from curl_cffi import requests
        
        captcha_url = "https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha?data=FRgSx1tL9%2f0G%2bD9EfeIZa81YXF6HZDO3BhxYtLDzyTOAF%2f4dZSNfsnPjwSpA7bFnzLUMcWuQmmMULXnB2iGIobnBCsP6QmCKJ6yMVLmXFpA%3d"
        
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'es-ES,es;q=0.9',
            'cache-control': 'max-age=0',
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
        }
        
        session = requests.Session(impersonate="chrome")
        session.headers.update(headers)
        
        logger.info(f"🌐 Making direct request to: {captcha_url}")
        response = session.get(captcha_url, timeout=30)
        
        logger.info(f"📡 Direct response status: {response.status_code}")
        logger.info(f"📡 Direct response content length: {len(response.text)}")
        logger.info(f"📡 Direct response headers: {dict(response.headers)}")
        
        # Save direct response
        timestamp = int(time.time())
        debug_file = f"test_direct_response_{timestamp}.html"
        
        try:
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Direct Request Response -->\n")
                f.write(f"<!-- Timestamp: {timestamp} -->\n")
                f.write(f"<!-- URL: {captcha_url} -->\n")
                f.write(f"<!-- Status: {response.status_code} -->\n")
                f.write(f"<!-- Content Length: {len(response.text)} -->\n")
                f.write(f"<!-- Headers: {dict(response.headers)} -->\n")
                f.write(response.text)
            logger.info(f"💾 Saved direct response to {debug_file}")
        except Exception as e:
            logger.warning(f"⚠️ Could not save direct response: {e}")
        
        # Check if it's a WAF challenge
        is_waf_challenge = ('gokuProps' in response.text and 'challenge.js' in response.text) or response.status_code in [202, 403]
        logger.info(f"🔍 Is WAF challenge: {is_waf_challenge}")
        
        if is_waf_challenge:
            logger.info("🔍 WAF challenge detected - this confirms WAF bypass is needed")
        else:
            logger.info("✅ No WAF challenge - direct access works")
            
    except Exception as e:
        logger.error(f"❌ Direct request failed: {e}")

async def test_registration_page_comparison():
    """Test registration page WAF bypass for comparison"""
    
    logger.info("\n🔄 Testing registration page WAF bypass for comparison...")
    
    try:
        base_url = "https://algeria.blsspainglobal.com"
        register_url = "/dza/account/RegisterUser"
        visitor_id = "22615162"
        
        waf_handler = WAFBypassHandler(base_url, register_url, visitor_id)
        
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'es-ES,es;q=0.9',
            'cache-control': 'max-age=0',
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
        }
        
        bypass_result = await waf_handler.try_comprehensive_bypass("http://84.120.69.83:50100", headers)
        
        if bypass_result and bypass_result.get('success'):
            content = bypass_result.get('content', '')
            logger.info(f"✅ Registration page bypass successful! Content length: {len(content)}")
            
            # Save registration response
            timestamp = int(time.time())
            debug_file = f"test_registration_response_{timestamp}.html"
            try:
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(f"<!-- Registration Page Response -->\n")
                    f.write(f"<!-- Timestamp: {timestamp} -->\n")
                    f.write(f"<!-- URL: {base_url}{register_url} -->\n")
                    f.write(f"<!-- Content Length: {len(content)} -->\n")
                    f.write(content)
                logger.info(f"💾 Saved registration response to {debug_file}")
            except Exception as e:
                logger.warning(f"⚠️ Could not save registration response: {e}")
        else:
            logger.warning("⚠️ Registration page bypass failed")
            
    except Exception as e:
        logger.error(f"❌ Registration page test failed: {e}")

async def test_with_proxy():
    """Test captcha page with proxy"""
    
    logger.info("\n🔄 Testing captcha page with proxy...")
    
    # Test with different proxy configurations
    proxy_configs = [
        None,  # No proxy
        "http://84.120.69.83:50100",  # Direct IP proxy from logs
        # Add more proxy configurations if you have them:
        # "http://user:pass@84.120.69.83:50100",  # Authenticated proxy
        # "http://another-proxy:port",  # Another proxy
    ]
    
    for i, proxy_url in enumerate(proxy_configs):
        logger.info(f"\n--- Proxy Test {i+1}/{len(proxy_configs)}: {proxy_url or 'No Proxy'} ---")
        
        try:
            base_url = "https://algeria.blsspainglobal.com"
            captcha_url = "/dza/CaptchaPublic/GenerateCaptcha?data=FRgSx1tL9%2f0G%2bD9EfeIZa81YXF6HZDO3BhxYtLDzyTOAF%2f4dZSNfsnPjwSpA7bFnzLUMcWuQmmMULXnB2iGIobnBCsP6QmCKJ6yMVLmXFpA%3d"
            visitor_id = "22615162"
            
            waf_handler = WAFBypassHandler(base_url, captcha_url, visitor_id)
            
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'es-ES,es;q=0.9',
                'cache-control': 'max-age=0',
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
            }
            
            bypass_result = await waf_handler.try_comprehensive_bypass(proxy_url, headers)
            
            if bypass_result and bypass_result.get('success'):
                content = bypass_result.get('content', '')
                logger.info(f"✅ Captcha bypass successful with proxy {i+1}! Content length: {len(content)}")
                
                # Save response
                timestamp = int(time.time())
                debug_file = f"test_captcha_proxy_{i+1}_{timestamp}.html"
                try:
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(f"<!-- Captcha Response with Proxy {i+1} -->\n")
                        f.write(f"<!-- Timestamp: {timestamp} -->\n")
                        f.write(f"<!-- Proxy: {proxy_url} -->\n")
                        f.write(f"<!-- Content Length: {len(content)} -->\n")
                        f.write(content)
                    logger.info(f"💾 Saved proxy {i+1} response to {debug_file}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not save proxy {i+1} response: {e}")
            else:
                logger.warning(f"⚠️ Captcha bypass failed with proxy {i+1}")
                
        except Exception as e:
            logger.error(f"❌ Proxy test {i+1} failed: {e}")

async def main():
    """Main test function"""
    logger.info("🧪 Starting Captcha Page WAF Bypass Test")
    logger.info("=" * 60)
    
    # Test 1: Registration page comparison
    await test_registration_page_comparison()
    
    logger.info("\n" + "=" * 60)
    
    # Test 2: Direct request (to see if WAF challenge is present)
    await test_direct_request()
    
    logger.info("\n" + "=" * 60)
    
    # Test 3: WAF bypass with different proxies
    await test_with_proxy()
    
    logger.info("\n" + "=" * 60)
    logger.info("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(main())

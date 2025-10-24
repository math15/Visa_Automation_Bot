#!/usr/bin/env python3
"""
Working direct captcha submission test script based on the successful captcha_submitter.py code.
"""

import requests
import json

def test_working_captcha_submission():
    """Test direct captcha submission using the exact working code from captcha_submitter.py"""
    print("🚀 Starting working direct captcha submission test...")
    print("🧪 Testing direct captcha submission with working code...")
    
    # Submission URL
    submission_url = "https://algeria.blsspainglobal.com/dza/CaptchaPublic/SubmitCaptcha"
    
    # Proxy (update with your proxy) - DISABLED FOR TESTING
    proxy_url = None  # "http://7929b5ffffe8ef9be2d0__cr.es:18b90548041f7f87@gw.dataimpulse.com:10000"
    
    print(f"🔗 Submission URL: {submission_url}")
    if proxy_url:
        print(f"🌐 Proxy: {proxy_url[:50]}...")
    else:
        print("🌐 No proxy configured")
    
    try:
        # Create session (same as working code)
        session = requests.Session()
        print("🔄 Using standard requests.Session (same as working code)")
        
        # Set proxy if provided (same as working code)
        if proxy_url:
            if not proxy_url.startswith('http://'):
                proxy_url = f"http://{proxy_url}"
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            print(f"🌐 Using proxy: {proxy_url[:50]}...")
        else:
            print("🌐 Testing without proxy...")
        
        # Cookies from successful browser submission
        cookies = {
            '.AspNetCore.Antiforgery.cyS7zUT4rj8': 'CfDJ8lgywFVuzRdKg_dc1Q11WiAUCIIMnadzxHhe-AfEk_yKjzag8gHw3UwYFZPbGuBUI5iwd1h4HgrhpSZHezJw5khSwuUSbdYq1fRqjGJzNiP-nhBZiiXdYZn0Qfw9hIXIfdSOT-cgnul754dWiqYuqNc',
            'aws-waf-token': 'b26ae269-a7fb-45ce-bb61-7f1a55e807a0:CQoAkW8NcNFFAAAA:CRBtuqjq+UFQXSP43kgPls4y8oH2NLoVSckt+9lGaXQx/xWUH8A+EftVUPxcBHflZAa6eXa2dEnaWIuT47FLE4jFXmgtWRMQFUbLRUW8aHd/wo9lscWQQJyvPrVVdQ6RdNbGkAeOZrfRqLw1rzBJvQypGlAdLq9dmkoGy//ttEITObBCSI2q4ebXI25mhqGKS32fuqIr9cJD0PRj8jnHJrmtWi5ts3MjvCi/'
        }
        
        # Set cookies in session (same as working code)
        session.cookies.update(cookies)
        print(f"🍪 Set cookies: {list(cookies.keys())}")
        print(f"🍪 Final session cookies: {dict(session.cookies)}")
        
        # Prepare headers (EXACT same as working code)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://algeria.blsspainglobal.com',
            'Referer': 'https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Add AWS WAF token to headers if present in cookies (same as working code)
        if 'aws-waf-token' in cookies:
            headers['aws-waf-token'] = cookies['aws-waf-token']
            print(f"🔑 Added AWS WAF token to headers")
        
        # Prepare submission data (EXACT same as working code)
        captcha_id = 'FRgSx1tL9/0G+D9EfeIZa81YXF6HZDO3BhxYtLDzyTOAF/4dZSNfsnPjwSpA7bFnzLUMcWuQmmMULXnB2iGIobnBCsP6QmCKJ6yMVLmXFpA='
        selected_image_ids = ['qwpyufu', 'heevt', 'akfnj', 'txvgb']
        captcha_data = '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'
        request_verification_token = 'CfDJ8IgywFVuzRdKg_dc1Q11WiB-YIdOdAZIANllVw6q8fE_YJUNignnTDKFsHZLPe890cJdutt2OPxCK_U57Q2KlwzhOyGByaD0XUmWwcOwj_7wOE2kcEvYHNxgiu2PvlOzUfovKNdXqxWcbbSOc91oehU'
        
        # Prepare submission data (EXACT same as working code)
        data = {
            'Id': captcha_id,
            'SelectedImages': ','.join(selected_image_ids),
            'Captcha': captcha_data,
            '__RequestVerificationToken': request_verification_token  # Note: double underscore like working code
        }
        
        print(f"📤 Submission data prepared:")
        print(f"📤 Id: {captcha_id[:20]}...")
        print(f"📤 SelectedImages: {data['SelectedImages']}")
        print(f"📤 Captcha: {captcha_data[:20]}...")
        print(f"📤 __RequestVerificationToken: {request_verification_token[:20]}...")
        
        # Make POST request (EXACT same as working code)
        print(f"🔗 URL: {submission_url}")
        print(f"📤 Data: {data}")
        print(f"📋 Headers: {headers}")
        print(f"🍪 Cookies: {dict(session.cookies)}")
        
        # Add timing optimization - submit immediately to avoid session expiration (same as working code)
        import time
        print(f"⏰ Submitting captcha immediately to avoid session expiration...")
        
        response = session.post(
            submission_url,
            data=data,
            headers=headers,  # Use the prepared headers
            proxies=session.proxies if hasattr(session, 'proxies') else None,
            timeout=30
        )
        
        # Get response text first for debugging (same as working code)
        response_text = response.text
        
        # Enhanced console debugging (same as working code)
        print(f"📡 Captcha submission response status: {response.status_code}")
        print(f"📄 Captcha submission response body: {response_text}")
        print(f"🔍 Response headers: {dict(response.headers)}")
        
        # Check for WAF challenge headers specifically (same as working code)
        if 'x-amzn-waf-action' in response.headers:
            print(f"🛡️ WAF Action Header: {response.headers.get('x-amzn-waf-action')}")
        if 'x-amzn-waf-request-id' in response.headers:
            print(f"🛡️ WAF Request ID: {response.headers.get('x-amzn-waf-request-id')}")
        
        if response.status_code == 200:
            print("✅ Captcha submission successful!")
            # Check if submission was successful
            if "success" in response_text.lower() or "valid" in response_text.lower():
                print("✅ Captcha submission successful!")
                return True
            else:
                print(f"❌ Captcha submission failed - response doesn't indicate success")
                return False
        elif response.status_code == 202 and 'x-amzn-waf-action' in response.headers:
            waf_action = response.headers.get('x-amzn-waf-action')
            print(f"🔍 AWS WAF challenge detected on captcha submission! Action: {waf_action}")
            print(f"🔍 Challenge content length: {len(response_text)}")
            return False
        else:
            print(f"❌ Captcha submission failed with status: {response.status_code}")
            return False
                
    except Exception as e:
        print(f"❌ Error submitting captcha solution: {e}")
        return False
    
    print("\n📊 Test completed!")

if __name__ == "__main__":
    print("🚀 Starting working direct captcha submission test...")
    test_working_captcha_submission()

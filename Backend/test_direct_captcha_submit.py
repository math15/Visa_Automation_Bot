#!/usr/bin/env python3
"""
Direct captcha submission test script.
This script submits captcha solution directly to the submit URL with provided values.
"""

import requests
import json

def test_direct_captcha_submission():
    """Test direct captcha submission with provided cookies and payload"""
    print("🧪 Testing direct captcha submission...")
    
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
        # Create session
        session = requests.Session()
        
        # Set proxy
        use_proxy = True  # Set to True to test with proxy, False to test without proxy
        if use_proxy and proxy_url:
            if not proxy_url.startswith('http://'):
                proxy_url = f"http://{proxy_url}"
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            print(f"🌐 Using proxy: {proxy_url[:50]}...")
        else:
            print("🌐 Testing without proxy...")
        
        # Cookies provided by user
        cookies = {
            '.AspNetCore.Antiforgery.cyS7zUT4rj8': 'CfDJ8lgywFVuzRdKg_dc1Q11WiAUCIIMnadzxHhe-AfEk_yKjzag8gHw3UwYFZPbGuBUI5iwd1h4HgrhpSZHezJw5khSwuUSbdYq1fRqjGJzNiP-nhBZiiXdYZn0Qfw9hIXIfdSOT-cgnul754dWiqYuqNc',
            'aws-waf-token': 'b26ae269-a7fb-45ce-bb61-7f1a55e807a0:CQoAanUMU/9HAAAA:wjKYXyMSf1wUNpw2AYXz/X7MK4MM1cnNzyMewg/ssmDpa8JIVvB9NeLoTKsKCH6BP09SvzlwX4gxQN+YzcBdNBDC4jYLh868woMq7sRWY5U2+nvlhyZkqlD4Klu5ZAvC1FXtZat+IQGRUiby2Z4wbgq/Gmykp9m14028smHnXOF8y3PX34yQEZVALvBS3y6trVOL9DQLrzT4Jw+cOyyWVZAezqgNf4aJanFJ'
        }
        
        # Set cookies in session
        session.cookies.update(cookies)
        print(f"🍪 Set cookies: {list(cookies.keys())}")
        
        # Payload provided by user
        payload = {
            'Id': 'FRgSx1tL9/0G+D9EfeIZa81YXF6HZDO3BhxYtLDzyTOAF/4dZSNfsnPjwSpA7bFnzLUMcWuQmmMULXnB2iGIobnBCsP6QmCKJ6yMVLmXFpA=',
            'SelectedImages': 'qwpyufu,heevt,akfnj,txvgb',  # Your selected images
            'Captcha': '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',
            '__RequestVerificationToken': 'CfDJ8IgywFVuzRdKg_dc1Q11WiB-YIdOdAZIANllVw6q8fE_YJUNignnTDKFsHZLPe890cJdutt2OPxCK_U57Q2KlwzhOyGByaD0XUmWwcOwj_7wOE2kcEvYHNxgiu2PvlOzUfovKNdXqxWcbbSOc91oehU'
        }
        
        print(f"📤 Payload:")
        for key, value in payload.items():
            if value:
                print(f"   {key}: {value[:50]}...")
        
        # Headers for submission (matching the successful browser version exactly)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://algeria.blsspainglobal.com',
            'Referer': 'https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha?data=FRgSx1tL9%2f0G%2bD9EfelZa81YXF6HZDO3BhxYtLDzyTOAF%2f4dZSNfsnPjwSpA7bFnzLUMcWuQmmMULXnB2iGlobnBCsP6QmCKJ6yMVLmXFpA%3d',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Accept': "*/*",
            'Accept-Language': 'es-ES,es;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=1, i'
        }
        
        # Add AWS WAF token to headers if present in cookies
        if 'aws-waf-token' in cookies:
            headers['aws-waf-token'] = cookies['aws-waf-token']
            print(f"🔑 Added AWS WAF token to headers")
        
        # Make POST request
        print("\n📤 Making POST request for captcha submission...")
        response = session.post(submission_url, data=payload, headers=headers, timeout=30)
        
        print(f"📡 Submission Response Status: {response.status_code}")
        print(f"📄 Submission Response Headers: {dict(response.headers)}")
        print(f"📄 Submission Response Content Length: {len(response.text)}")
        print(f"📄 Submission Response Content Preview: {response.text[:500]}...")
        print(f"🍪 Session cookies after submission: {dict(session.cookies)}")
        
        if response.status_code == 200:
            print("✅ Captcha submission successful!")
        elif response.status_code == 400:
            print("❌ Bad Request - likely antiforgery token mismatch or invalid captcha data")
        elif response.status_code == 202:
            print("⚠️ AWS WAF challenge - tokens may have expired or submission triggered WAF again")
        elif response.status_code == 403:
            print("❌ Forbidden - cookies may be expired or invalid")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
        
        # Save submission response
        with open('debug_direct_submission_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("💾 Saved submission response to debug_direct_submission_response.html")
        
        # Save request details for debugging
        request_details = {
            'url': submission_url,
            'method': 'POST',
            'headers': headers,
            'cookies': dict(session.cookies),
            'payload': payload,
            'response_status': response.status_code,
            'response_headers': dict(response.headers),
            'response_content_length': len(response.text)
        }
        
        with open('debug_direct_submission_details.json', 'w', encoding='utf-8') as f:
            json.dump(request_details, f, indent=2)
        print("💾 Saved request details to debug_direct_submission_details.json")
        
    except Exception as e:
        print(f"❌ Error during direct captcha submission: {e}")

if __name__ == "__main__":
    print("🚀 Starting direct captcha submission test...")
    test_direct_captcha_submission()
    print("\n📊 Test completed!")
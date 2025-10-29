"""
Simple BLS Captcha Submission Test Script
Just edit the values below and run the script

HOW TO GET VALUES FROM BROWSER (Chrome DevTools):
=================================================
1. Open browser DevTools (F12)
2. Go to Network tab
3. Find the SUCCESSFUL POST request to "SubmitCaptcha" (Status 200)
4. Click on it → Headers tab
5. Scroll to "Request Headers" section
6. Copy these cookie values from "Cookie:" header:
   - aws-waf-token=...
   - .AspNetCore.Antiforgery.cyS7zUT4rj8=...
   - visitorId_current=...
7. Scroll down to "Form Data" section - copy these:
   - Id=...
   - SelectedImages=...
   - Captcha=...
   - __RequestVerificationToken=...

IMPORTANT NOTES:
- Get values from a SUCCESSFUL 200 OK request, not a failed one!
- Values expire quickly - refresh page and get new tokens
- x-amz-cf-id and x-amz-cf-pop are RESPONSE headers (you don't send them)
- CloudFront generates these when it processes your request
"""

# Try requests first, but recommend curl_cffi for better browser impersonation
try:
    from curl_cffi import requests
    print("✅ Using curl_cffi with browser impersonation")
except ImportError:
    import requests
    print("⚠️ Using standard requests - install curl_cffi for better results: pip install curl_cffi")

# AWS WAF bypass functionality
try:
    from awswaf.aws import AwsWaf
    HAS_AWS_WAF = True
    print("✅ AWS WAF bypass available")
except ImportError:
    HAS_AWS_WAF = False
    print("⚠️ AWS WAF bypass not available - install awswaf module")


def submit_captcha():
    """Submit captcha with your data"""
    
    # ===== EDIT THESE VALUES =====
    CAPTCHA_ID = "IllL9V8QD32+yFxKcKQx4j1tBCaretpFqZ+gQM95p+IbSV8AGeqBtwAac2U3sJhCRXpMLdqh2PLNOdEudmRrh+vx366kn+ZT9NisKNe8HVQ="  # The Id field from captcha page
    SELECTED_IMAGE_IDS = ["vrkjd", "opxud", "heyxs"]  # Which images were selected
    CAPTCHA_DATA = "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"
    REQUEST_VERIFICATION_TOKEN = "CfDJ8IgywFVuzRdKg_dc1Q11WiAHAt0Uh0y0xBfnV9ifNooEpxg3g7-1xlmZWYRbkkJR-4vv7S5_iYkMdMaVgRGiEOTFLsr3nVlX2o84zHqf3xUO3VNtOf7tCjQzZ1epwYs78ZOx7tqaaHQ4XBFUtk9Axro"
    
    # Optional but usually required
    AWS_WAF_TOKEN = "deba1094-1dc5-490f-b4f1-0cdc55b58de9:CgoAYHOGE28jAAAA:PM95UkZKmLv4ut+BmNvtliTxbhPArANByshV5WpM//IlqYJ4cmqpauwlQBcrzR2ZHG+iHJAOCePDcZDcpx8WbVXvhQfERtY/tOSg/WWTqf3Km8diD0GuQZ+v0uXUShdJRUmbV5+rqr7NP1ZxfC2MhrnrV3aPQXOgrRUtxVmeRPpF6Sv8wtxRQQbUcinTfhWJm8IKv+PpslbIlZx8iXFiijsOcP3qMmShSEbmGiAlc6r1beKynZFc6SmdcpwsDuQLrUXp"
    ANTIFORGERY_TOKEN = "CfDJ8IgywFVuzRdKg_dc1Q11WiAUCllMnadzxHhe-AfEk_yKjzag8gHw3UwYFZPbGuBUl5iwd1h4HgrhpSZHezJw5khSwuUSbdYq1fRqjGJzNiP-nhBZiiXdYZn0Qfw9hlXIfdSOT-cgnul754dWiqYuqNc"  # .AspNetCore.Antiforgery.cyS7zUT4rj8 from cookies
    CURRENT_USER_ID = "62215875"  # visitorId_current from cookies
    
    # Optional proxy - Format: http://username:password@host:port
    # IMPORTANT: These tokens might be expired! Get fresh values from browser dev tools
    PROXY_URL = 'http://7929b5ffffe8ef9be2d0__cr.es:18b90548041f7f87@gw.dataimpulse.com:10000'  # DataImpulse proxy
    # PROXY_URL = None  # Test without proxy
    
    # ===== END OF EDIT =====
    
    # URL
    url = "https://algeria.blsspainglobal.com/dza/CaptchaPublic/SubmitCaptcha"
    
    # Create session with browser impersonation (curl_cffi) if available
    try:
        # Try curl_cffi with Chrome impersonation (best for bypassing WAF)
        # Common supported versions: "chrome", "chrome110", "chrome104", "edge99", "safari15_3"
        session = requests.Session(impersonate="chrome110")
        print("✅ Using curl_cffi with Chrome impersonation")
    except (TypeError, ValueError) as e:
        # Fallback to standard requests
        try:
            session = requests.Session(impersonate="chrome")
            print("✅ Using curl_cffi with generic Chrome impersonation")
        except:
            session = requests.Session()
            print(f"⚠️ Using standard requests Session - {e}")
    
    # Set proxy - if PROXY_URL doesn't start with http:// or https://, we need to add it
    if PROXY_URL:
        # Ensure proxy URL has the correct scheme
        if not PROXY_URL.startswith('http://') and not PROXY_URL.startswith('https://'):
            PROXY_URL = f"http://{PROXY_URL}"
        
        session.proxies = {
            'http': PROXY_URL,
            'https': PROXY_URL
        }
        proxy_display = PROXY_URL.split('@')[-1] if '@' in PROXY_URL else PROXY_URL
        print(f"🌐 Using proxy: {proxy_display}")
        print(f"🔍 Proxy configured for session: {session.proxies}")
    else:
        print("⚠️ No proxy configured - using direct connection")
    
    # Headers - EXACTLY match browser developer tools from the image
    import urllib.parse
    
    # Build Referer URL with data parameter (URL encoded CAPTCHA_ID)
    # Note: The data parameter should be URL encoded like the browser
    referer_data_param = urllib.parse.quote(CAPTCHA_ID, safe='')
    referer_url = f'https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha?data={referer_data_param}'
    
    # Debug: Compare with browser
    print(f"\n🔍 Debug Referer URL: {referer_url[:100]}...")
    print(f"🔍 Expected format from browser should match this pattern")
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://algeria.blsspainglobal.com',
        'Referer': referer_url,  # MUST include data parameter!
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'es-ES,es;q=0.9',  # Spanish like browser shows
        'Accept-Encoding': 'gzip, deflate, br, zstd',  # Match browser exactly
        'Priority': 'u=1, i',
        'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': '',  # EMPTY string like browser shows
        'Sec-Fetch-Mode': 'cors',  # Different from script - browser shows 'cors'
        'Sec-Fetch-Site': 'same-origin',
    }
    
    # Cookies - Set both in session and headers
    if AWS_WAF_TOKEN:
        # Set cookies in the session
        session.cookies.set('aws-waf-token', AWS_WAF_TOKEN)
        
        # Also set in headers for compatibility
        cookies_list = [f"aws-waf-token={AWS_WAF_TOKEN}"]
        
        if ANTIFORGERY_TOKEN:
            session.cookies.set('.AspNetCore.Antiforgery.cyS7zUT4rj8', ANTIFORGERY_TOKEN)
            cookies_list.append(f".AspNetCore.Antiforgery.cyS7zUT4rj8={ANTIFORGERY_TOKEN}")
            
        if CURRENT_USER_ID:
            session.cookies.set('visitorId_current', CURRENT_USER_ID)
            cookies_list.append(f"visitorId_current={CURRENT_USER_ID}")
        
        headers['Cookie'] = '; '.join(cookies_list)
    
    # Form data
    data = {
        'Id': CAPTCHA_ID,
        'SelectedImages': ','.join(SELECTED_IMAGE_IDS),
        'Captcha': CAPTCHA_DATA,
        '__RequestVerificationToken': REQUEST_VERIFICATION_TOKEN
    }
    
    print(f"\n📤 Submitting captcha...")
    print(f"   Method: POST")
    print(f"   URL: {url}")
    print(f"   Id: {CAPTCHA_ID[:50]}...")
    print(f"   SelectedImages: {data['SelectedImages']}")
    print(f"   Referer: {referer_url}")
    print(f"\n🔍 COOKIES BEING SENT:")
    cookie_header = headers.get('Cookie', 'None')
    if cookie_header != 'None':
        # Parse cookies for better display
        cookies_list = cookie_header.split('; ')
        for cookie in cookies_list[:3]:  # Show first 3
            cookie_name = cookie.split('=')[0]
            cookie_value = cookie.split('=')[1][:50] if '=' in cookie else ''
            print(f"   {cookie_name}: {cookie_value}...")
    else:
        print("   No cookies!")
    
    try:
        # Send POST request
        print(f"\n🔍 Sending headers:")
        for key, value in headers.items():
            if key == 'Cookie':
                print(f"   {key}: {value[:80]}...")
            else:
                print(f"   {key}: {value}")
        
        response = session.post(url, data=data, headers=headers, timeout=30)
        
        print(f"\n📡 Response Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        # Check for CloudFront response headers
        if 'x-amz-cf-id' in response.headers:
            print(f"✅ Got CloudFront response ID: {response.headers['x-amz-cf-id']}")
        if 'x-amz-cf-pop' in response.headers:
            print(f"✅ Got CloudFront PoP: {response.headers['x-amz-cf-pop']}")
        print(f"📄 Response Length: {len(response.text)} chars")
        print(f"📄 Response:\n{response.text[:500]}...")  # Print first 500 chars only
        
        # Check if we got a WAF challenge
        if (response.status_code in [202, 403] or 
            ('gokuProps' in response.text and 'challenge.js' in response.text)):
            
            print("\n🔍 AWS WAF Challenge Detected! Attempting bypass...")
            
            if HAS_AWS_WAF:
                try:
                    # Extract challenge data
                    extract_result = AwsWaf.extract(response.text)
                    
                    if isinstance(extract_result, (list, tuple)) and len(extract_result) >= 2:
                        goku_props, host = extract_result[0], extract_result[1]
                    elif isinstance(extract_result, dict):
                        goku_props = extract_result.get('key') or extract_result.get('goku_props')
                        host = extract_result.get('host')
                    else:
                        print("❌ Could not extract WAF challenge data")
                        return False
                    
                    print(f"🔑 Extracted WAF challenge, solving...")
                    print(f"🌐 Host: {host}")
                    
                    # Solve the challenge
                    import time
                    start = time.time()
                    token = AwsWaf(goku_props, host, "algeria.blsspainglobal.com")()
                    elapsed = time.time() - start
                    
                    print(f"✅ WAF challenge solved in {elapsed:.2f} seconds!")
                    print(f"🔑 Token: {token[:50]}...")
                    
                    # Retry request with solved token
                    print("\n🔄 Retrying request with WAF token...")
                    
                    # Update cookies with solved token
                    headers['Cookie'] = headers.get('Cookie', '') + f"; aws-waf-token={token}"
                    
                    # Make the request again
                    retry_response = session.post(url, data=data, headers=headers, timeout=30)
                    
                    print(f"\n📡 Retry Response Code: {retry_response.status_code}")
                    print(f"📄 Retry Response:\n{retry_response.text[:500]}...")
                    
                    if retry_response.status_code == 200 and ("success" in retry_response.text.lower() or "valid" in retry_response.text.lower()):
                        print("\n✅ SUCCESS with WAF bypass!")
                        return True
                    else:
                        print("\n❌ FAILED even with WAF bypass")
                        return False
                        
                except Exception as e:
                    print(f"\n❌ WAF bypass failed: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                print("❌ AWS WAF module not available - cannot bypass")
                return False
        
        # No WAF challenge - check if it was successful
        if response.status_code == 200 and ("success" in response.text.lower() or "valid" in response.text.lower()):
            print("\n✅ SUCCESS!")
            return True
        else:
            print("\n❌ FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Simple BLS Captcha Submission Test")
    print("=" * 60)
    submit_captcha()


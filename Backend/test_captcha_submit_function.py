"""
Captcha Submission Function with AWS WAF Bypass
Clean reusable function for submitting BLS captcha solutions
"""

import requests
try:
    from curl_cffi import requests
    print("✅ Using curl_cffi with browser impersonation")
except ImportError:
    import requests
    print("⚠️ Using standard requests - install curl_cffi for better results")

try:
    from awswaf.aws import AwsWaf
    HAS_AWS_WAF = True
except ImportError:
    HAS_AWS_WAF = False
    print("⚠️ AWS WAF bypass not available")


def submit_bls_captcha(
    captcha_id: str,
    selected_image_ids: list,
    captcha_data: str,
    request_verification_token: str,
    aws_waf_token: str,
    antiforgery_token: str,
    visitor_id: str,
    proxy_url: str = None,
    verbose: bool = True
):
    """
    Submit BLS captcha solution with automatic AWS WAF bypass
    
    Args:
        captcha_id: The Id field from captcha page
        selected_image_ids: List of selected image IDs (e.g., ["vrkjd", "opxud", "heyxs"])
        captcha_data: The Captcha field from captcha page
        request_verification_token: The __RequestVerificationToken value
        aws_waf_token: AWS WAF token from cookies
        antiforgery_token: Antiforgery token from cookies (.AspNetCore.Antiforgery.cyS7zUT4rj8)
        visitor_id: visitorId_current value
        proxy_url: Proxy URL (optional)
        verbose: Print debug information
    
    Returns:
        dict with:
            - success: bool
            - status_code: int
            - response_text: str
            - error: str or None
    """
    
    # Import here to avoid issues
    import urllib.parse
    import time
    
    url = "https://algeria.blsspainglobal.com/dza/CaptchaPublic/SubmitCaptcha"
    
    if verbose:
        print("\n" + "=" * 60)
        print("BLS Captcha Submission with WAF Bypass")
        print("=" * 60)
    
    # Create session with browser impersonation
    try:
        session = requests.Session(impersonate="chrome110")
        if verbose:
            print("✅ Using curl_cffi with Chrome impersonation")
    except:
        session = requests.Session()
        if verbose:
            print("⚠️ Using standard requests Session")
    
    # Set proxy
    if proxy_url:
        if not proxy_url.startswith('http://') and not proxy_url.startswith('https://'):
            proxy_url = f"http://{proxy_url}"
        
        session.proxies = {'http': proxy_url, 'https': proxy_url}
        if verbose:
            proxy_display = proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url
            print(f"🌐 Using proxy: {proxy_display}")
    else:
        if verbose:
            print("⚠️ No proxy configured")
    
    # Build Referer URL with data parameter
    referer_data_param = urllib.parse.quote(captcha_id, safe='')
    referer_url = f'https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha?data={referer_data_param}'
    
    # Prepare headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://algeria.blsspainglobal.com',
        'Referer': referer_url,
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Priority': 'u=1, i',
        'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': '',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    
    # Set cookies
    cookie_parts = [
        f"aws-waf-token={aws_waf_token}",
        f".AspNetCore.Antiforgery.cyS7zUT4rj8={antiforgery_token}",
        f"visitorId_current={visitor_id}"
    ]
    headers['Cookie'] = '; '.join(cookie_parts)
    
    # Also set in session
    session.cookies.set('aws-waf-token', aws_waf_token)
    session.cookies.set('.AspNetCore.Antiforgery.cyS7zUT4rj8', antiforgery_token)
    session.cookies.set('visitorId_current', visitor_id)
    
    # Prepare form data
    data = {
        'Id': captcha_id,
        'SelectedImages': ','.join(selected_image_ids),
        'Captcha': captcha_data,
        '__RequestVerificationToken': request_verification_token
    }
    
    if verbose:
        print(f"\n📤 Submitting captcha...")
        print(f"   Method: POST")
        print(f"   URL: {url}")
        print(f"   SelectedImages: {data['SelectedImages']}")
    
    try:
        # Send initial request
        response = session.post(url, data=data, headers=headers, timeout=30)
        
        if verbose:
            print(f"\n📡 Response Code: {response.status_code}")
            if 'x-amzn-waf-action' in response.headers:
                print(f"🛡️ WAF Action: {response.headers.get('x-amzn-waf-action')}")
        
        # Check for WAF challenge
        if (response.status_code in [202, 403] or 
            ('gokuProps' in response.text and 'challenge.js' in response.text)):
            
            if verbose:
                print("\n🔍 AWS WAF Challenge Detected!")
            
            if not HAS_AWS_WAF:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'response_text': response.text,
                    'error': 'AWS WAF module not available - cannot bypass WAF challenge'
                }
            
            try:
                # Extract and solve WAF challenge
                extract_result = AwsWaf.extract(response.text)
                
                if isinstance(extract_result, (list, tuple)) and len(extract_result) >= 2:
                    goku_props, host = extract_result[0], extract_result[1]
                elif isinstance(extract_result, dict):
                    goku_props = extract_result.get('key') or extract_result.get('goku_props')
                    host = extract_result.get('host')
                else:
                    return {
                        'success': False,
                        'status_code': response.status_code,
                        'response_text': response.text,
                        'error': 'Could not extract WAF challenge data'
                    }
                
                if verbose:
                    print(f"🔑 Solving WAF challenge...")
                
                # Solve challenge
                start = time.time()
                token = AwsWaf(goku_props, host, "algeria.blsspainglobal.com")()
                elapsed = time.time() - start
                
                if verbose:
                    print(f"✅ Challenge solved in {elapsed:.2f} seconds!")
                
                # Retry with solved token
                headers['Cookie'] = headers.get('Cookie', '') + f"; aws-waf-token={token}"
                session.cookies.set('aws-waf-token', token)
                
                if verbose:
                    print("🔄 Retrying request with WAF token...")
                
                retry_response = session.post(url, data=data, headers=headers, timeout=30)
                
                if verbose:
                    print(f"📡 Retry Response: {retry_response.status_code}")
                
                # Check success
                is_success = retry_response.status_code == 200 and (
                    "success" in retry_response.text.lower() or 
                    "valid" in retry_response.text.lower()
                )
                
                return {
                    'success': is_success,
                    'status_code': retry_response.status_code,
                    'response_text': retry_response.text,
                    'error': None if is_success else 'Captcha submission failed'
                }
                
            except Exception as e:
                if verbose:
                    print(f"❌ WAF bypass failed: {e}")
                    import traceback
                    traceback.print_exc()
                
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'response_text': response.text,
                    'error': f'WAF bypass failed: {e}'
                }
        
        # No WAF challenge - check if successful
        is_success = response.status_code == 200 and (
            "success" in response.text.lower() or "valid" in response.text.lower()
        )
        
        if verbose:
            print(f"\n{'✅ SUCCESS!' if is_success else '❌ FAILED'}")
        
        return {
            'success': is_success,
            'status_code': response.status_code,
            'response_text': response.text,
            'error': None if is_success else 'Captcha submission failed'
        }
        
    except Exception as e:
        if verbose:
            print(f"❌ Error: {e}")
        
        return {
            'success': False,
            'status_code': None,
            'response_text': None,
            'error': str(e)
        }


def main():
    """Example usage"""
    
    # Example values - REPLACE WITH YOUR ACTUAL VALUES
    result = submit_bls_captcha(
        captcha_id="YOUR_CAPTCHA_ID",
        selected_image_ids=["vrkjd", "opxud", "heyxs"],
        captcha_data="YOUR_CAPTCHA_DATA",
        request_verification_token="YOUR_TOKEN",
        aws_waf_token="YOUR_WAF_TOKEN",
        antiforgery_token="YOUR_ANTIFORGERY_TOKEN",
        visitor_id="YOUR_VISITOR_ID",
        proxy_url="http://username:password@host:port",  # Optional
        verbose=True
    )
    
    print("\n" + "=" * 60)
    print(f"Result: {result}")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    main()


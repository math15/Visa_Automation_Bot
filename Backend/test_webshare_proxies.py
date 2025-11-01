"""
Test Webshare Proxies One by One
Format: host:port:username:password
"""

import requests
import time
from loguru import logger

# Your Webshare proxies
PROXIES = [
    "na.85802b8f3d264de5.abcproxy.vip:4950:9QUzdBG1PJ-zone-star-region-ES-session-YBTxwnMb-sessTime-120:71937272"
]

def parse_proxy(proxy_string):
    """Parse proxy string: host:port:username:password"""
    parts = proxy_string.split(':')
    return {
        'host': parts[0],
        'port': int(parts[1]),
        'username': parts[2],
        'password': parts[3]
    }

def test_proxy(proxy_dict, test_num):
    """Test a single proxy"""
    logger.info("=" * 80)
    logger.info(f"🔍 TEST #{test_num}/10")
    logger.info("=" * 80)
    logger.info(f"Host:     {proxy_dict['host']}")
    logger.info(f"Port:     {proxy_dict['port']}")
    logger.info(f"Username: {proxy_dict['username']}")
    logger.info(f"Password: {proxy_dict['password'][:10]}...")
    logger.info("")
    
    # Build proxy URL
    proxy_url = f"http://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['host']}:{proxy_dict['port']}"
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    results = {
        'proxy': proxy_dict,
        'tests': []
    }
    
    # Test 1: Basic IP check
    logger.info("📍 Test 1: Basic IP Check (api.ipify.org)")
    try:
        start = time.time()
        response = requests.get(
            'https://api.ipify.org?format=json',
            proxies=proxies,
            timeout=15
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            ip_data = response.json()
            ip = ip_data.get('ip', 'Unknown')
            logger.success(f"✅ SUCCESS! IP: {ip} ({elapsed:.2f}s)")
            results['tests'].append({'test': 'ipify', 'success': True, 'ip': ip, 'time': elapsed})
        else:
            logger.error(f"❌ FAILED! Status: {response.status_code}")
            results['tests'].append({'test': 'ipify', 'success': False, 'error': f"HTTP {response.status_code}"})
    except requests.exceptions.ProxyError as e:
        error_msg = str(e)
        if '407' in error_msg:
            logger.error(f"❌ AUTHENTICATION FAILED (407)")
            results['tests'].append({'test': 'ipify', 'success': False, 'error': 'AUTH_FAILED'})
        else:
            logger.error(f"❌ PROXY ERROR: {error_msg[:100]}")
            results['tests'].append({'test': 'ipify', 'success': False, 'error': 'PROXY_ERROR'})
    except requests.exceptions.Timeout:
        logger.error(f"❌ TIMEOUT (>15s)")
        results['tests'].append({'test': 'ipify', 'success': False, 'error': 'TIMEOUT'})
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)[:100]}")
        results['tests'].append({'test': 'ipify', 'success': False, 'error': str(e)[:50]})
    
    logger.info("")
    
    # Test 2: Alternative IP check
    logger.info("📍 Test 2: Alternative IP Check (httpbin.org)")
    try:
        start = time.time()
        response = requests.get(
            'https://httpbin.org/ip',
            proxies=proxies,
            timeout=15
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            ip_data = response.json()
            ip = ip_data.get('origin', 'Unknown')
            logger.success(f"✅ SUCCESS! IP: {ip} ({elapsed:.2f}s)")
            results['tests'].append({'test': 'httpbin', 'success': True, 'ip': ip, 'time': elapsed})
        else:
            logger.error(f"❌ FAILED! Status: {response.status_code}")
            results['tests'].append({'test': 'httpbin', 'success': False, 'error': f"HTTP {response.status_code}"})
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)[:100]}")
        results['tests'].append({'test': 'httpbin', 'success': False, 'error': str(e)[:50]})
    
    logger.info("")
    
    # Test 3: BLS Website
    logger.info("📍 Test 3: BLS Website (algeria.blsspainglobal.com)")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        }
        
        start = time.time()
        response = requests.get(
            'https://algeria.blsspainglobal.com/dza/account/RegisterUser',
            proxies=proxies,
            headers=headers,
            timeout=20,
            allow_redirects=True
        )
        elapsed = time.time() - start
        
        status = response.status_code
        
        if status == 200:
            logger.success(f"✅ SUCCESS! BLS website accessible ({elapsed:.2f}s)")
            results['tests'].append({'test': 'bls', 'success': True, 'status': status, 'time': elapsed})
        elif status == 403:
            logger.warning(f"⚠️ CloudFront 403 (blocked) - May need different IP")
            results['tests'].append({'test': 'bls', 'success': False, 'error': 'CLOUDFRONT_BLOCK', 'status': status})
        elif status == 202:
            logger.warning(f"⚠️ AWS WAF Challenge (202) - Normal, can be handled")
            results['tests'].append({'test': 'bls', 'success': True, 'status': status, 'time': elapsed})
        else:
            logger.warning(f"⚠️ Status: {status}")
            results['tests'].append({'test': 'bls', 'success': False, 'status': status})
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)[:100]}")
        results['tests'].append({'test': 'bls', 'success': False, 'error': str(e)[:50]})
    
    logger.info("")
    
    # Overall result
    success_count = sum(1 for test in results['tests'] if test.get('success', False))
    total_tests = len(results['tests'])
    
    if success_count == total_tests:
        logger.success(f"🎉 PROXY #{test_num} PASSED ALL TESTS ({success_count}/{total_tests})")
        results['overall'] = 'EXCELLENT'
    elif success_count >= 2:
        logger.success(f"✅ PROXY #{test_num} WORKING ({success_count}/{total_tests} tests passed)")
        results['overall'] = 'GOOD'
    elif success_count >= 1:
        logger.warning(f"⚠️ PROXY #{test_num} PARTIALLY WORKING ({success_count}/{total_tests} tests passed)")
        results['overall'] = 'PARTIAL'
    else:
        logger.error(f"❌ PROXY #{test_num} FAILED ALL TESTS")
        results['overall'] = 'FAILED'
    
    logger.info("")
    
    return results

def main():
    """Test all proxies"""
    logger.info("🚀 WEBSHARE PROXY TESTING")
    logger.info("=" * 80)
    logger.info(f"Total proxies to test: {len(PROXIES)}")
    logger.info("")
    
    all_results = []
    
    for i, proxy_string in enumerate(PROXIES, 1):
        proxy_dict = parse_proxy(proxy_string)
        result = test_proxy(proxy_dict, i)
        all_results.append(result)
        
        # Small delay between tests
        if i < len(PROXIES):
            logger.info("⏳ Waiting 2 seconds before next test...")
            logger.info("")
            time.sleep(2)
    
    # Final summary
    logger.info("=" * 80)
    logger.info("📊 FINAL SUMMARY")
    logger.info("=" * 80)
    
    excellent = sum(1 for r in all_results if r['overall'] == 'EXCELLENT')
    good = sum(1 for r in all_results if r['overall'] == 'GOOD')
    partial = sum(1 for r in all_results if r['overall'] == 'PARTIAL')
    failed = sum(1 for r in all_results if r['overall'] == 'FAILED')
    
    logger.info(f"Total Proxies:     {len(all_results)}")
    logger.info(f"🎉 Excellent:      {excellent} (passed all tests)")
    logger.info(f"✅ Good:           {good} (passed 2+ tests)")
    logger.info(f"⚠️  Partial:        {partial} (passed 1 test)")
    logger.info(f"❌ Failed:         {failed} (failed all tests)")
    logger.info("")
    
    working = excellent + good
    if working > 0:
        logger.success(f"🚀 {working} proxies are working and ready to use!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Add working proxies to database:")
        logger.info("   python manage_proxies.py add")
        logger.info("")
        logger.info("2. Or use the bulk import script (coming next)")
    else:
        logger.error("❌ No working proxies found!")
        logger.info("Please check:")
        logger.info("- Webshare account status")
        logger.info("- Credentials are correct")
        logger.info("- Proxy plan has traffic remaining")
    
    logger.info("")
    logger.info("=" * 80)
    
    return all_results

if __name__ == "__main__":
    main()


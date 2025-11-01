"""
Test ABC Proxy Spanish Proxies from proxylist.txt
Format: host:port:username:password
"""

import requests
import time
from loguru import logger
from typing import List, Dict, Tuple
import sys

def load_proxies_from_file(filepath: str) -> List[str]:
    """Load proxies from file"""
    try:
        with open(filepath, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return []

def parse_proxy(proxy_string):
    """Parse proxy string: host:port:username:password"""
    parts = proxy_string.split(':')
    return {
        'host': parts[0],
        'port': int(parts[1]),
        'username': parts[2],
        'password': parts[3]
    }

def test_proxy(proxy_dict, test_num, total):
    """Test a single proxy"""
    logger.info("=" * 80)
    logger.info(f"🔍 TEST #{test_num}/{total} - Spanish (ES) Proxy")
    logger.info("=" * 80)
    logger.info(f"Host:     {proxy_dict['host']}")
    logger.info(f"Port:     {proxy_dict['port']}")
    logger.info(f"Session:  {proxy_dict['username'].split('-session-')[1].split('-')[0] if '-session-' in proxy_dict['username'] else 'N/A'}")
    logger.info("")
    
    # Build proxy URL (HTTP method for ABC Proxy)
    proxy_url = f"http://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['host']}:{proxy_dict['port']}"
    proxies = {
        'http': proxy_url,
        'https': proxy_url  # ABC Proxy uses HTTP tunnel for HTTPS
    }
    
    results = {
        'proxy': proxy_dict,
        'tests': []
    }
    
    # Test 1: Basic IP check
    logger.info("📍 Test 1: IP Check & Location")
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
            
            # Get IP location info
            try:
                loc_response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
                if loc_response.status_code == 200:
                    loc_data = loc_response.json()
                    country = loc_data.get('country', 'Unknown')
                    country_code = loc_data.get('countryCode', 'Unknown')
                    city = loc_data.get('city', 'Unknown')
                    isp = loc_data.get('isp', 'Unknown')
                    logger.info(f"   📍 Location: {city}, {country} ({country_code})")
                    logger.info(f"   🏢 ISP: {isp}")
                    results['location'] = {
                        'country': country,
                        'country_code': country_code,
                        'city': city,
                        'isp': isp
                    }
            except:
                pass
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
    
    # Test 2: BLS Website (Critical Test!)
    logger.info("📍 Test 2: BLS Website (CRITICAL!)")
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
            logger.success(f"   🎉 This proxy will work for BLS registration!")
            results['tests'].append({'test': 'bls', 'success': True, 'status': status, 'time': elapsed})
        elif status == 202:
            logger.success(f"✅ AWS WAF Challenge (202) - This is NORMAL and GOOD! ({elapsed:.2f}s)")
            logger.info(f"   💡 Browser will handle this automatically")
            results['tests'].append({'test': 'bls', 'success': True, 'status': status, 'time': elapsed})
        elif status == 403:
            logger.error(f"❌ CloudFront 403 (blocked)")
            logger.warning(f"   ⚠️ This proxy might not work for BLS")
            results['tests'].append({'test': 'bls', 'success': False, 'error': 'CLOUDFRONT_BLOCK', 'status': status})
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
    
    # Check if BLS test passed (most important)
    bls_test = next((t for t in results['tests'] if t.get('test') == 'bls'), None)
    bls_passed = bls_test and bls_test.get('success', False)
    
    if bls_passed:
        logger.success(f"🎉 PROXY #{test_num} EXCELLENT - BLS ACCESSIBLE!")
        results['overall'] = 'EXCELLENT'
    elif success_count >= 1:
        logger.warning(f"⚠️ PROXY #{test_num} PARTIAL - Works but BLS blocked")
        results['overall'] = 'PARTIAL'
    else:
        logger.error(f"❌ PROXY #{test_num} FAILED ALL TESTS")
        results['overall'] = 'FAILED'
    
    logger.info("")
    
    return results

def main():
    """Test proxies from file"""
    logger.info("🚀 ABC PROXY SPANISH (ES) TESTING")
    logger.info("=" * 80)
    logger.info("Loading proxies from: ../proxylist.txt")
    logger.info("")
    
    # Load proxies
    proxy_strings = load_proxies_from_file('../proxylist.txt')
    
    if not proxy_strings:
        logger.error("❌ No proxies found in file!")
        return
    
    logger.info(f"📊 Found {len(proxy_strings)} proxies to test")
    logger.info("")
    
    # Ask how many to test
    print("How many proxies do you want to test?")
    print(f"  1. Test first 10 (quick)")
    print(f"  2. Test first 50 (medium)")
    print(f"  3. Test all {len(proxy_strings)} (slow)")
    print(f"  4. Enter custom number")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            test_count = 10
        elif choice == '2':
            test_count = 50
        elif choice == '3':
            test_count = len(proxy_strings)
        elif choice == '4':
            test_count = int(input("Enter number of proxies to test: "))
        else:
            test_count = 10
            logger.info("Invalid choice, testing first 10")
        
        test_count = min(test_count, len(proxy_strings))
        
    except KeyboardInterrupt:
        logger.info("\n\n👋 Testing cancelled by user")
        return
    except:
        test_count = 10
        logger.info("Using default: testing first 10")
    
    logger.info("")
    logger.info(f"🔍 Testing {test_count} proxies...")
    logger.info("")
    
    all_results = []
    
    for i in range(test_count):
        proxy_string = proxy_strings[i]
        proxy_dict = parse_proxy(proxy_string)
        result = test_proxy(proxy_dict, i + 1, test_count)
        all_results.append(result)
        
        # Small delay between tests
        if i < test_count - 1:
            logger.info("⏳ Waiting 1 second before next test...")
            logger.info("")
            time.sleep(1)
    
    # Final summary
    logger.info("=" * 80)
    logger.info("📊 FINAL SUMMARY")
    logger.info("=" * 80)
    
    excellent = sum(1 for r in all_results if r['overall'] == 'EXCELLENT')
    partial = sum(1 for r in all_results if r['overall'] == 'PARTIAL')
    failed = sum(1 for r in all_results if r['overall'] == 'FAILED')
    
    logger.info(f"Total Tested:      {len(all_results)}")
    logger.info(f"🎉 Excellent:      {excellent} (BLS accessible)")
    logger.info(f"⚠️  Partial:        {partial} (works but BLS blocked)")
    logger.info(f"❌ Failed:         {failed} (completely failed)")
    logger.info("")
    
    # Show locations
    spanish_count = 0
    for r in all_results:
        if 'location' in r and r['location'].get('country_code') == 'ES':
            spanish_count += 1
    
    if spanish_count > 0:
        logger.info(f"🇪🇸 Spanish IPs:    {spanish_count}/{len(all_results)}")
        logger.info("")
    
    if excellent > 0:
        logger.success(f"🚀 {excellent} proxies are working and BLS accessible!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Bulk import working proxies:")
        logger.info("   python import_abc_proxies.py")
        logger.info("")
        logger.info("2. Start BLS registration with these proxies!")
    elif partial > 0:
        logger.warning(f"⚠️ {partial} proxies work but BLS is blocking them")
        logger.info("These might be US/non-EU IPs. Try:")
        logger.info("- Request Spanish residential IPs from ABC Proxy")
        logger.info("- Or try anyway with browser (might bypass)")
    else:
        logger.error("❌ No working proxies found!")
        logger.info("Please check:")
        logger.info("- ABC Proxy account status")
        logger.info("- Credentials are correct")
        logger.info("- Proxy plan has traffic remaining")
    
    logger.info("")
    logger.info("=" * 80)
    
    return all_results

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n👋 Testing cancelled by user")
        sys.exit(0)


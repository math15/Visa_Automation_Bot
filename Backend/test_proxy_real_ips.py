#!/usr/bin/env python3
"""
Test real IP addresses of proxies by connecting through them
"""

import asyncio
import aiohttp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Proxy
from collections import Counter
import ssl

# Create database connection
engine = create_engine('sqlite:///./bls_database.db')
Session = sessionmaker(bind=engine)
db = Session()

# Services to check IP (we'll try multiple in case one fails)
IP_CHECK_SERVICES = [
    'https://api.ipify.org?format=json',
    'https://ifconfig.me/ip',
    'https://icanhazip.com',
    'https://ipinfo.io/ip'
]

async def check_proxy_ip(proxy_config, semaphore, service_url):
    """Check real IP through a proxy"""
    async with semaphore:
        try:
            # Build proxy URL
            if proxy_config.username and proxy_config.password:
                proxy_url = f"http://{proxy_config.username}:{proxy_config.password}@{proxy_config.host}:{proxy_config.port}"
            else:
                proxy_url = f"http://{proxy_config.host}:{proxy_config.port}"
            
            # Disable SSL verification for testing
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            timeout = aiohttp.ClientTimeout(total=15)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(service_url, proxy=proxy_url) as response:
                    if response.status == 200:
                        text = await response.text()
                        # Parse IP from different response formats
                        if 'ipify' in service_url:
                            import json
                            ip = json.loads(text).get('ip', text.strip())
                        else:
                            ip = text.strip()
                        
                        # Extract session ID for display
                        session_id = 'N/A'
                        if proxy_config.username and 'session-' in proxy_config.username:
                            session_id = proxy_config.username.split('session-')[1].split('-')[0]
                        
                        return {
                            'id': proxy_config.id,
                            'session': session_id,
                            'ip': ip,
                            'status': 'success'
                        }
                    else:
                        return {
                            'id': proxy_config.id,
                            'session': 'error',
                            'ip': None,
                            'status': f'HTTP {response.status}'
                        }
        except asyncio.TimeoutError:
            return {
                'id': proxy_config.id,
                'session': 'timeout',
                'ip': None,
                'status': 'timeout'
            }
        except Exception as e:
            return {
                'id': proxy_config.id,
                'session': 'error',
                'ip': None,
                'status': str(e)[:50]
            }

async def test_all_proxies(limit=None):
    """Test all proxies and show their real IPs"""
    
    print("=" * 80)
    print("TESTING REAL IP ADDRESSES OF PROXIES")
    print("=" * 80)
    
    # Get proxies from database
    query = db.query(Proxy).filter(Proxy.is_active == True)
    if limit:
        query = query.limit(limit)
    proxies = query.all()
    
    print(f"\n📊 Testing {len(proxies)} active proxies...")
    print(f"⏱️  This may take a few minutes...\n")
    
    # Use first available IP check service
    service_url = IP_CHECK_SERVICES[0]
    print(f"🌐 Using IP check service: {service_url}\n")
    
    # Limit concurrent requests to avoid overwhelming the proxy service
    semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests
    
    # Test all proxies
    tasks = [check_proxy_ip(proxy, semaphore, service_url) for proxy in proxies]
    results = []
    
    # Show progress
    completed = 0
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        completed += 1
        
        if result['status'] == 'success':
            print(f"✅ [{completed}/{len(proxies)}] Proxy {result['id']:3d} (session: {result['session']:10s}) → IP: {result['ip']}")
        else:
            print(f"❌ [{completed}/{len(proxies)}] Proxy {result['id']:3d} → {result['status']}")
    
    # Analyze results
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']
    
    print(f"\n✅ Successful: {len(successful)}/{len(proxies)}")
    print(f"❌ Failed:     {len(failed)}/{len(proxies)}")
    
    if successful:
        # Count unique IPs
        ips = [r['ip'] for r in successful]
        ip_counter = Counter(ips)
        unique_ips = len(set(ips))
        
        print(f"\n🎯 UNIQUE IP ADDRESSES:")
        print(f"   Total tested:  {len(successful)}")
        print(f"   Unique IPs:    {unique_ips}")
        print(f"   Duplicate IPs: {len(successful) - unique_ips}")
        
        if unique_ips == len(successful):
            print(f"\n   🎉 PERFECT! All proxies have different IP addresses! ✅")
        else:
            print(f"\n   ⚠️  Some proxies share IP addresses:")
            duplicates = {ip: count for ip, count in ip_counter.items() if count > 1}
            for ip, count in duplicates.items():
                print(f"      {ip} - used by {count} proxies")
                # Show which sessions share this IP
                sessions = [r['session'] for r in successful if r['ip'] == ip]
                print(f"         Sessions: {', '.join(sessions[:5])}{'...' if len(sessions) > 5 else ''}")
        
        # Show sample of IPs
        print(f"\n📋 SAMPLE OF DETECTED IPS (first 10):")
        for i, result in enumerate(successful[:10], 1):
            print(f"   {i:2d}. Session {result['session']:10s} → {result['ip']}")
        
        if len(successful) > 10:
            print(f"   ... and {len(successful) - 10} more")
        
        # IP range analysis
        print(f"\n🌍 IP RANGE ANALYSIS:")
        ip_prefixes = Counter(['.'.join(ip.split('.')[:2]) for ip in ips])
        print(f"   Different /16 subnets: {len(ip_prefixes)}")
        for prefix, count in ip_prefixes.most_common(5):
            print(f"      {prefix}.x.x: {count} IPs")
    
    if failed:
        print(f"\n❌ FAILED PROXIES:")
        failure_reasons = Counter([r['status'] for r in failed])
        for reason, count in failure_reasons.items():
            print(f"   {reason}: {count}")
    
    print("\n" + "=" * 80)
    
    db.close()

async def quick_test(num_proxies=10):
    """Quick test with limited number of proxies"""
    print(f"🔍 Quick test: Testing {num_proxies} random proxies...\n")
    await test_all_proxies(limit=num_proxies)

if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 80)
    print("PROXY IP ADDRESS TESTER")
    print("=" * 80)
    print("\nOptions:")
    print("  1. Quick test (10 proxies)")
    print("  2. Test all proxies")
    print()
    
    choice = input("Select option (1 or 2, default=1): ").strip() or "1"
    
    if choice == "2":
        print("\n⚠️  Testing all proxies may take 5-10 minutes...")
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm == 'y':
            asyncio.run(test_all_proxies())
        else:
            print("Cancelled.")
    else:
        asyncio.run(quick_test(num_proxies=10))


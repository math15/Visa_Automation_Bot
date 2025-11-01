"""
Comprehensive Proxy Testing Script
Tests all proxies in the database and reports their status
"""

import sqlite3
import requests
import time
from datetime import datetime
from loguru import logger
from typing import List, Dict, Tuple
import sys

class ProxyTester:
    def __init__(self, db_path: str = 'tesla_config.db'):
        self.db_path = db_path
        self.test_urls = [
            'https://api.ipify.org?format=json',  # Simple IP check
            'https://httpbin.org/ip',              # Alternative IP check
            'https://algeria.blsspainglobal.com/dza/account/RegisterUser'  # Actual BLS site
        ]
        
    def get_all_proxies(self) -> List[Dict]:
        """Get all proxies from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, host, port, username, password, country, is_active 
                FROM proxies 
                ORDER BY id
            ''')
            
            proxies = []
            for row in cursor.fetchall():
                proxies.append({
                    'id': row[0],
                    'host': row[1],
                    'port': row[2],
                    'username': row[3],
                    'password': row[4],
                    'country': row[5],
                    'is_active': row[6]
                })
            
            conn.close()
            return proxies
            
        except Exception as e:
            logger.error(f"Error reading database: {e}")
            return []
    
    def build_proxy_url(self, proxy: Dict) -> str:
        """Build proxy URL with authentication"""
        if proxy['username'] and proxy['password']:
            return f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
        else:
            return f"http://{proxy['host']}:{proxy['port']}"
    
    def test_proxy_simple(self, proxy: Dict, timeout: int = 10) -> Tuple[bool, str, str]:
        """
        Test proxy with a simple request
        Returns: (success, ip_address, error_message)
        """
        proxy_url = self.build_proxy_url(proxy)
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        try:
            start_time = time.time()
            response = requests.get(
                self.test_urls[0],
                proxies=proxies,
                timeout=timeout
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                ip_data = response.json()
                ip_address = ip_data.get('ip', 'Unknown')
                logger.success(f"✅ Proxy ID:{proxy['id']} works! IP: {ip_address} ({elapsed:.2f}s)")
                return True, ip_address, ""
            else:
                error_msg = f"HTTP {response.status_code}"
                logger.error(f"❌ Proxy ID:{proxy['id']} failed: {error_msg}")
                return False, "", error_msg
                
        except requests.exceptions.ProxyError as e:
            error_msg = str(e)
            
            # Check for specific errors
            if '407' in error_msg:
                if 'TRAFFIC_EXHAUSTED' in error_msg:
                    logger.error(f"❌ Proxy ID:{proxy['id']} - TRAFFIC EXHAUSTED")
                    return False, "", "TRAFFIC_EXHAUSTED"
                else:
                    logger.error(f"❌ Proxy ID:{proxy['id']} - AUTH FAILED (407)")
                    return False, "", "AUTH_FAILED"
            else:
                logger.error(f"❌ Proxy ID:{proxy['id']} - {error_msg[:100]}")
                return False, "", "PROXY_ERROR"
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Proxy ID:{proxy['id']} - TIMEOUT")
            return False, "", "TIMEOUT"
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Proxy ID:{proxy['id']} - CONNECTION ERROR")
            return False, "", "CONNECTION_ERROR"
            
        except Exception as e:
            logger.error(f"❌ Proxy ID:{proxy['id']} - {str(e)[:100]}")
            return False, "", str(e)[:50]
    
    def test_proxy_bls(self, proxy: Dict, timeout: int = 15) -> Tuple[bool, int, str]:
        """
        Test proxy against actual BLS website
        Returns: (success, status_code, error_message)
        """
        proxy_url = self.build_proxy_url(proxy)
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        }
        
        try:
            start_time = time.time()
            response = requests.get(
                self.test_urls[2],  # BLS website
                proxies=proxies,
                headers=headers,
                timeout=timeout,
                allow_redirects=True
            )
            elapsed = time.time() - start_time
            
            status = response.status_code
            
            if status == 200:
                logger.success(f"✅ BLS test passed for proxy ID:{proxy['id']} ({elapsed:.2f}s)")
                return True, status, ""
            elif status == 403:
                logger.warning(f"⚠️ Proxy ID:{proxy['id']} - BLS returned 403 (CloudFront block)")
                return False, status, "CLOUDFRONT_BLOCK"
            elif status == 202:
                logger.warning(f"⚠️ Proxy ID:{proxy['id']} - BLS returned 202 (WAF challenge)")
                return False, status, "WAF_CHALLENGE"
            else:
                logger.warning(f"⚠️ Proxy ID:{proxy['id']} - BLS returned {status}")
                return False, status, f"HTTP_{status}"
                
        except Exception as e:
            logger.error(f"❌ BLS test failed for proxy ID:{proxy['id']}: {str(e)[:100]}")
            return False, 0, str(e)[:50]
    
    def update_proxy_status(self, proxy_id: int, is_working: bool):
        """Update proxy status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE proxies 
                SET is_active = ?, 
                    validation_status = ?,
                    last_validated = ?
                WHERE id = ?
            ''', (
                1 if is_working else 0,
                'working' if is_working else 'failed',
                datetime.utcnow().isoformat(),
                proxy_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating database: {e}")
    
    def run_full_test(self, update_db: bool = True, test_bls: bool = False):
        """Run comprehensive proxy tests"""
        logger.info("=" * 80)
        logger.info("🚀 PROXY TESTING SCRIPT")
        logger.info("=" * 80)
        logger.info("")
        
        proxies = self.get_all_proxies()
        
        if not proxies:
            logger.error("❌ No proxies found in database!")
            logger.info("💡 Add proxies using: python manage_proxies.py add")
            return
        
        logger.info(f"📊 Found {len(proxies)} proxies in database")
        logger.info("")
        
        results = {
            'total': len(proxies),
            'working': 0,
            'failed': 0,
            'traffic_exhausted': 0,
            'auth_failed': 0,
            'timeout': 0,
            'details': []
        }
        
        # Test each proxy
        for i, proxy in enumerate(proxies, 1):
            logger.info(f"[{i}/{len(proxies)}] Testing Proxy ID:{proxy['id']} ({proxy['host']}:{proxy['port']})")
            logger.info(f"    Country: {proxy['country']} | Active: {proxy['is_active']}")
            logger.info(f"    Username: {proxy['username'][:15]}..." if proxy['username'] else "    No authentication")
            
            # Simple connectivity test
            success, ip, error = self.test_proxy_simple(proxy)
            
            result = {
                'proxy': proxy,
                'simple_test': success,
                'ip': ip,
                'error': error,
                'bls_test': None,
                'bls_status': None
            }
            
            if success:
                results['working'] += 1
                
                # Optional: Test against BLS website
                if test_bls:
                    logger.info(f"    🔍 Testing against BLS website...")
                    bls_success, bls_status, bls_error = self.test_proxy_bls(proxy)
                    result['bls_test'] = bls_success
                    result['bls_status'] = bls_status
                
                if update_db:
                    self.update_proxy_status(proxy['id'], True)
            else:
                results['failed'] += 1
                
                # Categorize failures
                if error == 'TRAFFIC_EXHAUSTED':
                    results['traffic_exhausted'] += 1
                elif error == 'AUTH_FAILED':
                    results['auth_failed'] += 1
                elif error == 'TIMEOUT':
                    results['timeout'] += 1
                
                if update_db:
                    self.update_proxy_status(proxy['id'], False)
            
            results['details'].append(result)
            logger.info("")
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def print_summary(self, results: Dict):
        """Print test summary"""
        logger.info("=" * 80)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Proxies:        {results['total']}")
        logger.info(f"✅ Working:           {results['working']}")
        logger.info(f"❌ Failed:            {results['failed']}")
        logger.info("")
        
        if results['failed'] > 0:
            logger.info("Failure Breakdown:")
            if results['traffic_exhausted'] > 0:
                logger.error(f"  💸 Traffic Exhausted: {results['traffic_exhausted']}")
            if results['auth_failed'] > 0:
                logger.error(f"  🔑 Auth Failed:       {results['auth_failed']}")
            if results['timeout'] > 0:
                logger.error(f"  ⏱️  Timeout:           {results['timeout']}")
            logger.info("")
        
        # Recommendations
        if results['traffic_exhausted'] > 0:
            logger.warning("⚠️  TRAFFIC EXHAUSTED DETECTED!")
            logger.warning("=" * 80)
            logger.warning("Your DataImpulse account has run out of bandwidth.")
            logger.warning("")
            logger.warning("Solutions:")
            logger.warning("1. Log into https://dataimpulse.com dashboard")
            logger.warning("2. Check your traffic usage and limits")
            logger.warning("3. Top up your account or wait for monthly reset")
            logger.warning("4. Or add proxies from a different provider")
            logger.warning("=" * 80)
        elif results['working'] == 0:
            logger.error("❌ NO WORKING PROXIES FOUND!")
            logger.error("The BLS registration cannot proceed without working proxies.")
        elif results['working'] < results['total']:
            logger.warning(f"⚠️  Only {results['working']}/{results['total']} proxies are working")
            logger.info("💡 Consider removing failed proxies or fixing their credentials")
        else:
            logger.success("✅ ALL PROXIES ARE WORKING!")
            logger.success("🚀 You're ready to run BLS account creation!")
        
        logger.info("")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test proxies in database')
    parser.add_argument('--no-update', action='store_true', help='Do not update database with results')
    parser.add_argument('--test-bls', action='store_true', help='Also test against BLS website (slower)')
    parser.add_argument('--db', default='tesla_config.db', help='Database path')
    
    args = parser.parse_args()
    
    tester = ProxyTester(db_path=args.db)
    tester.run_full_test(
        update_db=not args.no_update,
        test_bls=args.test_bls
    )


if __name__ == "__main__":
    main()


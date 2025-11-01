# 🔍 Proxy Testing Guide

## Quick Start

Test all proxies in your database:
```bash
python test_proxy.py
```

## Features

✅ **Comprehensive Testing**
- Tests all proxies in the database
- Checks connectivity and authentication
- Detects specific errors (traffic exhausted, auth failed, timeout)
- Updates database with validation results

✅ **Clear Error Detection**
- `TRAFFIC_EXHAUSTED` - Proxy bandwidth limit reached
- `AUTH_FAILED` - Invalid credentials (407 error)
- `TIMEOUT` - Proxy not responding
- `CONNECTION_ERROR` - Cannot connect to proxy server

✅ **Detailed Reports**
- Shows IP address for working proxies
- Response time for each test
- Summary statistics
- Actionable recommendations

## Usage

### Basic Test (Fast)
```bash
python test_proxy.py
```
Tests connectivity only (~1 second per proxy)

### Test Against BLS Website (Slower)
```bash
python test_proxy.py --test-bls
```
Also tests if proxies work with the actual BLS website (~15 seconds per proxy)

### Test Without Updating Database
```bash
python test_proxy.py --no-update
```
Run tests without marking proxies as active/inactive

### Custom Database Path
```bash
python test_proxy.py --db /path/to/database.db
```

## Understanding Results

### ✅ Working Proxy
```
✅ Proxy ID:1 works! IP: 185.123.45.67 (0.89s)
```
- Proxy is functional
- Shows the exit IP address
- Response time in seconds

### ❌ Traffic Exhausted
```
❌ Proxy ID:1 - TRAFFIC EXHAUSTED
```
**Action Required:** Top up your DataImpulse account or wait for monthly reset

### ❌ Auth Failed
```
❌ Proxy ID:1 - AUTH FAILED (407)
```
**Action Required:** Check username/password in database

### ❌ Timeout
```
❌ Proxy ID:1 - TIMEOUT
```
**Possible Causes:**
- Proxy server is down
- Network connectivity issues
- Firewall blocking connection

## Summary Report

After testing, you'll see a summary:

```
📊 TEST SUMMARY
================================================================================
Total Proxies:        10
✅ Working:           0
❌ Failed:            10

Failure Breakdown:
  💸 Traffic Exhausted: 10

⚠️  TRAFFIC EXHAUSTED DETECTED!
================================================================================
Your DataImpulse account has run out of bandwidth.

Solutions:
1. Log into https://dataimpulse.com dashboard
2. Check your traffic usage and limits
3. Top up your account or wait for monthly reset
4. Or add proxies from a different provider
================================================================================
```

## Troubleshooting

### All Proxies Show "TRAFFIC_EXHAUSTED"
This means your proxy provider account has run out of bandwidth.

**Solutions:**
1. **Top Up Account** - Add more traffic to your DataImpulse account
2. **Wait for Reset** - If you have a monthly plan, wait for the reset date
3. **Use Different Proxies** - Add proxies from another provider:
   ```bash
   python manage_proxies.py add
   ```

### All Proxies Show "AUTH_FAILED"
Your proxy credentials are incorrect.

**Solutions:**
1. Check your DataImpulse dashboard for correct credentials
2. Update proxies in database:
   ```bash
   python manage_proxies.py list
   python manage_proxies.py delete <id>
   python manage_proxies.py add
   ```

### All Proxies Show "TIMEOUT"
Network connectivity issue.

**Solutions:**
1. Check your internet connection
2. Try a different network
3. Check if your firewall is blocking proxy connections
4. Verify proxy server is online (check provider status page)

## Database Updates

By default, the script updates the database:
- Sets `is_active = 1` for working proxies
- Sets `is_active = 0` for failed proxies
- Updates `validation_status` field
- Records `last_validated` timestamp

This ensures the BLS account creator only uses working proxies.

## Integration with BLS Account Creator

The BLS account creation system automatically:
1. Queries for proxies where `is_active = 1`
2. Rotates through available proxies
3. Avoids recently used proxies

**Recommendation:** Run `python test_proxy.py` before starting BLS account creation to ensure you have working proxies.

## Advanced: Testing Specific Proxies

To test a specific proxy without the database:
```python
from test_proxy import ProxyTester

tester = ProxyTester()
proxy = {
    'id': 1,
    'host': 'gw.dataimpulse.com',
    'port': 10000,
    'username': 'your_username',
    'password': 'your_password',
    'country': 'ES',
    'is_active': 1
}

success, ip, error = tester.test_proxy_simple(proxy)
print(f"Success: {success}, IP: {ip}, Error: {error}")
```

## See Also

- `manage_proxies.py` - Add, remove, and manage proxies
- `PROXY_SETUP.md` - Guide for setting up proxies
- DataImpulse Dashboard: https://dataimpulse.com


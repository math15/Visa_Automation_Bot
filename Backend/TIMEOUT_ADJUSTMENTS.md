# Timeout Adjustments for Browser Captcha Solver

## Overview

All timeouts in the browser captcha solver have been **doubled** to accommodate slow-loading BLS pages and improved browser closing behavior when captcha token is received.

## Timeout Changes

### 1. Captcha Image Container Wait
**Before:** 10 seconds  
**After:** 20 seconds  
**Reason:** Captcha images take longer to load after WAF bypass

```python
# OLD
await page.wait_for_selector('.captcha-image-container', timeout=10000)

# NEW
await page.wait_for_selector('.captcha-image-container', timeout=20000)
```

### 2. Submit Button Click
**Before:** 5 seconds  
**After:** 10 seconds  
**Reason:** Submit button may take longer to become clickable

```python
# OLD
await page.click('button[type="submit"]', timeout=5000)

# NEW
await page.click('button[type="submit"]', timeout=10000)
```

### 3. API Response Wait
**Before:** 30 seconds  
**After:** 60 seconds  
**Reason:** BLS pages are very slow, submissions can take 30-60 seconds

```python
# OLD
max_wait = 30  # 30 seconds max

# NEW
max_wait = 60  # 60 seconds max
```

### 4. Network Idle Wait
**Before:** 5 seconds  
**After:** 10 seconds  
**Reason:** Page processing takes longer on slow connections

```python
# OLD
await page.wait_for_load_state('networkidle', timeout=5000)

# NEW
await page.wait_for_load_state('networkidle', timeout=10000)
```

## Browser Closing Behavior

### Immediate Close After Token

When captcha token is received, browser closes immediately:

```python
if response_received:
    logger.info(f"✅ Response received after {waited:.1f} seconds")
    
    # Close browser immediately (as user requested)
    logger.info("🔒 Closing browser after receiving captcha response...")
```

**Benefits:**
- No waiting for network idle if token already received
- Faster execution
- Cleaner shutdown

### Skip Unnecessary Waits

Network idle wait is only done if response NOT received:

```python
if not response_received:
    # Only wait if we didn't get response
    await page.wait_for_load_state('networkidle', timeout=10000)
```

## Summary of Timeouts

| Operation | Old Timeout | New Timeout | Multiplier |
|-----------|-------------|-------------|------------|
| Captcha images load | 10s | 20s | 2x |
| Submit button click | 5s | 10s | 2x |
| API response wait | 30s | 60s | 2x |
| Network idle | 5s | 10s | 2x |

## Timeline Examples

### Fast Page (20 seconds total)
```
00:00 - Navigate to page
00:05 - WAF challenge solved
00:10 - Captcha images loaded (within 20s timeout ✅)
00:12 - Images clicked
00:13 - Submit button clicked (within 10s timeout ✅)
00:20 - Response received (within 60s timeout ✅)
00:20 - Browser closed immediately ✅
```

### Slow Page (55 seconds total)
```
00:00 - Navigate to page
00:08 - WAF challenge solved
00:18 - Captcha images loaded (within 20s timeout ✅)
00:20 - Images clicked
00:22 - Submit button clicked (within 10s timeout ✅)
00:55 - Response received (within 60s timeout ✅)
00:55 - Browser closed immediately ✅
```

### Very Slow Page (timeout case)
```
00:00 - Navigate to page
00:10 - WAF challenge solved
00:25 - Captcha images loaded (within 20s timeout ✅)
00:27 - Images clicked
00:28 - Submit button clicked (within 10s timeout ✅)
01:28 - ⚠️ No response after 60 seconds
01:28 - Try network idle wait (10s)
01:38 - Browser closed with timeout
```

## Error Messages

### Old (Too Fast)
```
❌ Error loading captcha page: Timeout 10000ms exceeded
```

### New (More Time)
```
⏳ Still waiting for response... (15s / 60s)
⏳ Still waiting for response... (30s / 60s)
⏳ Still waiting for response... (45s / 60s)
✅ Response received after 48.2 seconds
```

## Configuration

All timeouts can be adjusted in `browser_captcha_solver.py`:

```python
# Captcha images
CAPTCHA_IMAGE_TIMEOUT = 20000  # 20 seconds

# Submit button
SUBMIT_BUTTON_TIMEOUT = 10000  # 10 seconds

# API response
MAX_RESPONSE_WAIT = 60  # 60 seconds

# Network idle
NETWORK_IDLE_TIMEOUT = 10000  # 10 seconds
```

## Performance Impact

### Before (Short Timeouts)
- ❌ Failures on slow pages
- ❌ Timeouts after 10-30 seconds
- ❌ Wasted time retrying

### After (Doubled Timeouts)
- ✅ Handles slow pages
- ✅ Waits up to 60 seconds
- ✅ Better success rate
- ✅ Immediate close when token received

## Benefits

1. **✅ Better compatibility** - Works with slow BLS pages
2. **✅ Fewer failures** - More time for operations
3. **✅ Faster completion** - Closes immediately after token
4. **✅ Progress visibility** - Logs every 5 seconds
5. **✅ Graceful handling** - Continues even if timeout

## Testing

Test with the updated timeouts:

```bash
cd Backend
python test_browser_captcha.py
```

Expected behavior:
- Captcha images load within 20 seconds
- Submit button clicks within 10 seconds
- Response received within 60 seconds
- Browser closes immediately after token

## Recommendations

For production use:
- **Keep doubled timeouts** - BLS pages are consistently slow
- **Monitor logs** - Watch for timeout warnings
- **Adjust if needed** - Can increase further for very slow networks
- **Use headless mode** - Faster performance

## Summary

✅ **All timeouts doubled** (2x original values)  
✅ **Captcha images: 10s → 20s**  
✅ **Submit button: 5s → 10s**  
✅ **API response: 30s → 60s**  
✅ **Network idle: 5s → 10s**  
✅ **Immediate close after token received**  
✅ **Skip unnecessary waits when token captured**  

These adjustments ensure the browser captcha solver works reliably with slow-loading BLS pages and closes efficiently when the captcha token is received. 🚀


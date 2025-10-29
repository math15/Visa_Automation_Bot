# BLS Captcha Generation Test Scripts

This directory contains test scripts for testing the BLS captcha generation endpoint with proxy support to avoid 403 issues.

## Files

- `test_captcha_generation.py` - Main test class with comprehensive functionality
- `run_captcha_test.py` - Simple test runner for easy configuration
- `README.md` - This documentation file

## Quick Start

1. **Update the configuration in `run_captcha_test.py`:**
   ```python
   # Replace with your proxy details
   PROXY_URL = "http://username:password@proxy_host:proxy_port"
   
   # Replace with your cookies (including AWS WAF token)
   COOKIES = {
       '.AspNetCore.Antiforgery.cyS7zUT4rj8': 'your_antiforgery_token',
       'aws-waf-token': 'your_aws_waf_token',
       # Add other cookies as needed
   }
   ```

2. **Run the test:**
   ```bash
   python run_captcha_test.py
   ```

## Expected Results

### With Valid Proxy + Cookies (including AWS WAF token):
- **Status 200**: Successfully accessed captcha generation page
- **Status 202**: AWS WAF challenge (expected behavior)
- **Status 403**: Invalid/expired cookies or missing AWS WAF token in cookies

### Without Proxy:
- **Status 403**: Forbidden (proxy is required)

## Configuration Details

### Proxy Format
```
http://username:password@proxy_host:proxy_port
```
or
```
http://proxy_host:proxy_port
```

### Required Cookies
The following cookies are typically required:
- `.AspNetCore.Antiforgery.cyS7zUT4rj8` - Antiforgery token
- `aws-waf-token` - AWS WAF token (included in cookies)
- Other session cookies as needed

**Note**: The AWS WAF token should be included in the cookies, not as a separate header.

## Troubleshooting

### 403 Forbidden Error
- Check if proxy is working
- Verify cookies are fresh and valid
- Ensure AWS WAF token is included in cookies
- Check if IP is blocked

### AWS WAF Challenge (202 Status)
- This is expected behavior
- The proxy is working correctly
- AWS WAF is challenging the request
- Manual intervention may be required

### Connection Errors
- Check proxy credentials
- Verify proxy server is accessible
- Check network connectivity

## Advanced Usage

For more advanced testing, use the main `CaptchaGenerationTester` class directly:

```python
from test_captcha_generation import CaptchaGenerationTester

# Initialize with proxy
tester = CaptchaGenerationTester(proxy_url="http://user:pass@host:port")

# Test with custom parameters
result = tester.test_captcha_generation(
    data_param="your_data_param",
    cookies={"cookie_name": "cookie_value", "aws-waf-token": "your_waf_token"}
)

# Test without proxy for comparison
result_no_proxy = tester.test_without_proxy(
    data_param="your_data_param",
    cookies={"cookie_name": "cookie_value", "aws-waf-token": "your_waf_token"}
)
```

## Notes

- The script automatically handles AWS WAF challenges
- Comprehensive logging is provided for debugging
- Both proxy and no-proxy tests are performed for comparison
- The script mimics a real browser with proper headers
- Timeout is set to 30 seconds for requests

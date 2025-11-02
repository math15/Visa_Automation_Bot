# Complete Namecheap Domain Setup Guide for BLS OTP

## 🎯 Goal
Purchase a domain from Namecheap and configure it to receive BLS OTP emails via Gmail IMAP

---

## ✅ STEP 1: Purchase Domain on Namecheap

### 1.1 Go to Namecheap
- Visit: https://www.namecheap.com
- Sign up / Login

### 1.2 Search for Domain
- Search for domain names (e.g., `blsvisa.shop`, `visabooking.shop`, `appointbls.shop`)
- Choose a `.shop`, `.com`, or `.net` domain
- Add to cart and checkout

### 1.3 Recommended Domain Names
```
- blsvisa.shop ✅ (already in your code!)
- visabooking.shop ✅ (already in your code!)
- appointbls.shop ✅ (already in your code!)
```

---

## ✅ STEP 2: Configure DNS with Gmail

### 2.1 Add Domain to Google Workspace
**Google Workspace is REQUIRED for email forwarding!**

1. Go to Google Workspace: https://workspace.google.com
2. Sign up for **Google Workspace Business Starter** ($6/user/month)
3. Verify domain ownership via:
   - DNS TXT record (easiest)
   - Upload HTML file to website

### 2.2 Add DNS Records to Namecheap

**Go to Namecheap Dashboard → Domain List → Manage**

#### Add MX Records (REQUIRED for Email)
```
Priority: 1, Host: @, Value: aspmx.l.google.com
Priority: 5, Host: @, Value: alt1.aspmx.l.google.com
Priority: 5, Host: @, Value: alt2.aspmx.l.google.com
Priority: 10, Host: @, Value: alt3.aspmx.l.google.com
Priority: 10, Host: @, Value: alt4.aspmx.l.google.com
```

#### Add TXT Record (Domain Verification)
```
Host: @
Value: google-site-verification=xxxxxxx (from Google Workspace)
```

#### Optional: Add CNAME for Email Aliases
```
Host: mail
Value: ghs.googlehosted.com
```

### 2.3 Wait for DNS Propagation
- **DNS changes take 24-48 hours to propagate**
- Check propagation: https://dnschecker.org

---

## ✅ STEP 3: Create Email Accounts in Google Workspace

### 3.1 Create Gmail Accounts
In Google Workspace Admin Console:

1. Go to **Users** → **Add Users**
2. For each domain, create one base email:
   ```
   admin@blsvisa.shop
   admin@visabooking.shop
   admin@appointbls.shop
   ```
3. Set password (remember this for IMAP!)

### 3.2 Generate App Password (REQUIRED!)
**Regular password won't work for IMAP!**

1. Go to **Google Account** → **Security** → **2-Step Verification** (enable it)
2. Go to **App Passwords**
3. Generate new app password for "Mail"
4. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

---

## ✅ STEP 4: Configure Code with Environment Variables

### 4.1 Create `.env` file in `Backend/` directory

```bash
# Gmail IMAP Configuration (for custom domains)
GMAIL_ADDRESS=admin@blsvisa.shop
GMAIL_APP_PASSWORD=your-16-char-app-password

# Note: The code will automatically use all 3 domains:
# - blsvisa.shop
# - visabooking.shop
# - appointbls.shop
```

### 4.2 Load Environment Variables

Your `Backend/services/email_service.py` already loads these:
```python
self.gmail_address = os.getenv('GMAIL_ADDRESS', '')
self.gmail_app_password = os.getenv('GMAIL_APP_PASSWORD', '')
```

---

## ✅ STEP 5: Test Email Reception

### 5.1 Run Test Script

Create `Backend/test_email_domain.py`:

```python
"""Test custom domain email reception"""
import asyncio
from services.email_service import real_email_service

async def test():
    # Generate email
    email, service = await real_email_service.generate_real_email()
    print(f"📧 Generated email: {email}")
    print(f"🔧 Service: {service}")
    
    # Send test email to yourself
    print(f"\n💡 Now send a test email to: {email}")
    input("Press Enter after sending email...")
    
    # Try to retrieve
    otp = await real_email_service.get_otp_from_email(email, service)
    print(f"📬 OTP: {otp}")

if __name__ == "__main__":
    asyncio.run(test())
```

### 5.2 Run Test
```bash
cd Backend
python test_email_domain.py
```

---

## ⚠️ CRITICAL: Email Forwarding Setup

**IMPORTANT:** Your custom domain emails need to **forward** to your main Gmail!

### Option 1: Catch-All Forward (RECOMMENDED!)

In Google Workspace Admin Console:

1. Go to **Apps** → **Google Workspace** → **Gmail** → **Routing**
2. Add routing rule:
   - **Add Setting**: "Also deliver to"
   - **Recipient address**: your-personal-email@gmail.com
   - **Apply to all messages**

**Result:** All emails to `*@blsvisa.shop` will forward to your Gmail inbox!

### Option 2: Create Email Aliases

For each generated email:
1. Go to **Users** → Your Admin Account → **Email Aliases**
2. Add alias: `user123456@blsvisa.shop`
3. Emails automatically forward to admin account

**BUT:** You need to manually create each alias (NOT scalable!)

---

## 🎯 RECOMMENDED SETUP (Best Practice)

### Setup 1: Catch-All Forward ✅ (EASIEST!)

**How it works:**
1. Configure catch-all forward in Google Workspace
2. Your code generates: `user123456@blsvisa.shop`
3. BLS sends OTP to: `user123456@blsvisa.shop`
4. **Email automatically forwards** to: `your-email@gmail.com`
5. Your code connects via IMAP and retrieves OTP!

**Benefits:**
- ✅ Unlimited emails (no alias limits)
- ✅ Zero manual setup per email
- ✅ Fully automated

**Setup:**
```bash
Google Workspace Admin Console
→ Apps → Google Workspace → Gmail → Routing
→ Add Setting: "Also deliver to"
→ Recipient: your-email@gmail.com
→ Apply to all messages
```

### Setup 2: Wildcard Email (ALTERNATIVE)

**Configure wildcard MX in DNS:**
1. Add MX record for `*@blsvisa.shop`
2. Point to Google Workspace
3. Configure catch-all user

**Less reliable but free!**

---

## 🔧 Integration with BLS Registration

### Current Flow (Already Implemented!)

```python
# 1. Generate email with custom domain
email, service = await real_email_service.generate_real_email()
# Returns: user123456@blsvisa.shop, "gmail_imap"

# 2. Use email in BLS registration
user_data['Email'] = email

# 3. Send OTP request to BLS
await otp_handler.send_otp_request(...)

# 4. Wait for OTP (automatically checks IMAP!)
otp = await email_service.wait_for_otp(email, timeout_seconds=60)
# Automatically connects to Gmail IMAP and retrieves OTP!

# 5. Verify OTP with BLS
await otp_handler.verify_otp(otp, ...)
```

### Email Service Priority

Your code already tries services in this order:

1. **Gmail IMAP** (custom domains) ← **USE THIS!** ✅
2. Mail.tm (free, but may be blocked)
3. Temp-Mail.io (premium)
4. Others...

---

## 💰 COST ESTIMATE

### Monthly Costs
- **Namecheap Domain:** ~$10/year = **$0.83/month**
- **Google Workspace:** $6/user/month
- **Total:** ~**$7/month per domain**

### Multiple Domains
You can use **3 domains** for rotation:
- blsvisa.shop
- visabooking.shop  
- appointbls.shop

**Total cost:** ~$20/month for all 3 domains

---

## 🚀 QUICK START CHECKLIST

- [ ] 1. Purchase 3 domains on Namecheap
- [ ] 2. Sign up for Google Workspace
- [ ] 3. Verify domain ownership
- [ ] 4. Add MX records in Namecheap
- [ ] 5. Wait 24-48h for DNS propagation
- [ ] 6. Create admin email accounts
- [ ] 7. Generate app passwords
- [ ] 8. Configure catch-all forwarding
- [ ] 9. Test email reception
- [ ] 10. Add GMAIL_ADDRESS and GMAIL_APP_PASSWORD to .env
- [ ] 11. Run test script to verify
- [ ] 12. Restart backend and test BLS registration!

---

## 🔍 TROUBLESHOOTING

### "Gmail credentials not configured"
**Solution:** Add to `.env`:
```bash
GMAIL_ADDRESS=admin@blsvisa.shop
GMAIL_APP_PASSWORD=your-app-password
```

### "No messages found"
**Possible causes:**
1. DNS not propagated yet (wait 48h)
2. MX records incorrect
3. Catch-all forwarding not configured
4. Email hasn't arrived yet (wait 30s)

### "IMAP authentication failed"
**Solution:**
- Make sure you're using **App Password**, not regular password
- Enable 2-Step Verification first

### "Domain not verified"
**Solution:**
- Add TXT record in Namecheap
- Wait for Google to verify

---

## 📚 ADDITIONAL RESOURCES

- Namecheap DNS: https://www.namecheap.com/support/knowledgebase/article.aspx/225
- Google Workspace Setup: https://support.google.com/a/answer/140034
- MX Records: https://support.google.com/a/answer/140034
- App Passwords: https://support.google.com/accounts/answer/185833

---

## ✨ WHAT YOU GET

After setup:
- ✅ Unlimited email addresses per domain
- ✅ Automatic email forwarding
- ✅ IMAP access via Gmail
- ✅ Real emails that BLS accepts
- ✅ Fully automated OTP retrieval
- ✅ No manual intervention needed!


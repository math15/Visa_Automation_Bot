# 🚀 Quick Start Checklist: Namecheap Domain + Gmail Setup for BLS OTP

## ✅ IMMEDIATE ACTION ITEMS

### 1. Purchase Domain on Namecheap (15 minutes)
- [ ] Go to https://www.namecheap.com
- [ ] Search and buy these domains:
  - ✅ `blsvisa.shop` (~$10/year)
  - ✅ `visabooking.shop` (~$10/year)  
  - ✅ `appointbls.shop` (~$10/year)

### 2. Sign Up for Google Workspace (15 minutes)
- [ ] Go to https://workspace.google.com
- [ ] Choose **Business Starter** plan ($6/month)
- [ ] Click "Get Started" and select "Claim domain"
- [ ] Enter your domain: `blsvisa.shop`
- [ ] Create admin email: `admin@blsvisa.shop`
- [ ] Set password and complete setup

### 3. Configure DNS in Namecheap (10 minutes)
**Go to:** Namecheap Dashboard → Domain List → Manage

#### Add MX Records (Email)
```
Type: MX
Host: @
Value: aspmx.l.google.com
Priority: 1

Type: MX
Host: @
Value: alt1.aspmx.l.google.com
Priority: 5

Type: MX
Host: @
Value: alt2.aspmx.l.google.com
Priority: 5

Type: MX
Host: @
Value: alt3.aspmx.l.google.com
Priority: 10

Type: MX
Host: @
Value: alt4.aspmx.l.google.com
Priority: 10
```

#### Add TXT Record (Verification)
**From Google Workspace:**
```
Type: TXT
Host: @
Value: google-site-verification=xxxxx (your key from Google)
```

### 4. Wait for DNS Propagation (24-48 hours)
- [ ] Check propagation: https://dnschecker.org
- [ ] Wait until MX records show "Google" worldwide
- [ ] Wait for Google to verify domain

### 5. Generate App Password (5 minutes)
**In Google Workspace:**
- [ ] Go to Google Account → Security
- [ ] Enable **2-Step Verification**
- [ ] Go to **App Passwords**
- [ ] Generate password for "Mail"
- [ ] Copy the **16-character password** (e.g., `abcd efgh ijkl mnop`)

### 6. Configure Catch-All Email Forwarding (10 minutes)
**In Google Workspace Admin Console:**
- [ ] Go to Apps → Google Workspace → Gmail → Routing
- [ ] Add routing rule:
  - **If**: Recipients match specific criteria
  - **Add Setting**: "Also deliver to"
  - **Recipient**: your-personal-email@gmail.com
  - **Apply to**: All messages
- [ ] Save

**What this does:** ALL emails sent to ANY address on your domain will forward to your Gmail inbox!

### 7. Configure Backend (.env file) (5 minutes)
**Create file:** `Backend/.env`

```bash
# Database
DATABASE_URL=sqlite:///./tesla_config.db

# Gmail IMAP (for OTP emails)
GMAIL_ADDRESS=admin@blsvisa.shop
GMAIL_APP_PASSWORD=your-16-char-app-password-from-google

# NoCaptchaAI (already set up)
NOCAPTCHAI_API_KEY=your-nocaptchai-key
```

### 8. Test Email Setup (5 minutes)
```bash
cd Backend
python test_email_setup.py
```

**Expected output:**
```
📧 Generated: user1234567890@blsvisa.shop
💡 Send test email to that address
📬 OTP Retrieved: 123456
✅ SUCCESS!
```

### 9. Restart Backend
```bash
# Stop backend (Ctrl+C if running)
cd Backend
python -m uvicorn main:app --reload
```

### 10. Test Full BLS Registration
- [ ] Go to frontend: http://localhost:3000
- [ ] Try creating a new BLS account
- [ ] Watch logs for:
  - ✅ Email generated with custom domain
  - ✅ OTP sent by BLS
  - ✅ OTP retrieved via IMAP
  - ✅ Registration completed!

---

## 🎯 WHAT YOU'RE BUILDING

```
BLS Website → Sends OTP → user123456@blsvisa.shop
                              ↓
                     Catch-All Forwarding
                              ↓
                    your-email@gmail.com
                              ↓
                     Gmail IMAP Connection
                              ↓
                    Your Code Retrieves OTP
                              ↓
                    Account Created! ✅
```

---

## ⚠️ CRITICAL NOTES

### Must-Have Setup
1. ✅ **Catch-All Forwarding** - Without this, emails won't work!
2. ✅ **App Password** - Regular password won't work for IMAP
3. ✅ **DNS Propagation** - Wait 24-48h before testing

### Cost Estimate
- Domains: $30/year (3 domains)
- Google Workspace: $6/month × 3 = $18/month
- **Total:** ~$240/year

### Alternatives (Lower Cost)
If you don't want to pay for all 3 domains:
- Use **Mail.tm** (free) as fallback
- Buy only 1 domain to start
- Test with Mail.tm first to verify flow works

---

## 🔍 TROUBLESHOOTING

### "No OTP found"
**Cause:** Catch-all forwarding not configured  
**Fix:** Set up routing rule in Google Workspace

### "IMAP authentication failed"
**Cause:** Using wrong password  
**Fix:** Use App Password, not regular password

### "Domain not verified"
**Cause:** DNS not propagated  
**Fix:** Wait 24-48 hours, check dnschecker.org

### "Email service not configured"
**Cause:** .env file missing or wrong location  
**Fix:** Create `Backend/.env` with credentials

---

## 📚 NEXT STEPS AFTER SETUP

Once working:
1. Buy all 3 domains
2. Set up rotation across domains
3. Monitor success rate
4. Scale up proxy usage
5. Automate account creation in bulk!

---

## ✅ COMPLETION CHECKLIST

- [ ] Domains purchased on Namecheap
- [ ] Google Workspace configured
- [ ] DNS records added and propagated
- [ ] Catch-all forwarding active
- [ ] App passwords generated
- [ ] .env file created in Backend/
- [ ] Test script passes
- [ ] Backend restarted
- [ ] Full BLS registration tested successfully!

**🎉 You're ready for automated BLS account creation!**


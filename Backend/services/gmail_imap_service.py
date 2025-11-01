"""
Gmail IMAP Email Service with Custom Domains
Similar to Arezki project - uses custom domains with catch-all forwarding to Gmail
"""

import imaplib
import email
import time
import re
import os
from typing import Optional, Tuple
from loguru import logger
from datetime import datetime

class GmailIMAPService:
    """Email service using custom domains with Gmail IMAP for OTP retrieval"""
    
    def __init__(self):
        # Gmail IMAP credentials (from environment variables)
        self.gmail_address = os.getenv('GMAIL_ADDRESS', '')
        self.gmail_app_password = os.getenv('GMAIL_APP_PASSWORD', '')
        
        # Custom domains (should forward to Gmail via catch-all)
        self.custom_domains = [
            "blsvisa.shop",
            "visabooking.shop", 
            "appointbls.shop"
        ]
        
        # IMAP settings
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        
        # Current domain index for rotation
        self.domain_index = 0
    
    def generate_custom_email(self) -> Tuple[str, str]:
        """
        Generate email using custom domain
        Returns: (email, password)
        """
        try:
            # Rotate through domains
            domain = self.custom_domains[self.domain_index]
            self.domain_index = (self.domain_index + 1) % len(self.custom_domains)
            
            # Generate username (similar to Arezki pattern)
            timestamp = int(time.time() * 1000)
            username = f"user{timestamp}"
            
            email_address = f"{username}@{domain}"
            password = "Qwerty*0"  # Standard password (BLS requirement)
            
            logger.info(f"Generated custom domain email: {email_address}")
            logger.info(f"Domain: {domain}")
            logger.info(f"📧 All emails to this address will forward to: {self.gmail_address}")
            
            return email_address, password
            
        except Exception as e:
            logger.error(f"Error generating custom email: {e}")
            return None, None
    
    async def wait_for_otp(self, email_address: str, timeout_seconds: int = 120) -> Optional[str]:
        """
        Wait for OTP email using Gmail IMAP
        
        Args:
            email_address: The custom domain email that forwards to Gmail
            timeout_seconds: How long to wait for OTP
        
        Returns:
            OTP code or None
        """
        if not self.gmail_address or not self.gmail_app_password:
            logger.error("Gmail credentials not configured!")
            logger.error("Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables")
            return None
        
        logger.info(f"🔍 Waiting for OTP for: {email_address}")
        logger.info(f"📬 Checking Gmail inbox: {self.gmail_address}")
        logger.info(f"⏰ Timeout: {timeout_seconds} seconds")
        
        start_time = time.time()
        check_interval = 3  # Check every 3 seconds
        
        while time.time() - start_time < timeout_seconds:
            try:
                otp = await self._check_gmail_for_otp(email_address)
                if otp:
                    logger.success(f"✅ OTP found: {otp}")
                    return otp
                
                elapsed = int(time.time() - start_time)
                logger.info(f"⏳ No OTP yet... ({elapsed}s / {timeout_seconds}s)")
                time.sleep(check_interval)
                
            except Exception as e:
                logger.warning(f"Error checking Gmail: {e}")
                time.sleep(check_interval)
        
        logger.warning(f"⏰ Timeout: No OTP received after {timeout_seconds} seconds")
        return None
    
    async def _check_gmail_for_otp(self, recipient_email: str) -> Optional[str]:
        """
        Check Gmail inbox for OTP email sent to the custom domain
        """
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.gmail_address, self.gmail_app_password)
            mail.select('inbox')
            
            # Search for recent emails to the custom domain address
            # Gmail keeps the original "To" header even after forwarding
            search_criteria = f'(TO "{recipient_email}" SUBJECT "OTP" UNSEEN)'
            
            # Also try searching by FROM (BLS sender)
            alternative_search = f'(FROM "algeria.blsspainglobal.com" UNSEEN)'
            
            status, messages = mail.search(None, search_criteria)
            
            if status != 'OK' or not messages[0]:
                # Try alternative search
                status, messages = mail.search(None, alternative_search)
            
            if status == 'OK' and messages[0]:
                # Get the latest email
                email_ids = messages[0].split()
                if email_ids:
                    latest_email_id = email_ids[-1]
                    
                    # Fetch the email
                    status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
                    
                    if status == 'OK':
                        # Parse email
                        raw_email = msg_data[0][1]
                        email_message = email.message_from_bytes(raw_email)
                        
                        # Extract email body
                        body = self._get_email_body(email_message)
                        
                        # Extract OTP
                        otp = self._extract_otp_from_text(body)
                        
                        if otp:
                            # Mark as read
                            mail.store(latest_email_id, '+FLAGS', '\\Seen')
                            mail.close()
                            mail.logout()
                            return otp
            
            mail.close()
            mail.logout()
            return None
            
        except Exception as e:
            logger.error(f"Gmail IMAP error: {e}")
            return None
    
    def _get_email_body(self, email_message) -> str:
        """Extract text body from email message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode()
                    except:
                        pass
                elif content_type == "text/html":
                    try:
                        body += part.get_payload(decode=True).decode()
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                pass
        
        return body
    
    def _extract_otp_from_text(self, text: str) -> Optional[str]:
        """Extract OTP code from email text"""
        if not text:
            return None
        
        # OTP patterns (from most specific to least)
        patterns = [
            r'OTP[:\s]+(\d{4,6})',
            r'code[:\s]+(\d{4,6})',
            r'verification code[:\s]+(\d{4,6})',
            r'One Time Password[:\s]+(\d{4,6})',
            r'\b(\d{6})\b',  # 6-digit number
            r'\b(\d{5})\b',  # 5-digit number
            r'\b(\d{4})\b',  # 4-digit number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                otp = match.group(1)
                logger.info(f"OTP extracted using pattern: {pattern}")
                return otp
        
        return None
    
    def get_config_status(self) -> dict:
        """Check configuration status"""
        return {
            "gmail_configured": bool(self.gmail_address and self.gmail_app_password),
            "gmail_address": self.gmail_address or "Not configured",
            "domains": self.custom_domains,
            "imap_server": f"{self.imap_server}:{self.imap_port}"
        }


# Global instance
gmail_imap_service = GmailIMAPService()


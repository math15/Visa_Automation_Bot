"""
REAL Email Service for BLS Account Creation
Real temporary email generation and OTP retrieval using multiple services
"""

import asyncio
import aiohttp
import json
import re
import random
import time
import os
from typing import Optional, List, Dict, Tuple
from loguru import logger
from datetime import datetime, timedelta


class EmailMessage:
    def __init__(self, id: int, from_email: str, subject: str, date: str):
        self.id = id
        self.from_email = from_email
        self.subject = subject
        self.date = date


class EmailContent:
    def __init__(self, id: int, from_email: str, subject: str, body: str, text_body: str):
        self.id = id
        self.from_email = from_email
        self.subject = subject
        self.body = body
        self.text_body = text_body


class RealEmailService:
    """REAL service for generating temporary emails and retrieving OTPs"""
    
    def __init__(self):
        # Get Temp-Mail.io API key from environment (premium service)
        self.temp_mail_io_api_key = os.getenv('TEMP_MAIL_IO_API_KEY', '')
        
        # Gmail IMAP credentials for custom domains
        self.gmail_address = os.getenv('GMAIL_ADDRESS', '')
        self.gmail_app_password = os.getenv('GMAIL_APP_PASSWORD', '')
        
        # Multiple real temporary email services
        # Supported email services (in priority order)
        # NOTE: 1secmail is blocked in some regions (403), so we prioritize others
        self.email_services = [
            # Custom domains with Gmail IMAP - MOST RELIABLE (like Arezki project)
            {
                "name": "gmail_imap",
                "base_url": "imap.gmail.com",
                "domains": ["blsvisa.shop", "visabooking.shop", "appointbls.shop"],
                "method": "gmail_imap",
                "requires_gmail": True
            },
            # Mail.tm - FREE, reliable, no API key needed! (May be blocked by BLS)
            {
                "name": "mailtm",
                "base_url": "https://api.mail.tm",
                "domains": [],  # Will be fetched dynamically
                "method": "mailtm",
                "auth_type": "jwt"  # Uses JWT Bearer token
            },
            # Premium service - most reliable (requires API key)
            {
                "name": "tempmail_io",
                "base_url": "https://api.temp-mail.io/v1/",
                "domains": ["temp-mail.io"],
                "method": "tempmail_io",
                "requires_api_key": True
            },
            {
                "name": "tempmail",
                "base_url": "https://api.tempmail.org/v1/",
                "domains": ["tempmail.org", "tempmail.net"],
                "method": "tempmail"
            },
            {
                "name": "guerrillamail",
                "base_url": "https://www.guerrillamail.com/ajax.php",
                "domains": ["guerrillamail.com", "guerrillamail.de", "guerrillamail.net"],
                "method": "guerrillamail"
            },
            {
                "name": "1secmail",
                "base_url": "https://www.1secmail.com/api/v1/",
                "domains": ["1secmail.com", "1secmail.org", "1secmail.net"],
                "method": "1secmail"
            }
        ]
        
        # Store Mail.tm credentials for the session
        self.mailtm_token = None
        self.mailtm_email = None
        self.mailtm_password = None
        
        # Store custom domain email for IMAP retrieval
        self.custom_domain_email = None
        self.custom_domain_password = None
        self.domain_index = 0  # For rotating domains
        
        # Tesla 2.0 compatible domains (for fallback)
        self.tesla_domains = [
            "ambisens.site", 
            "ibizamails.info", 
            "ayroutod.shop", 
            "easygmail.shop", 
            "liveauto.live"
        ]
        
    async def generate_real_email(self) -> Tuple[str, str]:
        """Generate a REAL temporary email that can receive OTPs"""
        try:
            logger.info("Generating REAL temporary email")
            
            # Try each service until one works
            for service in self.email_services:
                try:
                    email = await self._generate_email_from_service(service)
                    if email:
                        logger.info(f"Generated REAL email using {service['name']}: {email}")
                        return email, service['name']
                except Exception as e:
                    logger.warning(f"Failed to generate email from {service['name']}: {e}")
                    continue
            
            # Fallback to Tesla 2.0 pattern (but with real service)
            logger.warning("All services failed, using fallback")
            return await self._generate_fallback_email()
            
        except Exception as e:
            logger.error(f"Failed to generate real email: {e}")
            return await self._generate_fallback_email()
    
    async def _generate_email_from_service(self, service: Dict[str, str]) -> Optional[str]:
        """Generate email from specific service"""
        try:
            # Skip services that require API key if not configured
            if service.get("requires_api_key") and not self.temp_mail_io_api_key:
                logger.warning(f"Skipping {service['name']} - API key not configured")
                return None
            
            # Skip Gmail IMAP if credentials not configured
            if service.get("requires_gmail") and (not self.gmail_address or not self.gmail_app_password):
                logger.warning(f"Skipping {service['name']} - Gmail credentials not configured")
                logger.info(f"💡 Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables")
                return None
            
            if service["method"] == "gmail_imap":
                return await self._generate_gmail_imap_email(service)
            elif service["method"] == "mailtm":
                return await self._generate_mailtm_email(service)
            elif service["method"] == "tempmail_io":
                return await self._generate_tempmail_io_email(service)
            elif service["method"] == "1secmail":
                return await self._generate_1secmail_email(service)
            elif service["method"] == "tempmail":
                return await self._generate_tempmail_email(service)
            elif service["method"] == "guerrillamail":
                return await self._generate_guerrillamail_email(service)
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating email from {service['name']}: {e}")
            return None
    
    async def _generate_gmail_imap_email(self, service: Dict[str, str]) -> Optional[str]:
        """Generate email using custom domain with Gmail IMAP (like Arezki)"""
        try:
            # Rotate through custom domains
            domain = service["domains"][self.domain_index]
            self.domain_index = (self.domain_index + 1) % len(service["domains"])
            
            # Generate username (timestamp-based like Arezki)
            timestamp = int(time.time() * 1000)
            username = f"user{timestamp}"
            
            email_address = f"{username}@{domain}"
            password = "Qwerty*0"  # Standard password
            
            # Store for later OTP retrieval
            self.custom_domain_email = email_address
            self.custom_domain_password = password
            
            logger.info(f"✅ Generated custom domain email: {email_address}")
            logger.info(f"🌐 Domain: {domain}")
            logger.info(f"📧 Forwards to Gmail: {self.gmail_address}")
            logger.info(f"📬 OTP will be retrieved via IMAP")
            
            return email_address
            
        except Exception as e:
            logger.error(f"Error generating Gmail IMAP email: {e}")
            return None
    
    async def _generate_mailtm_email(self, service: Dict[str, str]) -> Optional[str]:
        """Generate email using Mail.tm FREE service (no API key needed!)"""
        try:
            async with aiohttp.ClientSession() as session:
                # Step 1: Get available domains
                domains_url = f"{service['base_url']}/domains"
                async with session.get(domains_url) as response:
                    if response.status != 200:
                        logger.error(f"Mail.tm domains fetch failed: {response.status}")
                        return None
                    
                    domains_data = await response.json()
                    domains = domains_data.get('hydra:member', [])
                    if not domains:
                        logger.error("No Mail.tm domains available")
                        return None
                    
                    # Get first active domain
                    domain = None
                    for d in domains:
                        if d.get('isActive') and not d.get('isPrivate'):
                            domain = d.get('domain')
                            break
                    
                    if not domain:
                        logger.error("No active Mail.tm domains found")
                        return None
                
                # Step 2: Create account
                timestamp = int(time.time() * 1000)
                username = f"harrouche{timestamp}"
                email = f"{username}@{domain}"
                password = f"Pass{timestamp}!Bls"  # Strong password
                
                account_url = f"{service['base_url']}/accounts"
                account_data = {
                    "address": email,
                    "password": password
                }
                
                async with session.post(account_url, json=account_data) as response:
                    if response.status not in [200, 201]:
                        logger.error(f"Mail.tm account creation failed: {response.status}")
                        text = await response.text()
                        logger.error(f"Response: {text[:200]}")
                        return None
                    
                    account_info = await response.json()
                    logger.info(f"Mail.tm account created: {email}")
                
                # Step 3: Get JWT token
                token_url = f"{service['base_url']}/token"
                token_data = {
                    "address": email,
                    "password": password
                }
                
                async with session.post(token_url, json=token_data) as response:
                    if response.status != 200:
                        logger.error(f"Mail.tm token fetch failed: {response.status}")
                        return None
                    
                    token_info = await response.json()
                    token = token_info.get('token')
                    
                    if not token:
                        logger.error("No token received from Mail.tm")
                        return None
                    
                    # Store credentials for later OTP retrieval
                    self.mailtm_email = email
                    self.mailtm_password = password
                    self.mailtm_token = token
                    
                    logger.info(f"Mail.tm JWT token obtained")
                    logger.info(f"Email will be valid for 24 hours")
                    
                    return email
            
        except Exception as e:
            logger.error(f"Error generating Mail.tm email: {e}")
            return None
    
    async def _generate_tempmail_io_email(self, service: Dict[str, str]) -> Optional[str]:
        """Generate email using Temp-Mail.io premium API (requires API key)"""
        try:
            headers = {
                "X-API-Key": self.temp_mail_io_api_key,
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                # Create new email via Temp-Mail.io API
                url = f"{service['base_url']}emails"
                async with session.post(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        email = data.get('email')
                        if email:
                            logger.info(f"Temp-Mail.io email created: {email}")
                            logger.info(f"TTL: {data.get('ttl', 'unknown')} seconds")
                            return email
                    else:
                        logger.error(f"Temp-Mail.io API error: {response.status}")
                        text = await response.text()
                        logger.error(f"Response: {text[:200]}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating Temp-Mail.io email: {e}")
            return None
    
    async def _generate_1secmail_email(self, service: Dict[str, str]) -> Optional[str]:
        """Generate email using 1secmail service"""
        try:
            # Generate username with Tesla 2.0 pattern
            timestamp = int(time.time() * 1000)
            username = f"harrouche{timestamp}"
            
            # Choose random domain
            domain = random.choice(service["domains"])
            email = f"{username}@{domain}"
            
            # Verify email is available
            async with aiohttp.ClientSession() as session:
                url = f"{service['base_url']}?action=getMessages&login={username}&domain={domain}"
                async with session.get(url) as response:
                    if response.status == 200:
                        logger.info(f"1secmail email verified: {email}")
                        return email
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating 1secmail email: {e}")
            return None
    
    async def _generate_tempmail_email(self, service: Dict[str, str]) -> Optional[str]:
        """Generate email using tempmail service"""
        try:
            # Generate username with Tesla 2.0 pattern
            timestamp = int(time.time() * 1000)
            username = f"harrouche{timestamp}"
            
            # Choose random domain
            domain = random.choice(service["domains"])
            email = f"{username}@{domain}"
            
            # Verify email is available
            async with aiohttp.ClientSession() as session:
                url = f"{service['base_url']}mailbox/{email}"
                async with session.get(url) as response:
                    if response.status == 200:
                        logger.info(f"Tempmail email verified: {email}")
                        return email
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating tempmail email: {e}")
            return None
    
    async def _generate_guerrillamail_email(self, service: Dict[str, str]) -> Optional[str]:
        """Generate email using guerrillamail service"""
        try:
            # Generate username with Tesla 2.0 pattern
            timestamp = int(time.time() * 1000)
            username = f"harrouche{timestamp}"
            
            # Choose random domain
            domain = random.choice(service["domains"])
            email = f"{username}@{domain}"
            
            # Verify email is available
            async with aiohttp.ClientSession() as session:
                url = f"{service['base_url']}?f=get_email_address&lang=en&domain={domain}&ip=127.0.0.1&agent=Mozilla_foo_bar"
                async with session.get(url) as response:
                    if response.status == 200:
                        logger.info(f"Guerrillamail email verified: {email}")
                        return email
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating guerrillamail email: {e}")
            return None
    
    async def get_otp_from_email(self, email: str, service_name: str = None) -> Optional[str]:
        """Retrieve OTP from email using appropriate service"""
        try:
            logger.info(f"Retrieving OTP from email: {email}")
            
            # Determine service from email domain
            if not service_name:
                service_name = self._detect_service_from_email(email)
            
            if service_name == "gmail_imap":
                return await self._get_otp_from_gmail_imap(email)
            elif service_name == "mailtm":
                return await self._get_otp_from_mailtm(email)
            elif service_name == "tempmail_io":
                return await self._get_otp_from_tempmail_io(email)
            elif service_name == "1secmail":
                return await self._get_otp_from_1secmail(email)
            elif service_name == "tempmail":
                return await self._get_otp_from_tempmail(email)
            elif service_name == "guerrillamail":
                return await self._get_otp_from_guerrillamail(email)
            
            # Try all services as fallback
            for service in self.email_services:
                try:
                    if service['name'] == '1secmail':
                        otp = await self._get_otp_from_1secmail(email)
                    elif service['name'] == 'tempmail':
                        otp = await self._get_otp_from_tempmail(email)
                    elif service['name'] == 'guerrillamail':
                        otp = await self._get_otp_from_guerrillamail(email)
                    else:
                        continue
                    
                    if otp:
                        return otp
                except Exception as e:
                    logger.warning(f"Failed to get OTP from {service['name']}: {e}")
                    continue
            
            logger.warning(f"No OTP found in email: {email}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve OTP from email {email}: {e}")
            return None
    
    async def _get_otp_from_gmail_imap(self, email: str) -> Optional[str]:
        """Get OTP from Gmail via IMAP (for custom domain emails)"""
        try:
            import imaplib
            import email as email_lib
            
            if not self.gmail_address or not self.gmail_app_password:
                logger.error("Gmail credentials not available for OTP retrieval")
                return None
            
            logger.info(f"📬 Connecting to Gmail IMAP for: {email}")
            
            # Connect to Gmail
            mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            mail.login(self.gmail_address, self.gmail_app_password)
            mail.select('inbox')
            
            # Search for emails to this custom domain address
            search_criteria = f'(TO "{email}" UNSEEN)'
            status, messages = mail.search(None, search_criteria)
            
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                if email_ids:
                    # Get latest email
                    latest_id = email_ids[-1]
                    status, msg_data = mail.fetch(latest_id, '(RFC822)')
                    
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        email_message = email_lib.message_from_bytes(raw_email)
                        
                        # Get email body
                        body = ""
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    try:
                                        body += part.get_payload(decode=True).decode()
                                    except:
                                        pass
                        else:
                            try:
                                body = email_message.get_payload(decode=True).decode()
                            except:
                                pass
                        
                        # Extract OTP
                        otp = self._extract_otp_from_text(body)
                        
                        if otp:
                            logger.info(f"✅ OTP retrieved from Gmail IMAP: {otp}")
                            # Mark as read
                            mail.store(latest_id, '+FLAGS', '\\Seen')
                            mail.close()
                            mail.logout()
                            return otp
            
            mail.close()
            mail.logout()
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving OTP from Gmail IMAP: {e}")
            return None
    
    async def _get_otp_from_mailtm(self, email: str) -> Optional[str]:
        """Get OTP from Mail.tm FREE service"""
        try:
            if not self.mailtm_token:
                logger.error("No Mail.tm token available. Email must be generated first.")
                return None
            
            headers = {
                "Authorization": f"Bearer {self.mailtm_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                # Get messages
                messages_url = "https://api.mail.tm/messages"
                async with session.get(messages_url, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Mail.tm messages fetch failed: {response.status}")
                        return None
                    
                    data = await response.json()
                    messages = data.get('hydra:member', [])
                    
                    if not messages or len(messages) == 0:
                        logger.info("No messages found in Mail.tm inbox yet")
                        return None
                    
                    # Get the latest message
                    latest_message = max(messages, key=lambda x: x.get('createdAt', ''))
                    message_id = latest_message.get('id')
                    
                    if not message_id:
                        logger.error("No message ID found")
                        return None
                    
                    # Get full message content
                    message_url = f"https://api.mail.tm/messages/{message_id}"
                    async with session.get(message_url, headers=headers) as msg_response:
                        if msg_response.status != 200:
                            logger.error(f"Mail.tm message fetch failed: {msg_response.status}")
                            return None
                        
                        msg_data = await msg_response.json()
                        
                        # Extract OTP from text or HTML body
                        body = msg_data.get('text', '') or msg_data.get('html', [''])[0] if isinstance(msg_data.get('html'), list) else msg_data.get('html', '')
                        otp = self._extract_otp_from_text(body)
                        
                        if otp:
                            logger.info(f"OTP retrieved from Mail.tm: {otp}")
                            # Mark message as read
                            try:
                                patch_url = f"https://api.mail.tm/messages/{message_id}"
                                patch_data = {"seen": True}
                                await session.patch(patch_url, headers=headers, json=patch_data)
                            except:
                                pass  # Don't fail if marking as read fails
                            
                            return otp
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting OTP from Mail.tm: {e}")
            return None
    
    async def _get_otp_from_tempmail_io(self, email: str) -> Optional[str]:
        """Get OTP from Temp-Mail.io premium API"""
        try:
            headers = {
                "X-API-Key": self.temp_mail_io_api_key,
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                # Get messages for email
                url = f"https://api.temp-mail.io/v1/emails/{email}/messages"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        messages = data.get('messages', [])
                        
                        if messages and len(messages) > 0:
                            # Get the latest message
                            latest_message = max(messages, key=lambda x: x.get('created_at', ''))
                            message_id = latest_message.get('id')
                            
                            # Get full message content
                            if message_id:
                                msg_url = f"https://api.temp-mail.io/v1/messages/{message_id}"
                                async with session.get(msg_url, headers=headers) as msg_response:
                                    if msg_response.status == 200:
                                        msg_data = await msg_response.json()
                                        
                                        # Extract OTP from message body
                                        body = msg_data.get('body_text', '') or msg_data.get('body_html', '')
                                        otp = self._extract_otp_from_text(body)
                                        
                                        if otp:
                                            logger.info(f"OTP retrieved from Temp-Mail.io: {otp}")
                                            return otp
                    else:
                        logger.error(f"Temp-Mail.io API error: {response.status}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting OTP from Temp-Mail.io: {e}")
            return None
    
    async def _get_otp_from_1secmail(self, email: str) -> Optional[str]:
        """Get OTP from 1secmail service"""
        try:
            username, domain = email.split('@')
            
            async with aiohttp.ClientSession() as session:
                # Get inbox messages
                url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
                async with session.get(url) as response:
                    if response.status == 200:
                        messages_data = await response.json()
                        
                        if messages_data and len(messages_data) > 0:
                            # Get the latest message
                            latest_message = max(messages_data, key=lambda x: x['date'])
                            
                            # Get message content
                            content_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={latest_message['id']}"
                            async with session.get(content_url) as response:
                                if response.status == 200:
                                    content_data = await response.json()
                                    
                                    # Extract OTP from message body
                                    body = content_data.get('body', '') or content_data.get('textBody', '')
                                    otp = self._extract_otp_from_text(body)
                                    
                                    if otp:
                                        logger.info(f"OTP retrieved from 1secmail: {otp}")
                                        return otp
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting OTP from 1secmail: {e}")
            return None
    
    async def _get_otp_from_tempmail(self, email: str) -> Optional[str]:
        """Get OTP from tempmail service"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get inbox messages
                url = f"https://api.tempmail.org/v1/mailbox/{email}"
                async with session.get(url) as response:
                    if response.status == 200:
                        messages_data = await response.json()
                        
                        if messages_data and len(messages_data) > 0:
                            # Get the latest message
                            latest_message = max(messages_data, key=lambda x: x['date'])
                            
                            # Extract OTP from message body
                            body = latest_message.get('body', '') or latest_message.get('text', '')
                            otp = self._extract_otp_from_text(body)
                            
                            if otp:
                                logger.info(f"OTP retrieved from tempmail: {otp}")
                                return otp
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting OTP from tempmail: {e}")
            return None
    
    async def _get_otp_from_guerrillamail(self, email: str) -> Optional[str]:
        """Get OTP from guerrillamail service"""
        try:
            username, domain = email.split('@')
            
            async with aiohttp.ClientSession() as session:
                # Get inbox messages
                url = f"https://www.guerrillamail.com/ajax.php?f=get_email_list&ip=127.0.0.1&agent=Mozilla_foo_bar&sid_token={username}"
                async with session.get(url) as response:
                    if response.status == 200:
                        messages_data = await response.json()
                        
                        if messages_data and len(messages_data) > 0:
                            # Get the latest message
                            latest_message = max(messages_data, key=lambda x: x['mail_date'])
                            
                            # Get message content
                            content_url = f"https://www.guerrillamail.com/ajax.php?f=fetch_email&ip=127.0.0.1&agent=Mozilla_foo_bar&sid_token={username}&email_id={latest_message['mail_id']}"
                            async with session.get(content_url) as response:
                                if response.status == 200:
                                    content_data = await response.json()
                                    
                                    # Extract OTP from message body
                                    body = content_data.get('mail_body', '')
                                    otp = self._extract_otp_from_text(body)
                                    
                                    if otp:
                                        logger.info(f"OTP retrieved from guerrillamail: {otp}")
                                        return otp
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting OTP from guerrillamail: {e}")
            return None
    
    async def wait_for_otp(self, email: str, service_name: str = None, timeout_seconds: int = 120) -> Optional[str]:
        """Wait for OTP to arrive in email"""
        try:
            logger.info(f"Waiting for OTP in email: {email} (timeout: {timeout_seconds}s)")
            
            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < timeout_seconds:
                otp = await self.get_otp_from_email(email, service_name)
                if otp:
                    return otp
                
                await asyncio.sleep(3)  # Wait 3 seconds before checking again
            
            logger.warning(f"Timeout waiting for OTP in email: {email}")
            return None
            
        except Exception as e:
            logger.error(f"Error waiting for OTP: {e}")
            return None
    
    def _detect_service_from_email(self, email: str) -> str:
        """Detect service from email domain"""
        domain = email.split('@')[1]
        
        for service in self.email_services:
            if domain in service["domains"]:
                return service["name"]
        
        return "1secmail"  # Default fallback
    
    def _extract_otp_from_text(self, text: str) -> Optional[str]:
        """Extract OTP from email text using regex patterns"""
        if not text:
            return None
        
        # Common OTP patterns (enhanced for BLS format)
        patterns = [
            # BLS specific patterns
            r'email verification code is as mentioned below\s*(\d{6})',  # BLS format
            r'verification code is as mentioned below\s*(\d{6})',      # BLS format variant
            r'email verification code.*?(\d{6})',                       # BLS flexible
            r'verification code.*?(\d{6})',                            # BLS flexible
            
            # Standard patterns
            r'\b\d{6}\b',           # 6-digit OTP (most common)
            r'\b\d{4}\b',           # 4-digit OTP
            r'\b\d{8}\b',           # 8-digit OTP
            
            # Text-based patterns
            r'verification code[:\s]*(\d+)',  # "verification code: 123456"
            r'OTP[:\s]*(\d+)',     # "OTP: 123456"
            r'code[:\s]*(\d+)',    # "code: 123456"
            r'pin[:\s]*(\d+)',     # "pin: 123456"
            r'your code is[:\s]*(\d+)',  # "your code is: 123456"
            r'enter code[:\s]*(\d+)',    # "enter code: 123456"
            
            # BLS International specific
            r'BLS International.*?(\d{6})',  # BLS in email content
            r'blsinternational\.com.*?(\d{6})',  # BLS domain reference
        ]
        
        # Try each pattern
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                otp = match.group(1) if match.groups() else match.group(0)
                # Validate OTP length (4-8 digits)
                if len(otp) >= 4 and len(otp) <= 8 and otp.isdigit():
                    logger.info(f"OTP extracted using pattern '{pattern}': {otp}")
                    return otp
        
        # Fallback: Look for standalone 6-digit numbers (BLS format)
        standalone_pattern = r'^\s*(\d{6})\s*$'
        lines = text.split('\n')
        for line in lines:
            match = re.match(standalone_pattern, line.strip())
            if match:
                otp = match.group(1)
                logger.info(f"OTP extracted as standalone number: {otp}")
                return otp
        
        return None
    
    async def _generate_fallback_email(self) -> Tuple[str, str]:
        """Generate fallback email using accessible service"""
        try:
            # Use Tesla 2.0 pattern with tempmail.org (NOT 1secmail - it's blocked!)
            timestamp = int(time.time() * 1000)
            username = f"harrouche{timestamp}"
            domain = "tempmail.org"  # Changed from 1secmail.com
            email = f"{username}@{domain}"
            
            logger.info(f"Generated fallback email: {email}")
            return email, "tempmail"
            
        except Exception as e:
            logger.error(f"Failed to generate fallback email: {e}")
            # Last resort - use tempmail instead of 1secmail
            timestamp = int(time.time())
            return f"harrouche{timestamp}@tempmail.org", "tempmail"


# Global instance
real_email_service = RealEmailService()
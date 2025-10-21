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
        # Multiple real temporary email services
        self.email_services = [
            {
                "name": "1secmail",
                "base_url": "https://www.1secmail.com/api/v1/",
                "domains": ["1secmail.com", "1secmail.org", "1secmail.net"],
                "method": "1secmail"
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
            }
        ]
        
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
            if service["method"] == "1secmail":
                return await self._generate_1secmail_email(service)
            elif service["method"] == "tempmail":
                return await self._generate_tempmail_email(service)
            elif service["method"] == "guerrillamail":
                return await self._generate_guerrillamail_email(service)
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating email from {service['name']}: {e}")
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
            
            if service_name == "1secmail":
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
        """Generate fallback email"""
        try:
            # Use Tesla 2.0 pattern with 1secmail
            timestamp = int(time.time() * 1000)
            username = f"harrouche{timestamp}"
            domain = "1secmail.com"
            email = f"{username}@{domain}"
            
            logger.info(f"Generated fallback email: {email}")
            return email, "1secmail"
            
        except Exception as e:
            logger.error(f"Failed to generate fallback email: {e}")
            # Last resort
            timestamp = int(time.time())
            return f"harrouche{timestamp}@1secmail.com", "1secmail"


# Global instance
real_email_service = RealEmailService()
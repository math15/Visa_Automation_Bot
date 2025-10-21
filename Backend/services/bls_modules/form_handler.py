"""
Form Handler Module for BLS Account Creation
Handles form data extraction, analysis, and submission
"""

import re
from typing import Dict, Any, Optional
from loguru import logger


class FormHandler:
    """Handles form data extraction and analysis for BLS website"""
    
    def __init__(self):
        pass
    
    async def extract_form_data(self, page_content: str) -> Dict[str, Any]:
        """Extract form data from registration page"""
        try:
            logger.info(f"📄 Extracting form data from content length: {len(page_content)}")
            logger.info(f"📄 Content preview: {page_content[:500]}...")
            
            # Analyze form structure first
            await self._analyze_form_structure(page_content)
            
            # Extract hidden fields, tokens, etc.
            form_data = {
                "__RequestVerificationToken": self._extract_token(page_content, "__RequestVerificationToken"),
                "Mode": "Register",
                "CaptchaParam": self._extract_token(page_content, "CaptchaParam"),
                "CaptchaData": self._extract_token(page_content, "CaptchaData"),
                "CaptchaId": self._extract_token(page_content, "CaptchaId")
            }
            
            logger.info(f"📋 Extracted form data: {form_data}")
            logger.info("Form data extracted successfully")
            return form_data
            
        except Exception as e:
            logger.error(f"Error extracting form data: {e}")
            return {}
    
    async def _analyze_form_structure(self, page_content: str):
        """Analyze and log the form structure found on the page"""
        try:
            logger.info("🔍 Analyzing form structure...")
            
            # Find all forms
            forms = re.findall(r'<form[^>]*>(.*?)</form>', page_content, re.DOTALL | re.IGNORECASE)
            logger.info(f"📝 Found {len(forms)} form(s) on the page")
            
            for i, form in enumerate(forms):
                logger.info(f"📝 Form {i+1} analysis:")
                
                # Find all input fields
                inputs = re.findall(r'<input[^>]*>', form, re.IGNORECASE)
                logger.info(f"   🔹 {len(inputs)} input fields found")
                
                for input_tag in inputs:
                    # Extract input attributes
                    name_match = re.search(r'name=["\']([^"\']*)["\']', input_tag)
                    type_match = re.search(r'type=["\']([^"\']*)["\']', input_tag)
                    id_match = re.search(r'id=["\']([^"\']*)["\']', input_tag)
                    value_match = re.search(r'value=["\']([^"\']*)["\']', input_tag)
                    
                    name = name_match.group(1) if name_match else "no-name"
                    input_type = type_match.group(1) if type_match else "text"
                    input_id = id_match.group(1) if id_match else "no-id"
                    value = value_match.group(1) if value_match else "no-value"
                    
                    logger.info(f"      📋 {name} (type: {input_type}, id: {input_id}, value: {value[:50]}...)")
                
                # Find all select fields
                selects = re.findall(r'<select[^>]*>(.*?)</select>', form, re.DOTALL | re.IGNORECASE)
                logger.info(f"   🔹 {len(selects)} select fields found")
                
                # Find all textarea fields
                textareas = re.findall(r'<textarea[^>]*>(.*?)</textarea>', form, re.DOTALL | re.IGNORECASE)
                logger.info(f"   🔹 {len(textareas)} textarea fields found")
            
            # Look for specific BLS form patterns
            logger.info("🎯 Checking for specific BLS form patterns:")
            
            # Check for FirstName field
            first_name_patterns = [
                r'name=["\']FirstName["\']',
                r'name=["\']first_name["\']',
                r'name=["\']firstName["\']',
                r'id=["\']FirstName["\']',
                r'id=["\']first_name["\']'
            ]
            
            for pattern in first_name_patterns:
                if re.search(pattern, page_content, re.IGNORECASE):
                    logger.info(f"   ✅ Found FirstName field with pattern: {pattern}")
                    break
            else:
                logger.warning("   ❌ FirstName field not found")
            
            # Check for LastName field
            last_name_patterns = [
                r'name=["\']LastName["\']',
                r'name=["\']last_name["\']',
                r'name=["\']lastName["\']',
                r'id=["\']LastName["\']',
                r'id=["\']last_name["\']'
            ]
            
            for pattern in last_name_patterns:
                if re.search(pattern, page_content, re.IGNORECASE):
                    logger.info(f"   ✅ Found LastName field with pattern: {pattern}")
                    break
            else:
                logger.warning("   ❌ LastName field not found")
            
            # Check for Email field
            email_patterns = [
                r'name=["\']Email["\']',
                r'name=["\']email["\']',
                r'type=["\']email["\']',
                r'id=["\']Email["\']',
                r'id=["\']email["\']'
            ]
            
            for pattern in email_patterns:
                if re.search(pattern, page_content, re.IGNORECASE):
                    logger.info(f"   ✅ Found Email field with pattern: {pattern}")
                    break
            else:
                logger.warning("   ❌ Email field not found")
            
            # Check for Password field (BLS doesn't use passwords)
            password_patterns = [
                r'name=["\']Password["\']',
                r'name=["\']password["\']',
                r'type=["\']password["\']',
                r'id=["\']Password["\']',
                r'id=["\']password["\']'
            ]
            
            password_found = False
            for pattern in password_patterns:
                if re.search(pattern, page_content, re.IGNORECASE):
                    logger.info(f"   ✅ Found Password field with pattern: {pattern}")
                    password_found = True
                    break
            
            if not password_found:
                logger.info("   ℹ️ Password field not found (BLS doesn't use passwords)")
            
            # Check for dropdown fields (select elements)
            logger.info("   🔍 Checking for dropdown/select fields:")
            
            # Passport Issue Country dropdown
            passport_issue_country_patterns = [
                r'name=["\']PassportIssueCountry["\']',
                r'id=["\']PassportIssueCountry["\']',
                r'Passport Issue Country'
            ]
            
            for pattern in passport_issue_country_patterns:
                if re.search(pattern, page_content, re.IGNORECASE):
                    logger.info(f"   ✅ Found Passport Issue Country dropdown with pattern: {pattern}")
                    break
            else:
                logger.warning("   ❌ Passport Issue Country dropdown not found")
            
            # Passport Type dropdown
            passport_type_patterns = [
                r'name=["\']PassportType["\']',
                r'id=["\']PassportType["\']',
                r'Passport Type'
            ]
            
            for pattern in passport_type_patterns:
                if re.search(pattern, page_content, re.IGNORECASE):
                    logger.info(f"   ✅ Found Passport Type dropdown with pattern: {pattern}")
                    break
            else:
                logger.warning("   ❌ Passport Type dropdown not found")
            
            # Country Of Residence dropdown
            country_of_residence_patterns = [
                r'name=["\']CountryOfResidence["\']',
                r'id=["\']CountryOfResidence["\']',
                r'Country Of Residence'
            ]
            
            for pattern in country_of_residence_patterns:
                if re.search(pattern, page_content, re.IGNORECASE):
                    logger.info(f"   ✅ Found Country Of Residence dropdown with pattern: {pattern}")
                    break
            else:
                logger.warning("   ❌ Country Of Residence dropdown not found")
            
            # Check for CaptchaId field
            captcha_patterns = [
                r'name=["\']CaptchaId["\']',
                r'name=["\']captcha_id["\']',
                r'id=["\']CaptchaId["\']',
                r'id=["\']captcha_id["\']'
            ]
            
            for pattern in captcha_patterns:
                if re.search(pattern, page_content, re.IGNORECASE):
                    logger.info(f"   ✅ Found CaptchaId field with pattern: {pattern}")
                    break
            else:
                logger.warning("   ❌ CaptchaId field not found")
            
            # Check for RequestVerificationToken
            token_patterns = [
                r'name=["\']__RequestVerificationToken["\']',
                r'name=["\']RequestVerificationToken["\']',
                r'id=["\']__RequestVerificationToken["\']'
            ]
            
            for pattern in token_patterns:
                if re.search(pattern, page_content, re.IGNORECASE):
                    logger.info(f"   ✅ Found RequestVerificationToken field with pattern: {pattern}")
                    break
            else:
                logger.warning("   ❌ RequestVerificationToken field not found")
            
            # Check for form action URL
            action_match = re.search(r'<form[^>]*action=["\']([^"\']*)["\']', page_content, re.IGNORECASE)
            if action_match:
                logger.info(f"   ✅ Form action URL: {action_match.group(1)}")
            else:
                logger.warning("   ❌ Form action URL not found")
            
            # Check for form method
            method_match = re.search(r'<form[^>]*method=["\']([^"\']*)["\']', page_content, re.IGNORECASE)
            if method_match:
                logger.info(f"   ✅ Form method: {method_match.group(1)}")
            else:
                logger.info("   ℹ️ Form method not specified (defaults to GET)")
            
            logger.info("🔍 Form structure analysis completed")
            
        except Exception as e:
            logger.error(f"Error analyzing form structure: {e}")
    
    def _extract_token(self, content: str, token_name: str) -> str:
        """Extract token from HTML content"""
        # Try multiple patterns for token extraction
        patterns = [
            f'name="{token_name}"[^>]*value="([^"]*)"',
            f'name="{token_name}"[^>]*value=\'([^\']*)\'',
            f'id="{token_name}"[^>]*value="([^"]*)"',
            f'id="{token_name}"[^>]*value=\'([^\']*)\'',
            f'<input[^>]*name="{token_name}"[^>]*value="([^"]*)"',
            f'<input[^>]*name="{token_name}"[^>]*value=\'([^\']*)\'',
            f'{token_name}.*?value="([^"]*)"',
            f'{token_name}.*?value=\'([^\']*)\''
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                token_value = match.group(1)
                logger.info(f"✅ Extracted token '{token_name}' with pattern {i+1}: {token_value[:50]}...")
                return token_value
        
        logger.warning(f"❌ Token '{token_name}' not found with any pattern")
        return ""
    
    async def submit_form(self, form_data: Dict[str, Any], proxy_url: str = None) -> Dict[str, Any]:
        """Submit the BLS registration form"""
        logger.info("📤 Submitting BLS registration form...")
        
        try:
            # This is a placeholder method - implement actual form submission logic here
            # For now, return a success response
            logger.info("✅ Form submission completed (placeholder)")
            return {
                "success": True,
                "message": "Form submitted successfully",
                "account_id": "placeholder_account_id"
            }
            
        except Exception as e:
            logger.error(f"❌ Error submitting form: {e}")
            return {
                "success": False,
                "message": f"Form submission failed: {e}",
                "account_id": None
            }
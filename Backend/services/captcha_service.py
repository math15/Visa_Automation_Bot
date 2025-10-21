"""
Captcha Solving Service for BLS Account Creation
Tesla 2.0 compatible captcha solving using NoCaptcha.io
"""

import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any
from loguru import logger


class CaptchaService:
    """Service for solving captchas using NoCaptcha.io API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "mayas94-9c2063ba-0944-cd88-ab10-9c4325fbb9fd"  # Your actual API key
        self.api_url = "https://api.nocaptchaai.com"
        logger.info(f"🔑 CaptchaService initialized with NoCaptchaAI API: {self.api_url}")
        logger.info(f"🔑 API Key: {self.api_key}")
        
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA v2 challenge"""
        try:
            logger.info(f"Solving reCAPTCHA v2 for site: {site_key}")
            
            # Submit captcha
            task_id = await self._submit_captcha({
                "type": "recaptcha_v2",
                "site_key": site_key,
                "page_url": page_url
            })
            
            if not task_id:
                return None
            
            # Wait for solution
            solution = await self._wait_for_solution(task_id)
            return solution
            
        except Exception as e:
            logger.error(f"Failed to solve reCAPTCHA v2: {e}")
            return None
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCaptcha challenge"""
        try:
            logger.info(f"Solving hCaptcha for site: {site_key}")
            
            # Submit captcha
            task_id = await self._submit_captcha({
                "type": "hcaptcha",
                "site_key": site_key,
                "page_url": page_url
            })
            
            if not task_id:
                return None
            
            # Wait for solution
            solution = await self._wait_for_solution(task_id)
            return solution
            
        except Exception as e:
            logger.error(f"Failed to solve hCaptcha: {e}")
            return None
    
    async def solve_image_captcha(self, image_base64: str) -> Optional[str]:
        """Solve image-based captcha"""
        try:
            logger.info("Solving image captcha")
            
            # Submit captcha
            task_id = await self._submit_captcha({
                "type": "image",
                "image": image_base64
            })
            
            if not task_id:
                return None
            
            # Wait for solution
            solution = await self._wait_for_solution(task_id)
            return solution
            
        except Exception as e:
            logger.error(f"Failed to solve image captcha: {e}")
            return None
    
    async def _submit_captcha(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Submit captcha to captcha solving service"""
        try:
            captcha_type = captcha_data.get("type")
            
            if captcha_type == "bls_captcha":
                # Use BLS OCR CAPTCHA service
                logger.info(f"📡 Submitting BLS captcha to OCR service: {captcha_data}")
                return await self._submit_bls_ocr_captcha(captcha_data)
            else:
                # Use NoCaptcha.io for other types
                logger.info(f"📡 Submitting captcha to NoCaptcha.io: {captcha_data}")
                
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    }
                    
                    async with session.post(
                        f"{self.api_url}/solve",
                        json=captcha_data,
                        headers=headers
                    ) as response:
                        response_text = await response.text()
                        logger.info(f"📡 NoCaptcha.io response: {response.status} - {response_text}")
                        
                        if response.status == 200:
                            result = await response.json()
                            task_id = result.get("task_id")
                            logger.info(f"✅ Captcha submitted successfully, task_id: {task_id}")
                            return task_id
                        else:
                            logger.error(f"❌ Failed to submit captcha: {response.status} - {response_text}")
                            return None
                        
        except Exception as e:
            logger.error(f"Error submitting captcha: {e}")
            return None
    
    async def _submit_bls_ocr_captcha(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Submit BLS captcha to NoCaptchaAI OCR service"""
        try:
            logger.info("🎯 Using NoCaptchaAI BLS OCR CAPTCHA service")
            
            # Extract images from captcha_data
            images = captcha_data.get("images", [])
            if not images:
                logger.error("No images provided for BLS captcha")
                return None
            
            # Prepare request payload according to NoCaptchaAI API
            payload = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ImageToTextTask",
                    "images": images,
                    "numeric": True,  # BLS captchas are usually numeric
                    "module": "bls",  # Use BLS module
                    "case": False,    # Case insensitive
                    "maxLength": 3    # BLS captchas are typically 3 digits
                }
            }
            
            logger.info(f"📡 Submitting BLS captcha to NoCaptchaAI: {len(images)} images")
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json"
                }
                
                async with session.post(
                    f"{self.api_url}/createTask",
                    json=payload,
                    headers=headers
                ) as response:
                    response_text = await response.text()
                    logger.info(f"📡 NoCaptchaAI response: {response.status} - {response_text}")
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("errorId") == 0:
                            task_id = result.get("taskId")
                            logger.info(f"✅ BLS captcha submitted successfully, task_id: {task_id}")
                            
                            # Wait for solution
                            solution = await self._wait_for_nocaptcha_solution(task_id)
                            return solution
                        else:
                            logger.error(f"❌ NoCaptchaAI error: {result.get('errorDescription')}")
                            return None
                    else:
                        logger.error(f"❌ Failed to submit BLS captcha: {response.status} - {response_text}")
                        return None
            
        except Exception as e:
            logger.error(f"Error submitting BLS OCR captcha: {e}")
            return None
    
    
    async def _wait_for_nocaptcha_solution(self, task_id: str, max_wait_time: int = 120) -> Optional[str]:
        """Wait for NoCaptchaAI solution"""
        try:
            logger.info(f"Waiting for NoCaptchaAI solution, task_id: {task_id}")
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "clientKey": self.api_key,
                    "taskId": task_id
                }
                
                start_time = asyncio.get_event_loop().time()
                
                while (asyncio.get_event_loop().time() - start_time) < max_wait_time:
                    async with session.post(
                        f"{self.api_url}/getTaskResult",
                        json=payload,
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            
                            if result.get("errorId") == 0:
                                status = result.get("status")
                                
                                if status == "ready":
                                    solution_data = result.get("solution", {})
                                    text_solutions = solution_data.get("text", [])
                                    
                                    if text_solutions:
                                        # Join all solutions (BLS captcha might have multiple images)
                                        combined_solution = "".join(text_solutions)
                                        logger.info(f"✅ NoCaptchaAI solved successfully: {combined_solution}")
                                        return combined_solution
                                    else:
                                        logger.error("❌ No solution text in response")
                                        return None
                                        
                                elif status == "processing":
                                    logger.info("⏳ NoCaptchaAI still processing...")
                                    await asyncio.sleep(3)  # Wait 3 seconds
                                    continue
                                else:
                                    logger.error(f"❌ NoCaptchaAI failed: {status}")
                                    return None
                            else:
                                logger.error(f"❌ NoCaptchaAI error: {result.get('errorDescription')}")
                                return None
                        else:
                            logger.error(f"❌ Failed to get solution: {response.status}")
                            await asyncio.sleep(3)
                            continue
                
                logger.warning(f"⏰ Timeout waiting for NoCaptchaAI solution: {task_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error waiting for NoCaptchaAI solution: {e}")
            return None
    
    async def solve_bls_images(self, images: list) -> Optional[str]:
        """Solve BLS image-based captcha using NoCaptchaAI API directly"""
        try:
            logger.info(f"Solving BLS image captcha with {len(images)} images using NoCaptchaAI API")
            
            # Prepare base64 images for API
            base64_images = []
            for i, image_data in enumerate(images):
                try:
                    logger.info(f"🔍 Processing image {i+1}/{len(images)}")
                    
                    # Extract base64 data from data URL
                    if isinstance(image_data, str) and image_data.startswith('data:image'):
                        # Remove data URL prefix if present
                        base64_data = image_data.split(',')[1] if ',' in image_data else image_data
                    else:
                        base64_data = image_data
                    
                    # Decode HTML entities in base64 data
                    import html
                    base64_data = html.unescape(base64_data)
                    
                    # Fix base64 padding if needed
                    missing_padding = len(base64_data) % 4
                    if missing_padding:
                        base64_data += '=' * (4 - missing_padding)
                    
                    # Validate base64 data
                    import base64
                    try:
                        decoded = base64.b64decode(base64_data)
                        if len(decoded) > 50:  # Ensure it's a valid image
                            base64_images.append(base64_data)
                            logger.info(f"✅ Image {i+1} validated successfully")
                        else:
                            logger.warning(f"⚠️ Image {i+1} too small, skipping")
                    except Exception as e:
                        logger.warning(f"⚠️ Image {i+1} invalid base64 data: {e}")
                        continue
                        
                except Exception as e:
                    logger.error(f"❌ Error processing image {i+1}: {e}")
                    continue
            
            if not base64_images:
                logger.error("❌ No valid images to process")
                return None
            
            # Limit images to 50 (NoCaptchaAI maximum)
            if len(base64_images) > 50:
                logger.warning(f"⚠️ Too many images ({len(base64_images)}), limiting to 50 for NoCaptchaAI")
                base64_images = base64_images[:50]
            
            # Use NoCaptchaAI API directly
            payload = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ImageToTextTask",
                    "images": base64_images,
                    "module": "common",  # Try common module
                    "case": False,    # Case insensitive
                    "maxLength": 10   # Increase max length
                }
            }
            
            logger.info(f"📡 Submitting {len(base64_images)} images to NoCaptchaAI API")
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json"
                }
                
                async with session.post(
                    f"{self.api_url}/createTask",
                    json=payload,
                    headers=headers
                ) as response:
                    response_text = await response.text()
                    logger.info(f"📡 NoCaptchaAI response: {response.status} - {response_text}")
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("errorId") == 0:
                            task_id = result.get("taskId")
                            status = result.get("status")
                            
                            logger.info(f"✅ BLS captcha submitted successfully, task_id: {task_id}, status: {status}")
                            
                            # Check if solution is ready immediately
                            if status == "ready":
                                solution_data = result.get("solution", {})
                                text_solutions = solution_data.get("text", [])
                                
                                if text_solutions:
                                    # Join all solutions (BLS captcha might have multiple images)
                                    combined_solution = "".join(text_solutions)
                                    logger.info(f"✅ NoCaptchaAI solved immediately: {combined_solution}")
                                    return combined_solution
                                else:
                                    logger.error("❌ No solution text in immediate response")
                                    return None
                            elif task_id:
                                # Wait for solution if task ID is provided
                                solution = await self._wait_for_nocaptcha_solution(task_id)
                                return solution
                            else:
                                logger.error("❌ No task ID and status not ready")
                                return None
                        else:
                            logger.error(f"❌ NoCaptchaAI error: {result.get('errorDescription')}")
                            return None
                    else:
                        logger.error(f"❌ Failed to submit BLS captcha: {response.status} - {response_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error solving BLS image captcha: {e}")
            return None
    
    async def _wait_for_solution(self, task_id: str, max_wait_time: int = 120) -> Optional[str]:
        """Wait for captcha solution"""
        try:
            logger.info(f"Waiting for captcha solution, task_id: {task_id}")
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                start_time = asyncio.get_event_loop().time()
                
                while (asyncio.get_event_loop().time() - start_time) < max_wait_time:
                    async with session.get(
                        f"{self.api_url}/result/{task_id}",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            
                            if result.get("status") == "completed":
                                solution = result.get("solution")
                                logger.info(f"Captcha solved successfully: {solution}")
                                return solution
                            elif result.get("status") == "failed":
                                logger.error(f"Captcha solving failed: {result.get('error')}")
                                return None
                        
                    await asyncio.sleep(2)  # Wait 2 seconds before checking again
                
                logger.warning(f"Timeout waiting for captcha solution: {task_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error waiting for captcha solution: {e}")
            return None


# Global instance
captcha_service = CaptchaService()

"""
Captcha solving module for BLS captcha handling
Handles solving of BLS image captchas using NoCaptchaAI
"""

import re
from typing import List, Optional, Dict, Any
from loguru import logger

from ..captcha_service import captcha_service


class CaptchaSolver:
    """Handles solving of BLS image captchas"""
    
    def __init__(self):
        self.captcha_service = captcha_service
    
    async def solve_bls_image_captcha(self, captcha_images: List[str], image_ids: List[str], instruction: str) -> Optional[List[str]]:
        """
        Solve BLS image captcha using NoCaptchaAI
        
        Args:
            captcha_images: List of base64 image data
            image_ids: List of image IDs
            instruction: Captcha instruction text
            
        Returns:
            List of selected image IDs or None if failed
        """
        try:
            logger.info(f"📸 Found {len(captcha_images)} captcha images with {len(image_ids)} IDs")
            logger.info(f"📝 Captcha instruction: {instruction}")
            
            # Solve with NoCaptchaAI
            solution = await self.captcha_service.solve_bls_images(captcha_images)
            
            if not solution:
                logger.error("❌ NoCaptchaAI failed to solve captcha")
                return None
            
            logger.info(f"✅ NoCaptchaAI solved successfully: {solution}")
            
            # Parse the solution
            selected_image_ids = self._parse_solution(solution, image_ids, instruction)
            
            if selected_image_ids:
                logger.info(f"🎯 Final selected image IDs: {selected_image_ids}")
                return selected_image_ids
            else:
                logger.error("❌ Failed to parse captcha solution")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error solving BLS image captcha: {e}")
            return None
    
    def _parse_solution(self, solution: str, image_ids: List[str], instruction: str) -> List[str]:
        """Parse NoCaptchaAI solution and match with image IDs"""
        try:
            # Extract target number from instruction
            target_match = re.search(r'number (\d+)', instruction)
            if not target_match:
                logger.error("❌ Could not extract target number from instruction")
                return []
            
            target_number = target_match.group(1)
            logger.info(f"🎯 Target number from instruction: {target_number}")
            
            # Parse solution string (e.g., "99944819810919819850619896")
            # Split into individual numbers
            solution_numbers = []
            i = 0
            while i < len(solution):
                # Try 3-digit numbers first
                if i + 3 <= len(solution):
                    num = solution[i:i+3]
                    if num.isdigit():
                        solution_numbers.append(num)
                        i += 3
                        continue
                
                # Try 2-digit numbers
                if i + 2 <= len(solution):
                    num = solution[i:i+2]
                    if num.isdigit():
                        solution_numbers.append(num)
                        i += 2
                        continue
                
                # Try 1-digit numbers
                if i + 1 <= len(solution):
                    num = solution[i:i+1]
                    if num.isdigit():
                        solution_numbers.append(num)
                        i += 1
                        continue
                
                i += 1
            
            logger.info(f"🎯 Parsed image values: {solution_numbers}")
            logger.info(f"🎯 Available image IDs: {image_ids}")
            
            # Match solution numbers with image IDs
            selected_image_ids = []
            
            for i, value in enumerate(solution_numbers):
                if i >= len(image_ids):
                    logger.warning(f"⚠️ Solution has more values than available images")
                    break
                
                if value == target_number:
                    selected_image_ids.append(image_ids[i])
                    logger.info(f"🎯 Selected image {i+1}: value '{value}' matches target '{target_number}' → ID '{image_ids[i]}'")
                else:
                    logger.info(f"🎯 Skipped image {i+1}: value '{value}' does not match target '{target_number}'")
            
            return selected_image_ids
            
        except Exception as e:
            logger.error(f"❌ Error parsing solution: {e}")
            return []

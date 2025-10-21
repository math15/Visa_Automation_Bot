"""
Instruction analysis module for BLS captcha handling
Handles extraction and analysis of captcha instructions using z-index
"""

import re
from typing import Optional, Tuple
from loguru import logger


class InstructionAnalyzer:
    """Handles analysis of captcha instructions using z-index"""
    
    def extract_instruction(self, content: str) -> Optional[str]:
        """
        Extract captcha instruction from HTML content using z-index analysis
        
        Args:
            content: HTML content containing captcha instructions
            
        Returns:
            Instruction string or None if not found
        """
        try:
            logger.info("🔍 Analyzing instruction using z-index method...")
            
            # Extract z-index mapping
            z_index_map = self._extract_z_index_map(content)
            
            # Find instruction divs
            instruction_matches = self._find_instruction_divs(content)
            
            if not instruction_matches:
                logger.warning("⚠️ No instruction divs found")
                return None
            
            # Find instruction with highest z-index
            target_instruction = self._find_highest_z_index_instruction(instruction_matches, z_index_map)
            
            if target_instruction:
                div_id, number, z_sum = target_instruction
                instruction = f"Please select all boxes with number {number}"
                logger.info(f"🎯 HIGHEST Z-INDEX INSTRUCTION: {instruction}")
                logger.info(f"✅ Div ID: {div_id}, Number: {number}, Z-index: {z_sum}")
                return instruction
            else:
                logger.warning("⚠️ No instruction divs found with z-index")
                # Fallback: use first instruction
                if instruction_matches:
                    div_classes, div_id, number = instruction_matches[0]
                    instruction = f"Please select all boxes with number {number}"
                    logger.info(f"🎯 Using fallback instruction: {instruction}")
                    return instruction
                    
        except Exception as e:
            logger.warning(f"⚠️ Error extracting instruction with z-index: {e}")
            return None
    
    def _extract_z_index_map(self, content: str) -> dict:
        """Extract z-index values from CSS styles"""
        # Extract all <style> blocks to get z-index values
        style_pattern = r'<style[^>]*>(.*?)</style>'
        style_matches = re.findall(style_pattern, content, re.DOTALL)
        styles = '\n'.join(style_matches)
        
        # Build a dictionary of class -> z-index
        z_index_map = {}
        for rule in re.findall(r"\.([\w-]+)\s*{[^}]*z-index\s*:\s*([^;]+);", styles):
            class_name, z = rule
            try:
                z_index_map[class_name.strip()] = int(z.strip())
            except ValueError:
                pass
        
        logger.info(f"📊 Found {len(z_index_map)} CSS classes with z-index values")
        return z_index_map
    
    def _find_instruction_divs(self, content: str) -> list:
        """Find all instruction divs in the content"""
        instruction_pattern = r"<div[^>]*class='([^']*box-label[^']*)'[^>]*id='([^']+)'[^>]*>Please select all boxes with number (\d+)</div>"
        instruction_matches = re.findall(instruction_pattern, content)
        
        logger.info(f"🔍 Found {len(instruction_matches)} instruction divs")
        return instruction_matches
    
    def _find_highest_z_index_instruction(self, instruction_matches: list, z_index_map: dict) -> Optional[Tuple[str, str, int]]:
        """Find the instruction with the highest z-index"""
        highest_z_index = -1
        target_instruction = None
        
        for div_classes, div_id, number in instruction_matches:
            # Calculate z-index sum for this div
            z_sum = 0
            for css_class in div_classes.split():
                if css_class in z_index_map:
                    z_sum += z_index_map[css_class]
            
            logger.info(f"   - Div ID: {div_id}, Number: {number}, Z-index sum: {z_sum}")
            
            if z_sum > highest_z_index:
                highest_z_index = z_sum
                target_instruction = (div_id, number, z_sum)
        
        return target_instruction

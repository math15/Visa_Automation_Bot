"""
Image extraction module for BLS captcha handling
Handles extraction of visible captcha images from HTML content
"""

import re
import base64
import html
from typing import List, Tuple, Dict, Any
from loguru import logger

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False


class ImageExtractor:
    """Handles extraction of visible captcha images from HTML content"""
    
    def __init__(self):
        self.container_divs = {'main-content', 'captcha-main-div', 'captcha-container', 'captcha-wrapper'}
    
    def extract_visible_images(self, content: str) -> Tuple[List[str], List[str]]:
        """
        Extract visible captcha images from HTML content
        
        Args:
            content: HTML content containing captcha images
            
        Returns:
            Tuple of (captcha_images, image_ids)
        """
        captcha_images = []
        image_ids = []
        
        # Decode HTML entities
        content = html.unescape(content)
        
        logger.info("🎯 Extracting VISIBLE image containers using BeautifulSoup")
        
        if BEAUTIFULSOUP_AVAILABLE:
            try:
                return self._extract_with_beautifulsoup(content)
            except Exception as e:
                logger.warning(f"⚠️ BeautifulSoup extraction failed: {e}")
                return self._extract_with_regex(content)
        else:
            logger.warning("⚠️ BeautifulSoup not available, using regex method")
            return self._extract_with_regex(content)
    
    def _extract_with_beautifulsoup(self, content: str) -> Tuple[List[str], List[str]]:
        """Extract images using BeautifulSoup"""
        logger.info(f"🔍 Processing content with BeautifulSoup: {len(content)} characters")
        logger.info(f"🔍 Content preview: {content[:200]}...")
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract CSS rules
        hidden_classes = self._get_hidden_css_classes(soup)
        
        # Find captcha image divs
        captcha_image_divs = self._find_captcha_image_divs(soup)
        
        # Analyze visibility
        visible_image_matches = self._analyze_image_visibility(captcha_image_divs, hidden_classes)
        
        # Process visible images
        return self._process_visible_images(visible_image_matches)
    
    def _get_hidden_css_classes(self, soup: BeautifulSoup) -> set:
        """Extract CSS classes that hide elements"""
        style_tags = soup.find_all('style')
        styles = '\n'.join([style.get_text() for style in style_tags])
        
        # Find CSS classes with display:none
        display_none_classes = re.findall(r'\.([\w-]+)\s*{[^}]*display\s*:\s*none[^}]*}', styles)
        logger.info(f"📊 Found {len(display_none_classes)} CSS classes with display:none")
        
        # Find CSS classes with opacity:0
        opacity_zero_classes = re.findall(r'\.([\w-]+)\s*{[^}]*opacity\s*:\s*0[^}]*}', styles)
        logger.info(f"📊 Found {len(opacity_zero_classes)} CSS classes with opacity:0")
        
        # Find CSS classes with visibility:hidden
        visibility_hidden_classes = re.findall(r'\.([\w-]+)\s*{[^}]*visibility\s*:\s*hidden[^}]*}', styles)
        logger.info(f"📊 Found {len(visibility_hidden_classes)} CSS classes with visibility:hidden")
        
        return set(display_none_classes + opacity_zero_classes + visibility_hidden_classes)
    
    def _find_captcha_image_divs(self, soup: BeautifulSoup) -> List:
        """Find all divs containing captcha images"""
        image_divs = soup.find_all('div', id=True)
        captcha_image_divs = []
        
        logger.info(f"🔍 Found {len(image_divs)} divs with IDs")
        
        # Look for all images first
        all_images = soup.find_all('img')
        logger.info(f"🔍 Found {len(all_images)} total images in content")
        
        for img in all_images:
            src = img.get('src', '')
            onclick = img.get('onclick', '')
            logger.info(f"🔍 Image src: {src[:50]}..., onclick: {onclick[:50]}...")
        
        for div in image_divs:
            div_id = div.get('id', '')
            
            # Skip container divs
            if div_id in self.container_divs:
                continue
                
            img = div.find('img', src=lambda x: x and x.startswith('data:image/'))
            if img and 'onclick' in img.attrs and 'Select(' in img['onclick']:
                captcha_image_divs.append(div)
        
        logger.info(f"📸 Found {len(captcha_image_divs)} divs containing captcha images")
        return captcha_image_divs
    
    def _analyze_image_visibility(self, captcha_image_divs: List, hidden_classes: set) -> List[Tuple[str, str, str]]:
        """Analyze which images are visible"""
        visible_image_matches = []
        
        for div in captcha_image_divs:
            div_id = div.get('id', 'no-id')
            div_classes = div.get('class', [])
            div_style = div.get('style', '')
            
            is_hidden = False
            hidden_reasons = []
            
            # Check if any CSS class is hidden
            for css_class in div_classes:
                if css_class in hidden_classes:
                    is_hidden = True
                    hidden_reasons.append(f"CSS class '{css_class}'")
            
            # Check inline style
            if div_style:
                style_lower = div_style.lower()
                if 'display:none' in style_lower or 'display: none' in style_lower:
                    is_hidden = True
                    hidden_reasons.append("inline style display:none")
                if 'opacity:0' in style_lower or 'opacity: 0' in style_lower:
                    is_hidden = True
                    hidden_reasons.append("inline style opacity:0")
                if 'visibility:hidden' in style_lower or 'visibility: hidden' in style_lower:
                    is_hidden = True
                    hidden_reasons.append("inline style visibility:hidden")
            
            # Get the image src and onclick
            img = div.find('img')
            if img:
                img_src = img.get('src', '')
                img_onclick = img.get('onclick', '')
                
                # Extract onclick ID
                onclick_match = re.search(r"Select\('([^']+)'", img_onclick)
                onclick_id = onclick_match.group(1) if onclick_match else 'no-onclick-id'
                
                if not is_hidden:
                    visible_image_matches.append((div_id, img_src, onclick_id))
                    logger.info(f"✅ Visible image: {div_id}")
                else:
                    logger.debug(f"❌ Hidden image {div_id}: {', '.join(hidden_reasons)}")
        
        logger.info(f"📸 Found {len(visible_image_matches)} VISIBLE image containers")
        return visible_image_matches
    
    def _process_visible_images(self, visible_image_matches: List[Tuple[str, str, str]]) -> Tuple[List[str], List[str]]:
        """Process visible images and extract valid ones"""
        image_data_list = []
        
        logger.info(f"🔍 Processing {len(visible_image_matches)} VISIBLE image containers...")
        
        for i, (container_id, image_src, onclick_id) in enumerate(visible_image_matches):
            logger.info(f"   Processing visible image {i+1}: container_id='{container_id}', onclick_id='{onclick_id}'")
            
            # Always use onclick_id as the captcha ID (not container_id)
            # The onclick ID is what BLS expects when submitting the solution
            try:
                # Extract just the base64 part for validation
                if 'base64,' in image_src:
                    base64_part = image_src.split('base64,')[1]
                    decoded = base64.b64decode(base64_part)
                    if len(decoded) > 50:  # Lower threshold for captcha images
                        image_data_list.append((image_src, onclick_id))
                        logger.info(f"✅ Found valid visible image with onclick ID: {onclick_id}")
                    else:
                        logger.warning(f"⚠️ Visible image {onclick_id} has invalid base64 data (too small)")
                else:
                    logger.warning(f"⚠️ Visible image {onclick_id} has no base64 data")
            except Exception as e:
                logger.warning(f"⚠️ Skipping invalid base64 data for visible image {onclick_id}: {e}")
        
        # Extract images and IDs in order
        captcha_images = []
        image_ids = []
        for image_src, onclick_id in image_data_list:
            captcha_images.append(image_src)
            image_ids.append(onclick_id)
        
        logger.info(f"🎯 Total captcha images found: {len(captcha_images)}")
        logger.info(f"🎯 Total image IDs found: {len(image_ids)}")
        
        return captcha_images, image_ids
    
    def _extract_with_regex(self, content: str) -> Tuple[List[str], List[str]]:
        """Fallback extraction using regex"""
        logger.info("🔄 Using regex fallback method")
        
        # Regex pattern for finding image containers
        image_pattern = r'<div[^>]*id="([^"]+)"[^>]*(?:style="([^"]*)")?[^>]*>.*?<img[^>]*src="(data:image/[^"]+)"[^>]*onclick="Select\(\'([^\']+)\',this\)"'
        image_matches = re.findall(image_pattern, content, re.IGNORECASE | re.DOTALL)
        
        # Filter for visible images only
        visible_image_matches = []
        for container_id, parent_style, image_src, onclick_id in image_matches:
            # Skip container divs
            if container_id in self.container_divs:
                continue
                
            # Check if parent container is visible
            is_visible = True
            
            if parent_style:
                parent_style_lower = parent_style.lower()
                # Check for hidden styles
                if any(hidden_style in parent_style_lower for hidden_style in [
                    'display:none', 'display: none', 
                    'opacity:0', 'opacity: 0',
                    'visibility:hidden', 'visibility: hidden',
                    'visibility:collapse', 'visibility: collapse'
                ]):
                    is_visible = False
                    logger.debug(f"   Hidden image {container_id}: {parent_style}")
            
            if is_visible:
                visible_image_matches.append((container_id, image_src, onclick_id))
                logger.info(f"✅ Visible image: {container_id}")
            else:
                logger.debug(f"❌ Hidden image: {container_id}")
        
        logger.info(f"📸 Found {len(visible_image_matches)} VISIBLE image containers")
        return self._process_visible_images(visible_image_matches)

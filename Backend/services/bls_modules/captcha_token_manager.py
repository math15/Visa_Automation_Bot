"""
Captcha Token Manager
Manages storage and retrieval of captcha response tokens
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from loguru import logger


class CaptchaTokenManager:
    """Manages captcha tokens - storage, retrieval, and validation"""
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize captcha token manager
        
        Args:
            storage_dir: Directory to store captcha tokens (default: Backend/captcha_tokens)
        """
        if storage_dir is None:
            # Default to Backend/captcha_tokens
            storage_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'captcha_tokens')
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        logger.info(f"📁 Captcha token storage: {self.storage_dir}")
    
    def store_token(self, response_data: Dict[str, any], visitor_id: str = None) -> bool:
        """
        Store captcha response token
        
        Args:
            response_data: Response from captcha submission containing:
                - success: bool
                - captcha: str (encrypted token)
                - captchaId: str
            visitor_id: Optional visitor ID for tracking
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # Generate timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Prepare storage data
            storage_data = {
                'timestamp': timestamp,
                'datetime': datetime.now().isoformat(),
                'visitor_id': visitor_id,
                'success': response_data.get('success'),
                'captcha_token': response_data.get('captcha'),
                'captcha_id': response_data.get('captchaId'),
                'full_response': response_data
            }
            
            # Save to timestamped file
            token_file = os.path.join(self.storage_dir, f'captcha_token_{timestamp}.json')
            with open(token_file, 'w', encoding='utf-8') as f:
                json.dump(storage_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Stored captcha token: {token_file}")
            logger.info(f"🔑 Token: {storage_data['captcha_token'][:50]}...")
            
            # Update latest token file
            latest_file = os.path.join(self.storage_dir, 'latest_captcha_token.json')
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(storage_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Updated latest token file")
            
            # Store by visitor ID if provided
            if visitor_id:
                visitor_file = os.path.join(self.storage_dir, f'visitor_{visitor_id}.json')
                with open(visitor_file, 'w', encoding='utf-8') as f:
                    json.dump(storage_data, f, indent=2, ensure_ascii=False)
                logger.info(f"💾 Stored token for visitor: {visitor_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing captcha token: {e}")
            return False
    
    def get_latest_token(self) -> Optional[Dict[str, any]]:
        """
        Get the most recent captcha token
        
        Returns:
            Token data dictionary or None if not found
        """
        try:
            latest_file = os.path.join(self.storage_dir, 'latest_captcha_token.json')
            
            if not os.path.exists(latest_file):
                logger.warning("⚠️ No latest token file found")
                return None
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"📖 Loaded latest token: {data['captcha_token'][:50]}...")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error loading latest token: {e}")
            return None
    
    def get_token_by_visitor(self, visitor_id: str) -> Optional[Dict[str, any]]:
        """
        Get captcha token for specific visitor
        
        Args:
            visitor_id: Visitor ID to look up
            
        Returns:
            Token data dictionary or None if not found
        """
        try:
            visitor_file = os.path.join(self.storage_dir, f'visitor_{visitor_id}.json')
            
            if not os.path.exists(visitor_file):
                logger.warning(f"⚠️ No token found for visitor: {visitor_id}")
                return None
            
            with open(visitor_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"📖 Loaded token for visitor {visitor_id}: {data['captcha_token'][:50]}...")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error loading token for visitor {visitor_id}: {e}")
            return None
    
    def get_all_tokens(self, max_age_hours: int = 24) -> List[Dict[str, any]]:
        """
        Get all captcha tokens within time range
        
        Args:
            max_age_hours: Maximum age of tokens to return (default 24 hours)
            
        Returns:
            List of token data dictionaries
        """
        try:
            tokens = []
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            # List all token files
            for filename in os.listdir(self.storage_dir):
                if filename.startswith('captcha_token_') and filename.endswith('.json'):
                    filepath = os.path.join(self.storage_dir, filename)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Check age
                        token_time = datetime.fromisoformat(data['datetime'])
                        if token_time >= cutoff_time:
                            tokens.append(data)
                    except Exception as e:
                        logger.warning(f"⚠️ Error loading {filename}: {e}")
            
            logger.info(f"📖 Loaded {len(tokens)} tokens from last {max_age_hours} hours")
            return tokens
            
        except Exception as e:
            logger.error(f"❌ Error loading tokens: {e}")
            return []
    
    def cleanup_old_tokens(self, max_age_days: int = 7) -> int:
        """
        Clean up old token files
        
        Args:
            max_age_days: Maximum age of tokens to keep (default 7 days)
            
        Returns:
            Number of files deleted
        """
        try:
            deleted_count = 0
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            
            # List all token files
            for filename in os.listdir(self.storage_dir):
                if filename.startswith('captcha_token_') and filename.endswith('.json'):
                    filepath = os.path.join(self.storage_dir, filename)
                    
                    try:
                        # Check file age
                        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        if file_time < cutoff_time:
                            os.remove(filepath)
                            deleted_count += 1
                            logger.info(f"🗑️ Deleted old token: {filename}")
                    except Exception as e:
                        logger.warning(f"⚠️ Error deleting {filename}: {e}")
            
            logger.info(f"🧹 Cleaned up {deleted_count} old token files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up tokens: {e}")
            return 0
    
    def is_token_valid(self, token_data: Dict[str, any], max_age_minutes: int = 30) -> bool:
        """
        Check if token is still valid
        
        Args:
            token_data: Token data dictionary
            max_age_minutes: Maximum age of token in minutes (default 30)
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            token_time = datetime.fromisoformat(token_data['datetime'])
            age = datetime.now() - token_time
            
            is_valid = age.total_seconds() < (max_age_minutes * 60)
            
            if is_valid:
                logger.info(f"✅ Token is valid (age: {age.total_seconds():.0f}s)")
            else:
                logger.warning(f"⚠️ Token is expired (age: {age.total_seconds():.0f}s, max: {max_age_minutes * 60}s)")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"❌ Error checking token validity: {e}")
            return False


# Global instance
captcha_token_manager = CaptchaTokenManager()


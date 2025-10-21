"""
Proxy Service for BLS Account Creation
Manages proxy rotation and validation for BLS website access
"""

import random
import aiohttp
from typing import Optional, Dict, Any, List
from loguru import logger
from sqlalchemy.orm import Session
from models.database import Proxy
from database.config import get_db

class ProxyService:
    """Service for managing proxies for BLS website access"""
    
    def __init__(self):
        self.current_proxy = None
        self.proxy_pool = []
        
    async def get_algerian_proxy(self, db: Session) -> Optional[Dict[str, Any]]:
        """Get a proxy for BLS website access (Algeria or Spain)"""
        try:
            # Try Algeria first, then Spain
            allowed_countries = ["DZ", "ES"]  # Algeria and Spain
            
            for country in allowed_countries:
                proxies = db.query(Proxy).filter(
                    Proxy.country == country,
                    Proxy.is_active == True
                ).all()
                
                if proxies:
                    # Select a random proxy
                    proxy = random.choice(proxies)
                    
                    proxy_config = {
                        "host": proxy.host,
                        "port": proxy.port,
                        "username": proxy.username,
                        "password": proxy.password,
                        "country": proxy.country
                    }
                    
                    logger.info(f"Selected {country} proxy: {proxy.host}:{proxy.port}")
                    return proxy_config
            
            logger.warning("No Algerian or Spanish proxies found in database")
            return None
            
        except Exception as e:
            logger.error(f"Error getting Algerian proxy: {e}")
            return None
    
    async def validate_proxy(self, proxy_config: Dict[str, Any]) -> bool:
        """Validate if a proxy is working"""
        try:
            proxy_url = self._build_proxy_url(proxy_config)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://httpbin.org/ip",
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Proxy validation successful: {result.get('origin')}")
                        return True
                    else:
                        logger.warning(f"Proxy validation failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Proxy validation error: {e}")
            return False
    
    def _build_proxy_url(self, proxy_config: Dict[str, Any]) -> str:
        """Build proxy URL for aiohttp"""
        if proxy_config.get("username") and proxy_config.get("password"):
            # URL encode the username and password to handle special characters
            import urllib.parse
            username = urllib.parse.quote(proxy_config['username'], safe='')
            password = urllib.parse.quote(proxy_config['password'], safe='')
            return f"http://{username}:{password}@{proxy_config['host']}:{proxy_config['port']}"
        else:
            return f"http://{proxy_config['host']}:{proxy_config['port']}"
    
    async def get_proxy_for_bls(self, db: Session, skip_validation: bool = False) -> Optional[str]:
        """Get a proxy for BLS website access"""
        try:
            # Get proxy (Algeria or Spain)
            proxy_config = await self.get_algerian_proxy(db)
            if not proxy_config:
                logger.warning("No Algerian or Spanish proxy available")
                return None
            
            # Validate proxy (unless skipped)
            if not skip_validation:
                is_valid = await self.validate_proxy(proxy_config)
                if not is_valid:
                    logger.warning(f"Proxy validation failed: {proxy_config['host']}:{proxy_config['port']}")
                    return None
                logger.info(f"Using validated proxy: {proxy_config['host']}:{proxy_config['port']}")
            else:
                logger.info(f"Using proxy without validation: {proxy_config['host']}:{proxy_config['port']}")
            
            # Build proxy URL
            proxy_url = self._build_proxy_url(proxy_config)
            
            return proxy_url
            
        except Exception as e:
            logger.error(f"Error getting proxy for BLS: {e}")
            return None

# Global instance
proxy_service = ProxyService()

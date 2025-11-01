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
        self.recently_used_proxies = []  # Track recently used proxies
        self.max_recent_cache = 5  # Remember last 5 used proxies
        
    async def get_algerian_proxy(self, db: Session, avoid_recent: bool = True) -> Optional[Dict[str, Any]]:
        """Get a proxy for BLS website access (Algeria or Spain)
        
        Args:
            db: Database session
            avoid_recent: If True, try to avoid recently used proxies for better rotation
        """
        try:
            # Try Algeria first, then Spain
            allowed_countries = ["DZ", "ES"]  # Algeria and Spain
            
            for country in allowed_countries:
                proxies = db.query(Proxy).filter(
                    Proxy.country == country,
                    Proxy.is_active == True
                ).all()
                
                if proxies:
                    # Filter out recently used proxies if we have enough proxies
                    available_proxies = proxies
                    
                    if avoid_recent and len(proxies) > 1:
                        # Try to avoid recently used proxies
                        available_proxies = [
                            p for p in proxies 
                            if f"{p.host}:{p.port}" not in self.recently_used_proxies
                        ]
                        
                        # If all proxies were recently used, use all proxies
                        if not available_proxies:
                            logger.info(f"All {country} proxies were recently used, resetting rotation")
                            available_proxies = proxies
                            self.recently_used_proxies.clear()
                    
                    # Select a random proxy from available ones
                    proxy = random.choice(available_proxies)
                    
                    # Track this proxy as recently used
                    proxy_key = f"{proxy.host}:{proxy.port}"
                    if proxy_key not in self.recently_used_proxies:
                        self.recently_used_proxies.append(proxy_key)
                        
                    # Keep only the last N proxies in the cache
                    if len(self.recently_used_proxies) > self.max_recent_cache:
                        self.recently_used_proxies.pop(0)
                    
                    proxy_config = {
                        "host": proxy.host,
                        "port": proxy.port,
                        "username": proxy.username,
                        "password": proxy.password,
                        "country": proxy.country,
                        "id": proxy.id
                    }
                    
                    logger.info(f"🎲 Selected {country} proxy (ID:{proxy.id}): {proxy.host}:{proxy.port}")
                    logger.info(f"📋 Recently used proxies: {len(self.recently_used_proxies)}/{self.max_recent_cache}")
                    return proxy_config
            
            logger.warning("No Algerian or Spanish proxies found in database")
            return None
            
        except Exception as e:
            logger.error(f"Error getting Algerian proxy: {e}")
            return None
    
    async def validate_proxy(self, proxy_config: Dict[str, Any], check_traffic: bool = True) -> bool:
        """Validate if a proxy is working
        
        Args:
            proxy_config: Proxy configuration dictionary
            check_traffic: If True, also check for traffic exhaustion errors
        """
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
            error_msg = str(e).lower()
            
            # Check for specific proxy errors
            if 'traffic_exhausted' in error_msg or '407' in error_msg:
                logger.error(f"❌ Proxy traffic exhausted: {proxy_config['host']}:{proxy_config['port']}")
                logger.warning(f"💡 Please top up your DataImpulse account or wait for traffic reset")
            elif 'timeout' in error_msg:
                logger.error(f"⏱️ Proxy timeout: {proxy_config['host']}:{proxy_config['port']}")
            else:
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
    
    async def mark_proxy_used(self, db: Session, proxy_id: int):
        """Mark a proxy as used and update usage statistics"""
        try:
            from datetime import datetime
            
            proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
            if proxy:
                # Add usage tracking fields if they exist
                if hasattr(proxy, 'usage_count'):
                    proxy.usage_count = (proxy.usage_count or 0) + 1
                if hasattr(proxy, 'last_used'):
                    proxy.last_used = datetime.utcnow()
                
                db.commit()
                logger.debug(f"Updated usage stats for proxy ID:{proxy_id}")
        except Exception as e:
            logger.warning(f"Could not update proxy usage stats: {e}")
    
    async def get_proxy_for_bls(self, db: Session, skip_validation: bool = False, avoid_recent: bool = True) -> Optional[str]:
        """Get a proxy for BLS website access
        
        Args:
            db: Database session
            skip_validation: If True, skip proxy validation
            avoid_recent: If True, avoid recently used proxies for better rotation
        """
        try:
            # Get proxy (Algeria or Spain)
            proxy_config = await self.get_algerian_proxy(db, avoid_recent=avoid_recent)
            if not proxy_config:
                logger.warning("No Algerian or Spanish proxy available")
                return None
            
            # Validate proxy (unless skipped)
            if not skip_validation:
                is_valid = await self.validate_proxy(proxy_config)
                if not is_valid:
                    logger.warning(f"Proxy validation failed: {proxy_config['host']}:{proxy_config['port']}")
                    # Mark as invalid and try to get another one
                    proxy = db.query(Proxy).filter(Proxy.id == proxy_config['id']).first()
                    if proxy:
                        proxy.validation_status = "invalid"
                        db.commit()
                    return None
                logger.info(f"✅ Using validated proxy: {proxy_config['host']}:{proxy_config['port']}")
            else:
                logger.info(f"🔄 Using proxy without validation: {proxy_config['host']}:{proxy_config['port']}")
            
            # Mark proxy as used
            await self.mark_proxy_used(db, proxy_config['id'])
            
            # Build proxy URL
            proxy_url = self._build_proxy_url(proxy_config)
            
            return proxy_url
            
        except Exception as e:
            logger.error(f"Error getting proxy for BLS: {e}")
            return None

# Global instance
proxy_service = ProxyService()

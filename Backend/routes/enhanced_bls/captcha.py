from fastapi import APIRouter, HTTPException, Response, Form
from typing import Dict, Any, Optional, List
from loguru import logger
import aiohttp
import re

from services.captcha_service import captcha_service

router = APIRouter()

@router.post("/captcha-solution")
async def submit_captcha_solution(request: Dict[str, str]):
    try:
        solution = request.get("solution")
        data_param = request.get("data_param")
        if not solution or not data_param:
            raise HTTPException(status_code=400, detail="solution and data_param are required")
        # No persistent store here; upstream flow should consume immediately
        return {"success": True, "message": "Captcha solution accepted", "data_param": data_param}
    except Exception as e:
        logger.error(f"Error storing captcha solution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fetch-captcha-images")
async def fetch_captcha_images(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        data_param: str = payload.get("data") or payload.get("captcha_data_param")
        if not data_param:
            raise HTTPException(status_code=400, detail="Missing captcha data parameter")

        proxy: Optional[str] = payload.get("proxy")
        waf_token: Optional[str] = payload.get("waf_token")
        visitor_id: Optional[str] = payload.get("visitor_id")
        antiforgery_cookie: Optional[str] = payload.get("antiforgery_cookie")
        timeout_seconds: int = int(payload.get("timeout", 15))
        auto_solve: bool = bool(payload.get("auto_solve", False))

        captcha_url = f"https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha?data={data_param}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://algeria.blsspainglobal.com/dza/account/RegisterUser",
            "Sec-Fetch-Dest": "iframe",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
        }

        cookie_parts: List[str] = []
        if waf_token:
            cookie_parts.append(f"aws-waf-token={waf_token}")
        if antiforgery_cookie:
            cookie_parts.append(antiforgery_cookie)
        if visitor_id:
            cookie_parts.append(f"visitorId_current={visitor_id}")
        if cookie_parts:
            headers["Cookie"] = "; ".join(cookie_parts)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                captcha_url,
                headers=headers,
                proxy=proxy,
                timeout=aiohttp.ClientTimeout(total=timeout_seconds)
            ) as response:
                html = await response.text()
                status_code = response.status
                logger.info(f"📡 Captcha page fetched: {status_code}, length={len(html)}")

        instruction = None
        try:
            # Look for the instruction that's actually displayed (has display:inline CSS class)
            # First, find CSS classes with display:inline
            css_pattern = r'\.([a-zA-Z0-9]+)\{display:inline;\}'
            css_matches = re.findall(css_pattern, html)
            
            if css_matches:
                # Look for box-label divs that have one of the display:inline classes
                for css_class in css_matches:
                    instruction_pattern = rf'<div[^>]*class="[^"]*{re.escape(css_class)}[^"]*"[^>]*class="[^"]*box-label[^"]*"[^>]*>(.*?)</div>'
                    m = re.search(instruction_pattern, html, re.IGNORECASE | re.DOTALL)
                    if m:
                        instruction = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
                        logger.info(f"🎯 Found displayed instruction: {instruction}")
                        break
            
            # Fallback: if no displayed instruction found, get the first one
            if not instruction:
                m = re.search(r'<div[^>]*class=["\']box-label["\'][^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
                if m:
                    instruction = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
                    logger.info(f"🎯 Found fallback instruction: {instruction}")
        except Exception as e:
            logger.warning(f"⚠️ Error extracting instruction: {e}")
            instruction = None

        src_to_id: Dict[str, str] = {}
        try:
            for m in re.finditer(r'<img[^>]*?(?:id=["\']([^"\']+)["\'][^>]*?src=["\'](data:image/[^"\']+)["\']|src=["\'](data:image/[^"\']+)["\'][^>]*?id=["\']([^"\']+)["\'])', html, re.IGNORECASE):
                img_id = m.group(1) or m.group(4)
                src = m.group(2) or m.group(3)
                if img_id and src:
                    src_to_id[src] = img_id
        except Exception:
            pass

        images: List[str] = []
        for m in re.finditer(r'(data:image/[^;]+;base64,[A-Za-z0-9+/=]+)', html):
            images.append(m.group(1))
            if len(images) >= 9:
                break

        if not images:
            logger.error("No base64 images found in captcha page")
            return {"success": False, "status_code": status_code, "message": "No images found", "html_length": len(html)}

        image_ids: List[Optional[str]] = []
        for src in images:
            image_ids.append(src_to_id.get(src))

        result: Dict[str, Any] = {
            "success": True,
            "status_code": status_code,
            "count": len(images),
            "images": images,
            "image_ids": image_ids,
            "instruction": instruction,
        }

        if auto_solve:
            try:
                solution = await captcha_service.solve_bls_images(images)
                result["auto_solved"] = bool(solution)
                result["solution"] = solution
            except Exception as e:
                logger.error(f"Auto-solve failed: {e}")
                result["auto_solved"] = False

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching captcha images: {e}")
        raise HTTPException(status_code=500, detail=str(e))



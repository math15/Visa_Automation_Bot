#!/usr/bin/env python3
"""
Launch multiple Chromium instances with different proxy configurations.

This script relies on Playwright. Install it (and the Chromium driver) with:

    pip install playwright
    playwright install chromium

Proxies are read from the repository-level `proxy.txt` file. Each line should be
formatted in one of the following styles:

    host:port
    host:port:username:password

Only the first five proxies are used by default, but you can change the target
count via the CLI argument `--count`.
"""

import argparse
import asyncio
import random
import signal
from pathlib import Path
from typing import Dict, List, Optional

from playwright.async_api import async_playwright, BrowserContext

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent
PROXY_CANDIDATES = [
    ROOT_DIR / "proxy.txt",
    SCRIPT_DIR / "proxy.txt",
]
PROFILE_ROOT = ROOT_DIR / ".proxy_profiles"

TARGET_URL = "https://algeria.blsspainvisa.com"


def parse_proxy_line(line: str) -> Optional[Dict[str, str]]:
    """
    Convert a proxy line into a Playwright proxy dictionary.

    Supported formats:
        host:port
        host:port:username:password
    """
    parts = [part.strip() for part in line.split(":") if part.strip()]
    if len(parts) < 2:
        return None

    host, port = parts[0], parts[1]
    proxy: Dict[str, str] = {"server": f"http://{host}:{port}"}

    if len(parts) >= 4:
        proxy["username"] = parts[2]
        proxy["password"] = parts[3]

    return proxy


def resolve_proxy_file() -> Path:
    for candidate in PROXY_CANDIDATES:
        if candidate.exists():
            return candidate
    search_paths = ", ".join(str(p) for p in PROXY_CANDIDATES)
    raise FileNotFoundError(f"Proxy file not found in any of: {search_paths}")


def load_proxies(path: Path, max_count: int) -> List[Dict[str, str]]:
    proxies: List[Dict[str, str]] = []

    if not path.exists():
        raise FileNotFoundError(f"Proxy file not found: {path}")

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        proxy = parse_proxy_line(line)
        if proxy:
            proxies.append(proxy)

    if not proxies:
        raise ValueError(f"No valid proxies found in {path}")

    if len(proxies) <= max_count:
        return proxies

    return random.sample(proxies, k=max_count)


async def launch_browser_with_proxy(
    index: int,
    proxy: Dict[str, str],
    playwright,
    url: str,
) -> BrowserContext:
    # Ensure each browser instance uses its own user-data-dir to keep sessions isolated.
    profile_dir = PROFILE_ROOT / f"profile_{index}"
    profile_dir.mkdir(parents=True, exist_ok=True)

    context = await playwright.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        headless=False,
        proxy=proxy,
        viewport={"width": 1280, "height": 800},
        args=[
            f"--window-position={100 + (index * 40)},{100 + (index * 40)}",
        ],
    )

    page = context.pages[0] if context.pages else await context.new_page()
    await page.goto(url, wait_until="load")
    await page.wait_for_timeout(2000)  # Let the page settle.

    return context


async def main(count: int, url: str):
    PROFILE_ROOT.mkdir(parents=True, exist_ok=True)
    proxy_path = resolve_proxy_file()
    proxies = load_proxies(proxy_path, max_count=count)

    contexts: List[BrowserContext] = []

    async with async_playwright() as playwright:
        try:
            launch_tasks = [
                launch_browser_with_proxy(idx + 1, proxy, playwright, url)
                for idx, proxy in enumerate(proxies)
            ]
            contexts = await asyncio.gather(*launch_tasks)

            print(
                f"✅ Launched {len(contexts)} Chromium instance(s). "
                "Press CTRL+C to close them."
            )

            # Keep the script alive until the user interrupts.
            stop_event = asyncio.Event()

            def handle_signal(*_):
                stop_event.set()

            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, handle_signal)

            await stop_event.wait()

        finally:
            print("🔻 Closing browsers...")
            await asyncio.gather(
                *(context.close() for context in contexts if context),
                return_exceptions=True,
            )
            print("✅ All browsers closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Launch multiple Chromium instances with proxy settings."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of proxy browsers to launch (default: 5)",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=TARGET_URL,
        help=f"Initial URL to open in each browser (default: {TARGET_URL})",
    )
    args = parser.parse_args()

    try:
        asyncio.run(main(args.count, args.url))
    except KeyboardInterrupt:
        pass


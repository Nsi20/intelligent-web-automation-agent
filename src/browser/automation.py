"""Browser automation wrapper using Playwright."""
import asyncio
import random
from pathlib import Path
from typing import Optional, Any
from datetime import datetime
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from config.settings import settings
from src.utils.logger import logger


class BrowserAutomation:
    """Playwright-based browser automation with session management."""
    
    def __init__(self, headless: Optional[bool] = None):
        """Initialize browser automation.
        
        Args:
            headless: Run in headless mode (default from settings)
        """
        self.headless = headless if headless is not None else settings.browser_headless
        self.timeout = settings.browser_timeout
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def start(self):
        """Start browser and create context."""
        logger.info(f"Starting browser (headless={self.headless})...")
        self.playwright = await async_playwright().start()
        
        # Stealth arguments
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--disable-dev-shm-usage",
            "--disable-browser-side-navigation",
            "--disable-gpu",
        ]
        
        ignore_default_args = ["--enable-automation"]
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=args,
            ignore_default_args=ignore_default_args
        )
        
        # Random User-Agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        user_agent = random.choice(user_agents)
        logger.info(f"Using User-Agent: {user_agent}")
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=user_agent,
            locale="en-US",
            timezone_id="America/New_York",
        )
        
        # Add stealth scripts to context
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = await self.context.new_page()
        self.page.set_default_timeout(self.timeout)
        logger.info("Browser started successfully with stealth settings")
        
    async def close(self):
        """Close browser and cleanup."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")
        
    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> None:
        """Navigate to URL.
        
        Args:
            url: Target URL
            wait_until: Wait condition (load, domcontentloaded, networkidle)
        """
        logger.info(f"Navigating to: {url}")
        await self.page.goto(url, wait_until=wait_until)
        logger.debug(f"Page loaded: {self.page.url}")
        
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> Any:
        """Wait for element to appear.
        
        Args:
            selector: CSS selector
            timeout: Custom timeout in milliseconds
            
        Returns:
            Element handle
        """
        timeout = timeout or self.timeout
        logger.debug(f"Waiting for selector: {selector}")
        return await self.page.wait_for_selector(selector, timeout=timeout)
        
    async def click(self, selector: str) -> None:
        """Click element.
        
        Args:
            selector: CSS selector
        """
        logger.debug(f"Clicking: {selector}")
        await self.page.click(selector)
        
    async def fill(self, selector: str, text: str) -> None:
        """Fill input field.
        
        Args:
            selector: CSS selector
            text: Text to fill
        """
        logger.debug(f"Filling {selector} with text")
        await self.page.fill(selector, text)
        
    async def get_text(self, selector: str) -> str:
        """Get element text content.
        
        Args:
            selector: CSS selector
            
        Returns:
            Text content
        """
        element = await self.page.query_selector(selector)
        if element:
            return await element.text_content() or ""
        return ""
        
    async def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get element attribute.
        
        Args:
            selector: CSS selector
            attribute: Attribute name
            
        Returns:
            Attribute value or None
        """
        element = await self.page.query_selector(selector)
        if element:
            return await element.get_attribute(attribute)
        return None
        
    async def get_html(self) -> str:
        """Get page HTML content.
        
        Returns:
            HTML content
        """
        return await self.page.content()
        
    async def screenshot(self, filename: Optional[str] = None) -> Path:
        """Take screenshot.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to screenshot file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
        screenshot_dir = Path("screenshots")
        screenshot_dir.mkdir(exist_ok=True)
        filepath = screenshot_dir / filename
        
        await self.page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"Screenshot saved: {filepath}")
        return filepath
        
    async def evaluate(self, script: str) -> Any:
        """Execute JavaScript in page context.
        
        Args:
            script: JavaScript code
            
        Returns:
            Script result
        """
        return await self.page.evaluate(script)
        
    async def query_selector_all(self, selector: str) -> list:
        """Get all matching elements.
        
        Args:
            selector: CSS selector
            
        Returns:
            List of element handles
        """
        return await self.page.query_selector_all(selector)

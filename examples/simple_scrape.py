"""Simple web scraping example using the automation framework."""
import asyncio
from src.browser.automation import BrowserAutomation
from src.llm.client import LLMClient


async def main():
    """Scrape Hacker News front page and extract top stories."""
    print("🌐 Simple Web Scraping Example\n")
    
    url = "https://news.ycombinator.com"
    
    # Initialize browser and LLM
    llm = LLMClient()
    
    async with BrowserAutomation(headless=False) as browser:
        # Navigate to page
        print(f"Navigating to {url}...")
        await browser.navigate(url)
        
        # Get page content
        html = await browser.get_html()
        
        # Take screenshot
        screenshot = await browser.screenshot("hackernews.png")
        print(f"Screenshot saved: {screenshot}")
        
    # Use LLM to extract data
    print("\nExtracting top stories using LLM...")
    prompt = """Extract the top 5 story titles from this Hacker News page HTML.

Return them as a numbered list.

HTML:
""" + html[:5000]
    
    response = llm.chat(prompt)
    
    print("\nTop Stories:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())

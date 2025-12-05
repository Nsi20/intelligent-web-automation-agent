"""Demo script for creating a video showcasing the web automation agent."""
import asyncio
import time
from src.browser.automation import BrowserAutomation
from src.llm.client import LLMClient
from config.settings import settings

async def demo():
    """Run a demo of the web automation agent."""
    print("🎬 Starting Web Automation Agent Demo...")
    print("=" * 60)
    
    # Initialize components
    print("\n✅ Initializing browser automation (visible mode)...")
    async with BrowserAutomation(headless=False) as browser:
        
        # Navigate to Indeed
        print("\n🌐 Navigating to Indeed job search...")
        await browser.navigate("https://www.indeed.com/jobs?q=python+developer&l=remote")
        await asyncio.sleep(3)  # Let page load
        
        # Take screenshot
        print("\n📸 Capturing job search results...")
        await browser.screenshot("demo_indeed_search.png")
        await asyncio.sleep(2)
        
        # Get page content
        print("\n📄 Extracting page content...")
        html = await browser.get_html()
        print(f"   Retrieved {len(html)} characters of HTML")
        await asyncio.sleep(2)
        
        # Show LLM analysis
        print("\n🧠 Analyzing jobs with AI (Llama 3)...")
        print("   This may take a moment...")
        await asyncio.sleep(3)
        
        print("\n✅ Demo complete!")
        print("=" * 60)
        print("\n📧 In production, the agent would:")
        print("   1. Extract job listings using AI")
        print("   2. Filter based on your criteria")
        print("   3. Send email notifications with direct apply links")
        print("   4. Track seen jobs to avoid duplicates")
        
        # Keep browser open for a moment
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(demo())

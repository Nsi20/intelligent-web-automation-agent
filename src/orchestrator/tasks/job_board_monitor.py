"""Indeed job board monitoring task."""
import asyncio
import json
from typing import Optional
from bs4 import BeautifulSoup

from src.browser.automation import BrowserAutomation
from src.llm.client import LLMClient
from src.llm.prompts import EXTRACT_JOB_LISTINGS, SUMMARIZE_JOBS
from src.utils.storage import JobStorage
from src.utils.notifications import EmailNotifier
from src.utils.logger import logger
from config.settings import settings


class IndeedJobMonitor:
    """Monitor Indeed job board for new listings."""
    
    def __init__(self):
        """Initialize job monitor."""
        self.llm = LLMClient()
        self.storage = JobStorage()
        self.notifier = EmailNotifier()
        
    def _build_indeed_url(self, keywords: str, location: str) -> str:
        """Build Indeed search URL.
        
        Args:
            keywords: Job search keywords
            location: Job location
            
        Returns:
            Indeed search URL
        """
        # URL encode keywords and location
        keywords_encoded = keywords.replace(" ", "+")
        location_encoded = location.replace(" ", "+")
        
        url = f"https://www.indeed.com/jobs?q={keywords_encoded}&l={location_encoded}"
        logger.info(f"Built Indeed URL: {url}")
        return url
        
    async def extract_jobs_from_html(self, html: str) -> list[dict]:
        """Extract job listings from Indeed HTML using LLM.
        
        Args:
            html: Page HTML content
            
        Returns:
            List of job dictionaries
        """
        logger.info("Extracting jobs from HTML using LLM...")
        
        # Parse HTML to get cleaner content
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content (limit size for LLM)
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Also get job cards HTML (Indeed uses specific structure)
        job_cards = soup.find_all('div', class_=lambda x: x and 'job' in x.lower())
        logger.info(f"DEBUG: Found {len(job_cards)} job cards in HTML")
        
        # Prepare structured content with explicit URLs
        structured_content = []
        for i, card in enumerate(job_cards[:20], 1):
            # Extract URL
            url = "N/A"
            link = card.find('a', href=True)
            if link:
                href = link['href']
                if href.startswith('/'):
                    url = f"https://www.indeed.com{href}"
                else:
                    url = href
            
            structured_content.append(f"""
JOB {i}:
URL: {url}
HTML:
{str(card)[:1000]}
---""")

        content_for_llm = "\n".join(structured_content)
        
        # Use LLM to extract structured data
        prompt = f"""{EXTRACT_JOB_LISTINGS}

HTML Content:
{content_for_llm}

Extract all job listings you can find. Be thorough but accurate."""

        response = await self.llm.achat(prompt)
        
        # Parse JSON response
        try:
            # Try to find JSON in response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                jobs = json.loads(json_str)
                logger.info(f"Extracted {len(jobs)} jobs from HTML")
                return jobs
            else:
                logger.warning("No JSON found in LLM response")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"LLM response: {response[:500]}")
            return []
            
    async def filter_jobs(self, jobs: list[dict], criteria: Optional[str] = None) -> list[dict]:
        """Filter jobs based on criteria using LLM.
        
        Args:
            jobs: List of job dictionaries
            criteria: Optional filtering criteria
            
        Returns:
            Filtered list of jobs
        """
        if not criteria or not jobs:
            return jobs
            
        logger.info(f"Filtering {len(jobs)} jobs with criteria: {criteria}")
        
        # Create job descriptions for LLM
        job_descriptions = []
        for i, job in enumerate(jobs, 1):
            desc = f"{i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')} - {job.get('location', 'N/A')}"
            if job.get('description'):
                desc += f"\n   {job.get('description')[:200]}"
            job_descriptions.append(desc)
            
        jobs_text = "\n".join(job_descriptions)
        
        prompt = f"""Filter these jobs based on the criteria:

Criteria: {criteria}

Jobs:
{jobs_text}

Return ONLY the numbers of relevant jobs (e.g., "1, 3, 5"), or "none" if no matches."""

        response = await self.llm.achat(prompt)
        
        # Parse response
        try:
            if "none" in response.lower():
                logger.info("No jobs matched criteria")
                return []
                
            indices = [int(x.strip()) - 1 for x in response.split(",") if x.strip().replace(" ", "").isdigit()]
            filtered_jobs = [jobs[i] for i in indices if 0 <= i < len(jobs)]
            logger.info(f"Filtered to {len(filtered_jobs)} relevant jobs")
            return filtered_jobs
            
        except Exception as e:
            logger.warning(f"Failed to parse filter response, returning all jobs: {e}")
            return jobs
            
    async def generate_summary(self, jobs: list[dict]) -> str:
        """Generate summary of job listings using LLM.
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Summary text
        """
        if not jobs:
            return "No jobs found matching your criteria."
            
        logger.info(f"Generating summary for {len(jobs)} jobs...")
        
        jobs_text = json.dumps(jobs, indent=2)
        
        prompt = f"""{SUMMARIZE_JOBS}

Job Listings:
{jobs_text}

Create a professional, engaging summary."""

        summary = await self.llm.achat(prompt)
        return summary
        
    async def run(self, 
                  keywords: Optional[str] = None,
                  location: Optional[str] = None,
                  filter_criteria: Optional[str] = None,
                  send_email: bool = True) -> dict:
        """Run job monitoring workflow.
        
        Args:
            keywords: Job search keywords (default from settings)
            location: Job location (default from settings)
            filter_criteria: Optional LLM filtering criteria
            send_email: Whether to send email notification
            
        Returns:
            Results dictionary with jobs and summary
        """
        keywords = keywords or settings.job_search_keywords
        location = location or settings.job_location
        
        logger.info(f"Starting job monitoring: keywords='{keywords}', location='{location}'")
        
        # Build URL
        url = self._build_indeed_url(keywords, location)
        
        # Start browser and navigate
        async with BrowserAutomation(headless=settings.browser_headless) as browser:
            await browser.navigate(url)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Take screenshot for debugging
            await browser.screenshot("indeed_search_results.png")
            
            # Get page HTML
            html = await browser.get_html()
            
        # Extract jobs using LLM
        all_jobs = await self.extract_jobs_from_html(html)
        
        if not all_jobs:
            logger.warning("No jobs extracted from page")
            return {"jobs": [], "new_jobs": [], "summary": "No jobs found."}
            
        # Filter jobs if criteria provided
        if filter_criteria:
            filtered_jobs = await self.filter_jobs(all_jobs, filter_criteria)
        else:
            filtered_jobs = all_jobs
            
        # Get only new jobs (not seen before)
        new_jobs = self.storage.get_new_jobs(filtered_jobs)
        
        # Generate summary
        summary = await self.generate_summary(new_jobs)
        
        # Save jobs
        self.storage.save_jobs(new_jobs, keywords)
        
        # Mark jobs as seen
        job_urls = [job.get('url', '') for job in filtered_jobs if job.get('url')]
        self.storage.mark_jobs_seen(job_urls)
        
        # Update last run
        self.storage.update_last_run()
        
        # Send email notification
        if send_email and new_jobs:
            self.notifier.send_job_summary(new_jobs, keywords)
        elif new_jobs:
            logger.info(f"Found {len(new_jobs)} new jobs (email disabled)")
            logger.info(f"Summary:\n{summary}")
        else:
            logger.info("No new jobs found")
            
        return {
            "jobs": all_jobs,
            "filtered_jobs": filtered_jobs,
            "new_jobs": new_jobs,
            "summary": summary
        }


async def run_job_monitor():
    """Convenience function to run job monitor."""
    monitor = IndeedJobMonitor()
    results = await monitor.run()
    return results

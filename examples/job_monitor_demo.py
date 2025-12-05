"""Simple job monitoring example."""
import asyncio
from src.orchestrator.tasks.job_board_monitor import IndeedJobMonitor


async def main():
    """Run a simple job monitoring example."""
    print("🤖 Simple Job Monitor Example\n")
    
    # Create monitor
    monitor = IndeedJobMonitor()
    
    # Run with custom parameters
    results = await monitor.run(
        keywords="python developer",
        location="remote",
        filter_criteria="Senior level positions with competitive salary",
        send_email=True
    )
    
    # Display results
    print(f"\n✓ Found {len(results['jobs'])} total jobs")
    print(f"✓ {len(results['new_jobs'])} new jobs\n")
    
    if results['new_jobs']:
        print("New Jobs:")
        for i, job in enumerate(results['new_jobs'][:5], 1):
            print(f"\n{i}. {job.get('title', 'N/A')}")
            print(f"   Company: {job.get('company', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   URL: {job.get('url', 'N/A')}")
    
    print(f"\n{results['summary']}")


if __name__ == "__main__":
    asyncio.run(main())

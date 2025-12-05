import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.notifications import EmailNotifier
from config.settings import settings

def test_notification_layout():
    """Test notification layout with different application types."""
    print("Testing notification layout...")
    
    # Mock jobs
    jobs = [
        {
            "title": "Email Application Job",
            "company": "Email Corp",
            "location": "Remote",
            "job_type": "Full-time",
            "salary": "$100k",
            "posted_date": "Today",
            "url": "https://indeed.com/job/1",
            "description": "Apply via email please.",
            "application_type": "email",
            "application_target": "jobs@emailcorp.com"
        },
        {
            "title": "Website Application Job",
            "company": "Web Corp",
            "location": "New York",
            "job_type": "Contract",
            "salary": "$80/hr",
            "posted_date": "Yesterday",
            "url": "https://indeed.com/job/2",
            "description": "Apply on our website.",
            "application_type": "url",
            "application_target": "https://webcorp.com/careers"
        },
        {
            "title": "Fallback Job (No Type)",
            "company": "Old Corp",
            "location": "London",
            "job_type": "Part-time",
            "salary": "Competitive",
            "posted_date": "2 days ago",
            "url": "https://indeed.com/job/3",
            "description": "Just a standard job.",
            "application_type": None,
            "application_target": None
        }
    ]
    
    notifier = EmailNotifier()
    
    # Force enable for testing if disabled, but print to console
    original_enabled = notifier.enabled
    notifier.enabled = False # Force console output for verification
    
    print("\n--- Generating Email Content (Console Output) ---\n")
    notifier.send_job_summary(jobs, "test keywords")
    
    print("\n--- Test Complete ---\n")

if __name__ == "__main__":
    test_notification_layout()

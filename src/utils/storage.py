"""Data storage utilities for persistence."""
import json
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from config.settings import settings
from src.utils.logger import logger


class JSONStorage:
    """Simple JSON-based storage for job data and state."""
    
    def __init__(self, filename: str = "jobs.json"):
        """Initialize storage.
        
        Args:
            filename: JSON file name
        """
        self.filepath = settings.data_dir / filename
        self.data = self._load()
        
    def _load(self) -> dict:
        """Load data from JSON file.
        
        Returns:
            Loaded data or empty dict
        """
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load {self.filepath}: {e}")
                return {}
        return {}
        
    def _save(self) -> None:
        """Save data to JSON file."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Data saved to {self.filepath}")
        except Exception as e:
            logger.error(f"Failed to save {self.filepath}: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key.
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            Value or default
        """
        return self.data.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set value by key.
        
        Args:
            key: Data key
            value: Value to store
        """
        self.data[key] = value
        self._save()
        
    def append(self, key: str, value: Any) -> None:
        """Append value to list.
        
        Args:
            key: Data key
            value: Value to append
        """
        if key not in self.data:
            self.data[key] = []
        if not isinstance(self.data[key], list):
            self.data[key] = [self.data[key]]
        self.data[key].append(value)
        self._save()
        
    def get_all(self) -> dict:
        """Get all data.
        
        Returns:
            All stored data
        """
        return self.data
        
    def clear(self) -> None:
        """Clear all data."""
        self.data = {}
        self._save()


class JobStorage:
    """Specialized storage for job listings."""
    
    def __init__(self):
        """Initialize job storage."""
        self.storage = JSONStorage("jobs.json")
        self.state_storage = JSONStorage("state.json")
        
    def save_jobs(self, jobs: list[dict], keywords: str) -> None:
        """Save job listings.
        
        Args:
            jobs: List of job dictionaries
            keywords: Search keywords used
        """
        timestamp = datetime.now().isoformat()
        
        # Save jobs with metadata
        job_data = {
            "timestamp": timestamp,
            "keywords": keywords,
            "count": len(jobs),
            "jobs": jobs
        }
        
        # Append to history
        history = self.storage.get("history", [])
        history.append(job_data)
        self.storage.set("history", history)
        
        # Update latest
        self.storage.set("latest", job_data)
        
        logger.info(f"Saved {len(jobs)} jobs to storage")
        
    def get_latest_jobs(self) -> Optional[dict]:
        """Get latest job listings.
        
        Returns:
            Latest job data or None
        """
        return self.storage.get("latest")
        
    def get_history(self) -> list[dict]:
        """Get all job history.
        
        Returns:
            List of historical job data
        """
        return self.storage.get("history", [])
        
    def get_seen_job_urls(self) -> set[str]:
        """Get set of previously seen job URLs.
        
        Returns:
            Set of job URLs
        """
        seen = self.state_storage.get("seen_urls", [])
        return set(seen)
        
    def mark_jobs_seen(self, job_urls: list[str]) -> None:
        """Mark jobs as seen.
        
        Args:
            job_urls: List of job URLs
        """
        seen = self.get_seen_job_urls()
        seen.update(job_urls)
        self.state_storage.set("seen_urls", list(seen))
        logger.debug(f"Marked {len(job_urls)} jobs as seen")
        
    def get_new_jobs(self, jobs: list[dict]) -> list[dict]:
        """Filter out previously seen jobs.
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of new (unseen) jobs
        """
        seen_urls = self.get_seen_job_urls()
        new_jobs = [job for job in jobs if job.get('url') not in seen_urls]
        logger.info(f"Found {len(new_jobs)} new jobs out of {len(jobs)} total")
        return new_jobs
        
    def update_last_run(self) -> None:
        """Update last run timestamp."""
        self.state_storage.set("last_run", datetime.now().isoformat())
        
    def get_last_run(self) -> Optional[str]:
        """Get last run timestamp.
        
        Returns:
            ISO format timestamp or None
        """
        return self.state_storage.get("last_run")

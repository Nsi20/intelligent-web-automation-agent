import json
import os

def inspect_jobs():
    file_path = 'data/jobs.json'
    if not os.path.exists(file_path):
        print("No jobs.json found.")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)
    
    jobs = data.get('latest', {}).get('jobs', [])
    print(f"Found {len(jobs)} jobs.")
    
    for i, job in enumerate(jobs[-3:]): # Print last 3
        print(f"\nJob {i+1}:")
        print(f"Title: {job.get('title')}")
        print(f"URL: {job.get('url')}")
        print(f"App Type: {job.get('application_type')}")
        print(f"App Target: {job.get('application_target')}")

if __name__ == "__main__":
    inspect_jobs()

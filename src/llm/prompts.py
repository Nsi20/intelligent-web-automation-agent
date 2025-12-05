"""Prompt templates for various automation tasks."""

# Data extraction prompts
EXTRACT_JOB_LISTINGS = """You are a job listing extraction expert. Extract job information from the provided structured text.
Each job is marked with "JOB X:", followed by its "URL:" and "HTML:".

For each job listing found, extract:
- Job Title
- Company Name
- Location
- Job Type (Full-time, Part-time, Contract, etc.)
- Salary (if available)
- Posted Date (if available)
- Job URL/Link
- Brief Description (1-2 sentences)
- Application Method (Email or Website URL)
- Application Target (The specific email address or URL to apply to)

Return the data in a clean, structured JSON format like this:
[
  {
    "title": "Senior Python Developer",
    "company": "Tech Corp",
    "location": "Remote",
    "job_type": "Full-time",
    "salary": "$120k-150k",
    "posted_date": "2 days ago",
    "url": "https://...",
    "description": "...",
    "application_type": "email",
    "application_target": "jobs@techcorp.com"
  },
  {
    "title": "Frontend Engineer",
    "company": "Web Solutions",
    "location": "New York, NY",
    "job_type": "Contract",
    "salary": "$80/hr",
    "posted_date": "1 day ago",
    "url": "https://...",
    "description": "...",
    "application_type": "url",
    "application_target": "https://websolutions.com/careers/apply/123"
  }
]

If a field is not available, use null. Be accurate and extract only what's clearly present. 
IMPORTANT: Use the "URL:" provided in the input for the "url" field. 
For application_type, infer 'email' if an email address is mentioned for applying, otherwise 'url'.
If application_type is 'url', use the same "URL:" for "application_target"."""

FILTER_JOBS_BY_CRITERIA = """You are a job filtering expert. Analyze the job listings and filter them based on the criteria.

Criteria:
{criteria}

Your task:
1. Review each job listing carefully
2. Determine if it matches the criteria
3. Return ONLY the indices (numbers) of matching jobs, comma-separated
4. Be selective - only include jobs that truly match

Example response: "1, 3, 5, 7"

If no jobs match, return "none"."""

SUMMARIZE_JOBS = """You are a job summary expert. Create a concise, well-formatted summary of the job listings.

Create a summary that includes:
1. Total number of jobs found
2. Brief overview of the types of positions
3. Highlight 3-5 most interesting/relevant opportunities with:
   - Job title and company
   - Why it's interesting
   - Key requirements or highlights

Keep the summary professional, concise, and actionable. Format it nicely for email."""

# Decision-making prompts
SHOULD_CLICK_ELEMENT = """You are a web navigation expert. Based on the context, determine if we should click this element.

Context: {context}
Goal: {goal}
Element text: {element_text}
Element type: {element_type}

Should we click this element? Respond with:
- "YES" if clicking helps achieve the goal
- "NO" if it doesn't help or might be harmful
- Brief reasoning (1 sentence)

Format: YES/NO - reasoning"""

EXTRACT_NEXT_ACTION = """You are a web automation expert. Based on the current page state and goal, determine the next action.

Current URL: {url}
Goal: {goal}
Page content summary: {page_summary}

What should be the next action? Choose from:
- NAVIGATE: Go to a different URL
- CLICK: Click an element
- FILL: Fill a form field
- EXTRACT: Extract data from page
- DONE: Goal achieved

Respond in format:
ACTION: [action type]
TARGET: [selector/url/data to extract]
REASONING: [why this action]"""

# Content analysis prompts
ANALYZE_PAGE_CONTENT = """You are a web content analyst. Analyze this page and provide insights.

Page URL: {url}
Page HTML: {html_content}

Provide:
1. Main purpose of the page
2. Key sections/elements
3. Any forms or interactive elements
4. Relevant data that can be extracted
5. Suggested next steps for automation

Be concise and focus on actionable insights."""

IS_CONTENT_RELEVANT = """You are a content relevance expert. Determine if this content is relevant to the user's interests.

User interests: {interests}
Content: {content}

Is this content relevant? Respond with:
- RELEVANT: If it matches user interests
- NOT_RELEVANT: If it doesn't match
- MAYBE: If partially relevant

Include brief reasoning (1 sentence)."""

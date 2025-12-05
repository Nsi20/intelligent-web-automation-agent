"""Email notification system."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from config.settings import settings
from src.utils.logger import logger


class EmailNotifier:
    """Email notification system using SMTP."""
    
    def __init__(self):
        """Initialize email notifier."""
        self.enabled = settings.email_enabled
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.email_from = settings.email_from or settings.smtp_user
        self.email_to = settings.email_to
        
    def send_email(self, 
                   subject: str, 
                   body: str, 
                   html: bool = True,
                   to_email: Optional[str] = None) -> bool:
        """Send email notification.
        
        Args:
            subject: Email subject
            body: Email body content
            html: Whether body is HTML (default True)
            to_email: Override recipient email
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Email disabled, printing to console instead:")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body:\n{body}")
            return False
            
        if not all([self.smtp_user, self.smtp_password, self.email_from, self.email_to]):
            logger.error("Email configuration incomplete, cannot send email")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body:\n{body}")
            return False
            
        try:
            recipient = to_email or self.email_to
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = recipient
            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            
            # Attach body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send via SMTP
            logger.info(f"Sending email to {recipient}...")
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                
            logger.info("Email sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body:\n{body}")
            return False
            
    def send_job_summary(self, jobs: list[dict], keywords: str) -> bool:
        """Send job summary email.
        
        Args:
            jobs: List of job dictionaries
            keywords: Search keywords used
            
        Returns:
            True if sent successfully
        """
        if not jobs:
            logger.info("No jobs to send, skipping email")
            return False
            
        subject = f"🔔 {len(jobs)} New Job(s) Found - {keywords}"
        
        # Create HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 20px; border-radius: 8px; }}
                .job {{ background: #f8f9fa; padding: 15px; margin: 15px 0; 
                        border-left: 4px solid #667eea; border-radius: 4px; }}
                .job-title {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
                .company {{ color: #7f8c8d; font-size: 14px; }}
                .details {{ margin: 10px 0; font-size: 14px; }}
                .label {{ font-weight: bold; color: #34495e; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; 
                          color: #7f8c8d; font-size: 12px; }}
                a {{ color: #667eea; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 New Job Opportunities Found!</h1>
                <p>Found {len(jobs)} new job(s) matching: <strong>{keywords}</strong></p>
                <p style="font-size: 14px; opacity: 0.9;">
                    {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
                </p>
            </div>
        """
        
        for i, job in enumerate(jobs, 1):
            title = job.get('title', 'N/A')
            company = job.get('company', 'N/A')
            location = job.get('location', 'N/A')
            job_type = job.get('job_type', 'N/A')
            salary = job.get('salary', 'Not specified')
            posted = job.get('posted_date', 'N/A')
            url = job.get('url', '#')
            description = job.get('description', 'No description available')
            
            application_type = job.get('application_type', 'url')
            application_target = job.get('application_target', url)
            
            # Determine action button
            if application_type == 'email' and application_target and '@' in application_target:
                action_button = f'<a href="mailto:{application_target}?subject=Application for {title}" style="background-color: #667eea; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; display: inline-block;">📧 Apply via Email</a>'
                secondary_link = f'<div style="margin-top: 8px; font-size: 12px;"><a href="{url}" target="_blank" style="color: #7f8c8d;">View Job Details on Indeed</a></div>'
            else:
                target_url = application_target if application_target else url
                action_button = f'<a href="{target_url}" target="_blank" style="background-color: #667eea; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; display: inline-block;">🌐 Apply on Website</a>'
                secondary_link = ""
            
            html_body += f"""
            <div class="job">
                <div class="job-title">{i}. {title}</div>
                <div class="company">🏢 {company}</div>
                <div class="details">
                    <span class="label">📍 Location:</span> {location} &nbsp;|&nbsp;
                    <span class="label">💼 Type:</span> {job_type} &nbsp;|&nbsp;
                    <span class="label">💰 Salary:</span> {salary}
                </div>
                <div class="details">
                    <span class="label">📅 Posted:</span> {posted}
                </div>
                <div class="details" style="margin-top: 10px;">
                    <p>{description}</p>
                </div>
                <div style="margin-top: 15px;">
                    {action_button}
                    {secondary_link}
                </div>
            </div>
            """
        
        html_body += """
            <div class="footer">
                <p>This email was automatically generated by your Intelligent Web Automation Agent.</p>
                <p>To stop receiving these notifications, update your .env configuration.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(subject, html_body, html=True)

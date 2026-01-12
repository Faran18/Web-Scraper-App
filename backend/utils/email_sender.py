# backend/utils/email_sender.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD


def send_email(to_email: str, subject: str, html_body: str):
    """
    Generic function to send HTML emails via SMTP.
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False


def send_reminder_confirmation(email: str, url: str, interval_hours: int):
    """
    Send confirmation email when a reminder is created.
    """
    subject = "🔔 Reminder Subscription Confirmed"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                margin: 20px 0;
            }}
            .url-box {{
                background: #f8f9fa;
                padding: 15px;
                border-left: 4px solid #667eea;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .url-box a {{
                color: #667eea;
                text-decoration: none;
                word-break: break-all;
            }}
            .info-list {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .info-list h3 {{
                margin-top: 0;
                color: #667eea;
            }}
            .info-list ul {{
                margin: 10px 0;
                padding-left: 20px;
            }}
            .info-list li {{
                margin: 8px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px solid #eee;
                text-align: center;
                color: #888;
                font-size: 14px;
            }}
            .badge {{
                display: inline-block;
                background: #10b981;
                color: white;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Reminder Subscription Confirmed</h1>
            </div>
            
            <div class="content">
                <p>Hello,</p>
                
                <p>You're now subscribed to updates for:</p>
                
                <div class="url-box">
                    <strong>📍 Monitored URL:</strong><br>
                    <a href="{url}" target="_blank">{url}</a>
                </div>
                
                <div class="badge">✓ Active - Checking every {interval_hours} hour{"s" if interval_hours != 1 else ""}</div>
                
                <div class="info-list">
                    <h3>What to expect:</h3>
                    <ul>
                        <li>🔔 <strong>Instant notifications</strong> when content is updated</li>
                        <li>🤖 <strong>AI-generated summaries</strong> of what changed</li>
                        <li>🔗 <strong>Direct links</strong> to view the full content</li>
                        <li>⏰ <strong>Automatic monitoring</strong> every {interval_hours} hour{"s" if interval_hours != 1 else ""}</li>
                    </ul>
                </div>
                
                <p style="margin-top: 30px;">
                    Our system will now monitor this URL and send you email notifications whenever changes are detected.
                </p>
                
                <p>
                    <strong>Note:</strong> You can manage or cancel this reminder anytime from your dashboard.
                </p>
            </div>
            
            <div class="footer">
                <p><strong>WebScraper AI Notification System</strong></p>
                <p>Thank you for using our service!</p>
                <p style="font-size: 12px; color: #aaa;">
                    This is an automated message. Please do not reply to this email.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_body)


def send_change_notification(email: str, agent_name: str, url: str, change_summary: str):
    """
    Send notification when content changes are detected.
    """
    subject = f"🔔 Content Update Detected: {agent_name}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .alert-box {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .summary-box {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #4c51bf;
            }}
            .summary-box h3 {{
                margin-top: 0;
                color: #4c51bf;
            }}
            .url-box {{
                background: #e3f2fd;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                text-align: center;
            }}
            .url-box a {{
                display: inline-block;
                background: #2196f3;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 10px;
            }}
            .url-box a:hover {{
                background: #1976d2;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px solid #eee;
                text-align: center;
                color: #888;
                font-size: 14px;
            }}
            .timestamp {{
                color: #888;
                font-size: 13px;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Content Update Detected!</h1>
            </div>
            
            <div class="content">
                <div class="alert-box">
                    <strong>⚠️ New changes detected for:</strong><br>
                    {agent_name}
                </div>
                
                <div class="summary-box">
                    <h3>📝 What Changed:</h3>
                    <p>{change_summary}</p>
                </div>
                
                <div class="url-box">
                    <p><strong>View the updated content:</strong></p>
                    <a href="{url}" target="_blank">Open Website →</a>
                </div>
                
                <p class="timestamp">
                    🕐 Detected at: {get_current_time()}
                </p>
            </div>
            
            <div class="footer">
                <p><strong>WebScraper AI Notification System</strong></p>
                <p style="font-size: 12px; color: #aaa;">
                    You're receiving this because you subscribed to updates for this URL.<br>
                    Manage your reminders from the dashboard.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_body)


def get_current_time():
    """Get current time in readable format"""
    from datetime import datetime
    return datetime.now().strftime("%B %d, %Y at %I:%M %p")


# ========================================
# DEPRECATED - Keeping for backward compatibility
# Will be removed in future versions
# ========================================

def send_subscription_confirmation(email: str, agent_name: str):
    """
    DEPRECATED: Use send_reminder_confirmation instead.
    This function is kept for backward compatibility with existing agent subscriptions.
    """
    subject = "Subscription Confirmed"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Subscription Confirmed</h2>
        <p>Hello,</p>
        <p>You're now subscribed to updates for: <strong>{agent_name}</strong></p>
        <p>You will receive email notifications whenever the monitored content changes.</p>
        <hr>
        <p style="color: #888; font-size: 12px;">WebScraper Notification System</p>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_body)

def send_password_reset_email(email: str, reset_link: str):
    subject = "🔐 Reset Your Password"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; padding: 24px; background:#f6f7fb;">
      <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:12px;padding:24px;box-shadow:0 2px 10px rgba(0,0,0,0.08);">
        <h2 style="margin:0 0 12px 0;">Reset your password</h2>
        <p style="color:#444;line-height:1.6;">
          We received a request to reset your password. Click the button below to set a new password.
        </p>
        <p style="text-align:center;margin:24px 0;">
          <a href="{reset_link}" target="_blank"
             style="display:inline-block;background:#4f46e5;color:#fff;text-decoration:none;padding:12px 18px;border-radius:10px;font-weight:bold;">
            Reset Password
          </a>
        </p>
        <p style="color:#777;font-size:13px;">
          This link expires in 30 minutes. If you didn’t request this, you can ignore this email.
        </p>
      </div>
    </body>
    </html>
    """

    return send_email(email, subject, html_body)

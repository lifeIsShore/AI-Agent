import os
import json

base_dir = "c:/AI-Agent/tests/email_cases"
os.makedirs(base_dir, exist_ok=True)

cases = {
    "urgent_deadline_tomorrow.json": {
        "subject": "Missing Submission - Action Required",
        "sender": "Prof. Davis <davis@university.edu>",
        "body": "Ahmet, your project submission is missing. If you do not submit it by tomorrow at noon, you will fail the course. Please respond immediately.",
        "unread": True
    },
    "urgent_account_problem.json": {
        "subject": "ACTION REQUIRED: Account Suspension Notice",
        "sender": "Bank Security <security@bank.com>",
        "body": "We have detected suspicious activity on your account. Your card has been temporarily frozen. Please call us immediately or click here to verify your identity within 24 hours.",
        "unread": True
    },
    "urgent_appointment_cancel.json": {
        "subject": "CANCELLATION: Dental Appointment",
        "sender": "Smile Clinic <no-reply@smileclinic.com>",
        "body": "Dear Ahmet, unfortunately, Dr. Smith is sick today and we must cancel your appointment scheduled for 2 PM this afternoon. Please call us to reschedule.",
        "unread": True
    },
    "important_university_next_week.json": {
        "subject": "Course Registration Opens Next Week",
        "sender": "Registrar <registrar@university.edu>",
        "body": "Dear Student, course registration for the upcoming semester will open next Tuesday at 8 AM. Please ensure you have cleared any holds on your account.",
        "unread": True
    },
    "important_work_request.json": {
        "subject": "Code Review Needed",
        "sender": "Alice <alice@company.com>",
        "body": "Hey Ahmet, I just opened a PR for the new caching module. Could you take a look when you have a chance? I'd like to merge it by Friday.",
        "unread": True
    },
    "important_finance.json": {
        "subject": "Your Monthly Statement is Ready",
        "sender": "Bank <statements@bank.com>",
        "body": "Your monthly statement for August is now available online. Your payment of $120.00 is due on September 15th.",
        "unread": True
    },
    "important_meeting_request.json": {
        "subject": "Sync next week?",
        "sender": "Bob <bob@startup.com>",
        "body": "Hi Ahmet, it was great meeting you yesterday. Would you be open to grabbing coffee next Wednesday to discuss potential collaborations?",
        "unread": True
    },
    "normal_linkedin_job_alert.json": {
        "subject": "EY-Parthenon Praktikant Transactions & Corporate Finance Valuation at EY-Parthenon",
        "sender": "LinkedIn Job Alerts <jobalerts-noreply@linkedin.com>",
        "body": "View the linked job post today. New jobs matching your search criteria were posted today in Frankfurt.",
        "unread": True
    },
    "normal_google_payment.json": {
        "subject": "Payment method updated for Ahmet Yagmur",
        "sender": "Google Payments <no-reply@google.com>",
        "body": "Your payment method for Google Cloud has been successfully updated.",
        "unread": True
    },
    "urgent_bank_payment_failed.json": {
        "subject": "ACTION REQUIRED: Monthly Payment Declined",
        "sender": "Bank Security <security@bank.com>",
        "body": "Your recent payment of $450.00 for your loan was declined. Please update your payment method immediately within 24 hours to avoid penalties.",
        "unread": True
    },
    "normal_amazon_delivered.json": {
        "subject": "Sipariş edildi: Miele GN Serisi",
        "sender": "Shipping <tracking@shipping.com>",
        "body": "Your package has been delivered to your doorstep.",
        "unread": True
    },
    "normal_university_announcement.json": {
        "subject": "Guest Lecture on AI",
        "sender": "CS Department <cs@university.edu>",
        "body": "Join us this Friday at 4 PM in the main hall for a guest lecture on the future of Agentic AI. Attendance is optional but highly recommended.",
        "unread": True
    },
    "normal_library_hours.json": {
        "subject": "Library hours changing",
        "sender": "Library <library@university.edu>",
        "body": "Starting next month, the library will close at 10 PM on weekends instead of midnight.",
        "unread": True
    },
    "normal_general_info.json": {
        "subject": "Package Delivered",
        "sender": "Shipping <tracking@shipping.com>",
        "body": "Your package has been delivered to the front desk. You can pick it up anytime during business hours.",
        "unread": True
    },
    "normal_dinner.json": {
        "subject": "Dinner plans",
        "sender": "Sarah <sarah@friends.com>",
        "body": "Hey, just confirming we are still on for dinner this Friday. Let me know what time you're free!",
        "unread": True
    },
    "irrelevant_newsletter_1.json": {
        "subject": "Top 10 Python Tricks",
        "sender": "Code Weekly <newsletter@codeweekly.com>",
        "body": "Check out this week's top Python tricks! From list comprehensions to generators... click here to view in browser. Unsubscribe at any time.",
        "unread": True
    },
    "irrelevant_advertisement.json": {
        "subject": "50% OFF All Shoes!",
        "sender": "Shoe Store <marketing@shoestore.com>",
        "body": "Our biggest sale of the year is here. Get 50% off all sneakers. Shop now! To unsubscribe, click here.",
        "unread": True
    },
    "irrelevant_promo.json": {
        "subject": "Get a free trial of Premium",
        "sender": "SaaS Platform <noreply@saas.com>",
        "body": "You're invited to try our Premium tier for 30 days free. Upgrade your productivity today.",
        "unread": True
    },
    "irrelevant_automated.json": {
        "subject": "New login on Chrome",
        "sender": "Security <security-noreply@service.com>",
        "body": "We noticed a new login to your account from Chrome on Windows. If this was you, you don't need to do anything.",
        "unread": True
    },
    "borderline_room_cancel.json": {
        "subject": "Room Booking Cancelled",
        "sender": "Facilities <noreply@university.edu>",
        "body": "Your study room booking for tomorrow at 10 AM has been cancelled due to maintenance. We apologize for the inconvenience.",
        "unread": True
    },
    "borderline_library_close_early.json": {
        "subject": "Library closing early tomorrow",
        "sender": "Library <library@university.edu>",
        "body": "Please be advised that the main library will close at 3 PM tomorrow due to a staff event.",
        "unread": True
    },
    "borderline_newsletter_urgent_subject.json": {
        "subject": "URGENT: Don't miss this sale!",
        "sender": "Marketing <marketing@store.com>",
        "body": "This is your last chance! The sale ends in 24 hours. Unsubscribe here.",
        "unread": True
    }
}

for filename, content in cases.items():
    with open(os.path.join(base_dir, filename), 'w') as f:
        json.dump(content, f, indent=2)

print(f"Generated {len(cases)} test cases including real-world inspired examples.")

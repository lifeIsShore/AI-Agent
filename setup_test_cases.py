import os
import json

base_dir = "c:/AI-Agent/tests/email_cases"
os.makedirs(base_dir, exist_ok=True)

cases = {
    "urgent.json": {
        "id": "1",
        "thread_id": "t1",
        "sender": "Prof. Smith <smith@university.edu>",
        "subject": "URGENT: Thesis Proposal Missing",
        "date": "Tue, 01 Sep 2026 09:00:00 +0000",
        "snippet": "Ahmet, we have not received your proposal...",
        "body": "Ahmet, we have not received your thesis proposal. The final deadline is today at 5 PM. If you do not submit it, you will fail the semester. Please reply immediately.",
        "unread": True
    },
    "university.json": {
        "id": "2",
        "thread_id": "t2",
        "sender": "University Administration <admin@university.edu>",
        "subject": "Campus Library Hours Update",
        "date": "Tue, 01 Sep 2026 10:00:00 +0000",
        "snippet": "Starting next week, library hours...",
        "body": "Dear Students, Starting next week, the campus library will be open 24/7 during the exam period. Good luck with your studies!",
        "unread": True
    },
    "newsletter.json": {
        "id": "3",
        "thread_id": "t3",
        "sender": "Tech Daily <news@techdaily.com>",
        "subject": "Top 10 AI Tools This Week",
        "date": "Tue, 01 Sep 2026 11:00:00 +0000",
        "snippet": "Discover the latest tools in AI...",
        "body": "Here are the top 10 AI tools you need to know about this week. Click here to read the full article...",
        "unread": True
    },
    "normal.json": {
        "id": "4",
        "thread_id": "t4",
        "sender": "John Doe <john.doe@example.com>",
        "subject": "Dinner on Friday?",
        "date": "Tue, 01 Sep 2026 12:00:00 +0000",
        "snippet": "Hey Ahmet, are we still on for dinner?",
        "body": "Hey Ahmet, just checking in to see if we are still on for dinner this Friday. Let me know what time works for you.",
        "unread": True
    }
}

for filename, content in cases.items():
    with open(os.path.join(base_dir, filename), 'w') as f:
        json.dump(content, f, indent=2)

print("Test cases created successfully.")

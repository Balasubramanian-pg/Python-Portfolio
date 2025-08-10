# Email Automation Scripts

## Overview
This repository contains Python scripts for automating common email-related tasks.  
The primary goal is to **streamline email management** by automatically fetching, parsing, extracting, and storing email data in structured formats such as CSV.

These scripts are ideal for:
- Businesses processing large volumes of inbound emails
- Automated data extraction from recurring email reports
- Archiving and indexing email content for analysis

---

## Features
1. **Fetching Emails from an IMAP Server**
   - Connect securely to an IMAP server using credentials.
   - Retrieve emails from specific folders (e.g., INBOX, Sent, Custom labels).
   - Filter by date range, sender, or subject keywords.

2. **Parsing Email Content**
   - Extract plain text and HTML content.
   - Handle attachments (PDF, CSV, images).
   - Normalize encoding for consistent text processing.

3. **Extracting Specific Information**
   - Identify key data using **regular expressions** or keyword matching.
   - Extract fields such as:
     - Order IDs
     - Tracking numbers
     - Invoice amounts
     - Dates

4. **Processing and Storing Data**
   - Clean and validate extracted values.
   - Save structured data to CSV for further processing.
   - Optionally export to JSON or database (MySQL, SQLite, etc.).

---

## Example Python Functions

### 1. Connecting to an IMAP Server
```python
import imaplib

def connect_imap(server, email, password):
    """Connect to IMAP server and login."""
    mail = imaplib.IMAP4_SSL(server)
    mail.login(email, password)
    return mail

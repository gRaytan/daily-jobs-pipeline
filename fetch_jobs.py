
import os
import requests
from bs4 import BeautifulSoup
import openai
import smtplib
from email.mime.text import MIMEText

# === Env ===
EMAIL_FROM = os.environ['EMAIL_FROM']
EMAIL_TO = os.environ['EMAIL_TO']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

openai.api_key = OPENAI_API_KEY

# === Career Page URLs ===
COMPANY_URLS = {
    "Acme": "https://acme.com/careers",
    "Globex": "https://globex.com/jobs",
    # Add more as needed
}

def fetch_html(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def extract_text_snippets(html):
    soup = BeautifulSoup(html, "html.parser")
    text_blocks = soup.find_all(["h1", "h2", "h3", "p", "a", "li"])
    text = "\n".join(el.get_text(strip=True) for el in text_blocks)
    return text[:8000]  # Limit to fit LLM context window

def extract_jobs_from_llm(company, text_snippet):
    prompt = f"""
You are an expert at parsing job postings from career sites.
Given the text snippet below from {company}'s career page, extract job openings as JSON.

Each job should include:
- title
- location (if available)
- job_url (if available)

Only return a JSON list like:
[
  {{"title": "...", "location": "...", "job_url": "..."}},
  ...
]

Text:
{text_snippet}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        content = response['choices'][0]['message']['content']
        return eval(content) if content.startswith('[') else []
    except Exception as e:
        print(f"LLM parsing failed for {company}: {e}")
        return []

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        smtp.send_message(msg)

def main():
    all_jobs_output = []

    for company, url in COMPANY_URLS.items():
        print(f"Processing {company}...")
        html = fetch_html(url)
        if not html:
            continue

        snippet = extract_text_snippets(html)
        jobs = extract_jobs_from_llm(company, snippet)

        if jobs:
            job_lines = [f"- {job['title']} ({job.get('location', 'N/A')})\n  {job.get('job_url', 'N/A')}" for job in jobs]
            section = f"🧑‍💼 {company} — {len(jobs)} job(s):\n" + "\n".join(job_lines)
            all_jobs_output.append(section)

    if all_jobs_output:
        final_body = "\n\n---\n\n".join(all_jobs_output)
        send_email("📢 New Job Openings (via LLM)", final_body)
    else:
        print("No jobs found.")

if __name__ == "__main__":
    main()


def fetch_html(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def extract_text_snippets(html):
    soup = BeautifulSoup(html, "html.parser")
    text_blocks = soup.find_all(["h1", "h2", "h3", "p", "a", "li"])
    text = "\n".join(el.get_text(strip=True) for el in text_blocks)
    return text[:8000]  # Limit to fit LLM context window

def extract_jobs_from_llm(company, text_snippet):
    prompt = f"""
You are an expert at parsing job postings from career sites.
Given the text snippet below from {company}'s career page, extract job openings as JSON.

Each job should include:
- title
- location (if available)
- job_url (if available)

Only return a JSON list like:
[
  {{"title": "...", "location": "...", "job_url": "..."}},
  ...
]

Text:
{text_snippet}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        content = response['choices'][0]['message']['content']
        return eval(content) if content.startswith('[') else []
    except Exception as e:
        print(f"LLM parsing failed for {company}: {e}")
        return []

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        smtp.send_message(msg)

def main():
    all_jobs_output = []

    for company, url in COMPANY_URLS.items():
        print(f"Processing {company}...")
        html = fetch_html(url)
        if not html:
            continue

        snippet = extract_text_snippets(html)
        jobs = extract_jobs_from_llm(company, snippet)

        if jobs:
            job_lines = [f"- {job['title']} ({job.get('location', 'N/A')})\n  {job.get('job_url', 'N/A')}" for job in jobs]
            section = f"🧑‍💼 {company} — {len(jobs)} job(s):\n" + "\n".join(job_lines)
            all_jobs_output.append(section)

    if all_jobs_output:
        final_body = "\n\n---\n\n".join(all_jobs_output)
        send_email("📢 New Job Openings (via LLM)", final_body)
    else:
        print("No jobs found.")

if __name__ == "__main__":
    main()

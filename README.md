# Hiredge AI

<p align="center">
  <img src="/static/favicon.svg" alt="Hiredge Logo" width="100" />
</p>

#### Video Demo: [Watch here](<URL HERE>)

---

## Description

**Hiredge AI** is an AI-powered resume analysis tool built with Django and Python. It uses the OpenAI API to analyze uploaded resumes and provide actionable, personalized feedback to improve them. The goal is to assist job seekers in refining their resumes for better job search outcomes.

This project was created out of a genuine need to help individuals struggling with resume clarity, structure, or impact. With job markets becoming increasingly competitive, having a tool that automates resume enhancement can make a real difference in landing interviews.

Hiredge AI was planned from the beginning to be both useful and easy to use—providing feedback within seconds after uploading a resume.

---

## Quick Start

1. **Clone the repository:**

```bash
git clone https://github.com/MrCrowNFT/hiredge-ai
cd hiredge-ai
```

2. **Create and activate a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install the dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

Create a `.env` file using the `.env.example` as a template and fill in your configuration.

5. **Apply migrations and run the development server:**

```bash
python3 manage.py migrate
python3 manage.py runserver
```

6. **Visit the app:**

Open your browser and go to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Tech Stack

- Python 3
- Django
- HTML
- Tailwind CSS
- PyPDF2
- OpenAI API

---

## .gitignore Note

Make sure your `.gitignore` file excludes:

```txt
__pycache__/
*.log
media/
db.sqlite3
.env
venv/
```

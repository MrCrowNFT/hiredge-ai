# Hiredge AI

<p align="center">
  <img src="/static/favicon.svg" alt="Hiredge Logo" width="100" />
</p>

### Video Demo: [Watch here](<https://youtu.be/oM4ka7EPDGo>)

---

### Description

**Hiredge AI** is an AI-powered resume analysis tool built with Django and Python. It uses the OpenAI API to analyze uploaded resumes and provide actionable, personalized feedback to improve them. The goal is to assist job seekers in refining their resumes for better job search outcomes.

This project was created out of a genuine need to help individuals struggling with resume clarity, structure, or impact. With job markets becoming increasingly competitive, having a tool that automates resume enhancement can make a real difference in landing interviews.

Hiredge AI was planned from the beginning to be both useful and easy to use—providing feedback within seconds after uploading a resume.

---

### Quick Start

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

### Clean up

**Management command for cleaning up old temporary files**

```sh
python3 manage.py cleanup_files --days=1
```

### Tech Stack

- Python 3
- Django
- HTML
- Tailwind CSS
- PyPDF2
- OpenAI API

---


### Live Project

- [Hiredge Ai (Render)](https://hiredge-ai.onrender.com/)

> Note: The project is hosted on Render free tier. It may take a few seconds to wake up when idle.

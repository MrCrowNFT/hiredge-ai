from openai import OpenAI

client = OpenAI(api_key="")  # Add API key

"""Enhance a resume using LLM, optionally tailoring it to a job description."""
def improve_resume(resume_text, job_desc=""):
    messages = [
        {"role": "system", "content": "You are a professional recruiter and HR manager. Improve resumes to make them more appealing to recruiters."},
        {"role": "user", "content": f"Improve this resume:\n\n{resume_text}"},
    ]
    
    if job_desc:
        messages.append({"role": "user", "content": f"Tailor it for this job description:\n\n{job_desc}"})

    response = client.chat.completions.create(
        model="",  
        messages=messages,
        max_tokens=1000,
    )

    return response.choices[0].message.content 
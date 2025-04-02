import openai

openai.api_key =""#add api key

"""Here we use LLM to enhance a resume, optionally with a job description for tailored resumes"""
def improve_resume(resume_text, job_desc):
    prompt= f"""
    Improve this resume to make it more appealing to recruters

    Resume: 
    {resume_text}

    Job Description: 
    Tailor the resume for this job description
    {job_desc}

    Return only the improved resume.
    """
    response = openai.ChatCompletion.create(
        model="",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response["choices"][0]["message"]["content"]

    
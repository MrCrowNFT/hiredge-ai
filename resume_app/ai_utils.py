from openai import OpenAI
import os
import time
from django.conf import settings

# Get API key from environment 
api_key = os.environ.get("OPENAI_API_KEY", "")
model_name = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

client = OpenAI(api_key=api_key)

def improve_resume(resume_text, job_desc=""):
    """Enhance a resume using OpenAI, optionally tailoring it to a job description."""
    try:
        system_message = """You are a professional recruiter and HR manager with expertise in resume optimization. 
        Improve the provided resume to make it more appealing, professional, and impactful.
        
        Guidelines:
        - Make language more action-oriented and results-focused
        - Ensure consistent formatting and proper structure
        - Highlight relevant skills and achievements
        - Use industry-standard terminology
        - Do not invent new information
        - Do not change dates, job titles, or employers
        - Maintain the original resume sections but improve their content
        - Keep the overall length similar to the original
        """
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Here is the resume to improve:\n\n{resume_text}"},
        ]
        
        if job_desc and job_desc.strip():
            job_instruction = f"""
            Additionally, tailor this resume for the following job description:
            
            {job_desc}
            
            Guidelines for tailoring:
            - Emphasize relevant skills and experiences that match the job requirements
            - Use similar keywords and terminology from the job description
            - Prioritize achievements that would be most impressive for this specific role
            - Do not fabricate experience or skills not mentioned in the original resume
            """
            messages.append({"role": "user", "content": job_instruction})
        
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.5,  
            max_tokens=4000,
        )
        
        improved_resume = response.choices[0].message.content
        return improved_resume
        
    except Exception as e:
        # Log the error 
        print(f"Error in improve_resume: {str(e)}")
        
        # Fallback to a basic improvement if API call fails
        return basic_improve_resume(resume_text, job_desc)

def basic_improve_resume(resume_text, job_desc=""):
    """Fallback function if the API call fails."""
    import re
    
    # Basic improvements
    improved = resume_text
    improved = re.sub(r'Responsible for', 'Successfully managed', improved)
    improved = re.sub(r'Worked (on|with)', 'Collaborated on', improved)
    improved = re.sub(r'Helped (with|to)', 'Contributed to', improved)
    
    # Add a note explaining the situation
    improved = "Note: Some basic improvements were made, but full AI enhancement is currently unavailable.\n\n" + improved
    
    return improved
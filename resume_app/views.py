from django.shortcuts import render, HttpResponse
from django.core.files.storage import FileSystemStorage
from .file_utils import extract_text
from .ai_utils import improve_resume


def upload_resume(request):
    if request.method == "POST":
        if "resume" not in request.FILES:
            return render(request, "upload.html", {"error": "No file was uploaded"})
            
        uploaded_file = request.FILES["resume"]  # Extract the uploaded file object with name attribute "resume"
        
        # Check file extension
        if not (uploaded_file.name.endswith('.pdf') or uploaded_file.name.endswith('.docx')):
            return render(request, "upload.html", {"error": "Only PDF and DOCX files are supported"})
        
        fs = FileSystemStorage()  # For handling file uploads
        filename = fs.save(uploaded_file.name, uploaded_file)  # Saves the uploaded file in the media storage directory
        file_path = fs.path(filename)  # Get absolute path

        try:
            extracted_text = extract_text(file_path)
            return render(request, "resume_preview.html", {"resume_text": extracted_text})
        except Exception as e:
            # Clean up the file if extraction fails
            fs.delete(filename)
            return render(request, "upload.html", {"error": f"Error processing file: {str(e)}"})
    
    # If no file has been uploaded or method is GET, render upload form
    return render(request, "upload.html")


def enhance_resume(request):
    if request.method == "POST":
        resume_text = request.POST["resume_text"]
        job_desc = request.POST.get("job_desc", "")

        improved_resume = improve_resume(resume_text, job_desc)
        return render(request, "resume_preview.html", {"resume_text": improved_resume})

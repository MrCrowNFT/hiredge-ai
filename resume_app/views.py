from django.shortcuts import render, HttpResponse
from django.core.files.storage import FileSystemStorage
from .file_utils import extract_text
from .ai_utils import improve_resume
import mimetypes


def upload_resume(request):
    if request.method == "POST":
        if "resume" not in request.FILES:
            return render(request, "upload.html", {"error": "No file was uploaded"})

        uploaded_file = request.FILES["resume"]

        # Validate file type using MIME type
        valid_mime_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        file_mime_type, _ = mimetypes.guess_type(uploaded_file.name)

        if file_mime_type not in valid_mime_types:
            return render(request, "upload.html", {"error": "Only PDF and DOCX files are supported"})

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        try:
            extracted_text = extract_text(file_path)
            return render(request, "resume_preview.html", {"resume_text": extracted_text})
        except Exception as e:
            fs.delete(filename)  # Delete file if extraction fails
            return render(request, "upload.html", {"error": f"Error processing file: {str(e)}"})

    return render(request, "upload.html")


def enhance_resume(request):
    if request.method == "POST":
        resume_text = request.POST.get("resume_text", "").strip()
        job_desc = request.POST.get("job_desc", "").strip()

        if not resume_text:
            return render(request, "resume_preview.html", {"error": "Resume text is required"})

        improved_resume = improve_resume(resume_text, job_desc)
        return render(request, "resume_preview.html", {"resume_text": improved_resume})

    return HttpResponse(status=405)  
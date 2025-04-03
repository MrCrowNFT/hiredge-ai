from django.shortcuts import render, HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from .file_utils import extract_text, create_document
from .ai_utils import improve_resume
import mimetypes
import os
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages


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
            # Store the original file info in session
            request.session['original_file'] = {
                'path': file_path,
                'name': uploaded_file.name,
                'mime_type': file_mime_type
            }
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

        try:
            improved_resume = improve_resume(resume_text, job_desc)
            # Store the improved text in session
            request.session['improved_resume'] = improved_resume
            return render(request, "improved_resume.html", {
                "resume_text": improved_resume,
                "original_text": resume_text,
                "job_desc": job_desc
            })
        except Exception as e:
            return render(request, "resume_preview.html", {
                "resume_text": resume_text,
                "job_desc": job_desc,
                "error": f"Error improving resume: {str(e)}"
            })

    return HttpResponse(status=405)


def download_resume(request):
    if request.method == "GET":
        improved_resume = request.session.get('improved_resume')
        original_file = request.session.get('original_file')
        
        if not improved_resume or not original_file:
            messages.error(request, "No improved resume available for download")
            return render(request, "upload.html")
            
        try:
            # Create a new document with the improved text
            output_format = request.GET.get('format', 'pdf')
            file_path = create_document(improved_resume, output_format)
            
            # Prepare file for download
            with open(file_path, 'rb') as file:
                response = FileResponse(
                    file,
                    content_type='application/pdf' if output_format == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                response['Content-Disposition'] = f'attachment; filename="improved_{os.path.basename(original_file["name"])}"'
                return response
                
        except Exception as e:
            messages.error(request, f"Error creating document: {str(e)}")
            return render(request, "improved_resume.html", {"resume_text": improved_resume, "error": str(e)})
            
    return HttpResponse(status=405)
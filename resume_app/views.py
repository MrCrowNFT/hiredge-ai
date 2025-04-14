from django.shortcuts import render, HttpResponse, redirect
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.contrib import messages
from django.conf import settings
import mimetypes
import os
import uuid
import time
from .file_utils import extract_text, create_document
from .ai_utils import improve_resume


def upload_resume(request):
    """Handle resume file upload and text extraction."""
    if request.method == "POST":
        if "resume" not in request.FILES:
            return render(request, "upload.html", {"error": "No file was uploaded"})

        uploaded_file = request.FILES["resume"]
        
        # Enhanced file validation
        # Check file extension explicitly
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in ['.pdf', '.docx']:
            return render(request, "upload.html", {"error": "Only PDF and DOCX files are supported"})
            
        # Validate MIME type
        valid_mime_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        file_mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        
        if file_mime_type not in valid_mime_types:
            return render(request, "upload.html", {"error": "Invalid file format detected"})

        # Enhanced size validation with clear message
        max_size_mb = 5
        if uploaded_file.size > max_size_mb * 1024 * 1024:
            return render(request, "upload.html", {"error": f"File size exceeds {max_size_mb}MB limit"})
            
        # Add validation for file content (prevent empty files)
        if uploaded_file.size == 0:
            return render(request, "upload.html", {"error": "Empty files are not allowed"})
        # Save file with a unique name to prevent overwriting
        fs = FileSystemStorage()
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        filename = fs.save(unique_filename, uploaded_file)
        file_path = fs.path(filename)

        try:
            extracted_text = extract_text(file_path)
            if not extracted_text.strip():
                fs.delete(filename)
                return render(request, "upload.html", {"error": "Could not extract text from file. Please ensure the file contains text content."})
            
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
    """Process resume text with AI and display improved version."""
    if request.method == "POST":
        resume_text = request.POST.get("resume_text", "").strip()
        job_desc = request.POST.get("job_desc", "").strip()

        # Enhanced text validation
        if not resume_text:
            return render(request, "resume_preview.html", {"error": "Resume text is required"})
            
        # Validate text length
        if len(resume_text) < 100:
            return render(request, "resume_preview.html", 
                {"error": "Resume text is too short. Please provide a complete resume.", 
                 "resume_text": resume_text, 
                 "job_desc": job_desc})
                 
        if len(resume_text) > 10000:  # Set reasonable maximum
            return render(request, "resume_preview.html", 
                {"error": "Resume text exceeds maximum length (10,000 characters).", 
                 "resume_text": resume_text[:10000], 
                 "job_desc": job_desc})
                 
        # Job description validation (optional field)
        if job_desc and len(job_desc) > 5000:
            return render(request, "resume_preview.html", 
                {"error": "Job description exceeds maximum length (5,000 characters).", 
                 "resume_text": resume_text, 
                 "job_desc": job_desc[:5000]})
        try:
            # Process with AI
            start_time = time.time()
            improved_resume = improve_resume(resume_text, job_desc)
            processing_time = time.time() - start_time
            
            # Store the improved text in session
            request.session['improved_resume'] = improved_resume
            request.session['job_desc'] = job_desc
            
            # Add processing time for analytics
            context = {
                "resume_text": improved_resume,
                "original_text": resume_text,
                "job_desc": job_desc,
                "processing_time": round(processing_time, 2)
            }
            
            return render(request, "improved_resume.html", context)
        except Exception as e:
            error_msg = f"Error improving resume: {str(e)}"
            if "api_key" in str(e).lower():
                error_msg = "API configuration error. Please contact the administrator."
                
            return render(request, "resume_preview.html", {
                "resume_text": resume_text,
                "job_desc": job_desc,
                "error": error_msg
            })

    return redirect("upload_resume")


def download_resume(request):
    """Generate and serve downloadable resume file."""
    if request.method == "GET":
        improved_resume = request.session.get('improved_resume')
        original_file = request.session.get('original_file')
        
        if not improved_resume:
            messages.error(request, "No improved resume available for download")
            return redirect("upload_resume")
            
        try:
            # Create a new document with the improved text
            output_format = request.GET.get('format', 'pdf').lower()
            if output_format not in ['pdf', 'docx']:
                output_format = 'pdf'  # Default to PDF if invalid format
                
            file_path = create_document(improved_resume, output_format)
            
            # Prepare file for download
            with open(file_path, 'rb') as file:
                content_type = 'application/pdf' if output_format == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                response = FileResponse(file, content_type=content_type)
                
                # Generate a filename
                if original_file and 'name' in original_file:
                    original_name = os.path.splitext(original_file['name'])[0]
                    filename = f"improved_{original_name}.{output_format}"
                else:
                    filename = f"improved_resume.{output_format}"
                    
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
                
        except Exception as e:
            messages.error(request, f"Error creating document: {str(e)}")
            return render(request, "improved_resume.html", {
                "resume_text": improved_resume, 
                "error": f"Download failed: {str(e)}"
            })
            
    return redirect("upload_resume")
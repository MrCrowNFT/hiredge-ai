from django.shortcuts import render, HttpResponse
from django.core.files.storage import FileSystemStorage

def upload_resume(request):
    if request.method == POST:
        uploaded_file = request.FILES["resume"] #extract the uploaded file object with name attribute "resume"
        fs = FileSystemStorage()# for handling file uploads
        filename = fs.save(uploaded_file.name, uploaded_file)#Saves the uploaded file in the media storage directory
        file_path = fs.path(filename)#get absolute path

        extracted_text = 
        return render(request, "resume_preview.html", {"resume_text": extracted_text})
    #if no file has been uploaded, render upload form
    return render(request, "upload.html")

#this one will be called when the user submits, 
#can not submit if the user hasn't upload resume
def enhance_resume(request):
    return 

import os
import tempfile
from unittest import mock
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from openai import OpenAI
from openai._exceptions import RateLimitError, AuthenticationError, APIError, APIConnectionError

# temporary media directory for testing
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ResumeViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test PDF file
        self.pdf_content = b'%PDF-1.4 test pdf content'
        self.pdf_file = SimpleUploadedFile(
            "resume.pdf",
            self.pdf_content,
            content_type="application/pdf"
        )
        
        # Create test DOCX file
        self.docx_content = b'mock docx content'
        self.docx_file = SimpleUploadedFile(
            "resume.docx",
            self.docx_content,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        # Create invalid file
        self.invalid_file = SimpleUploadedFile(
            "resume.txt",
            b"This is a text file",
            content_type="text/plain"
        )
        
        # Mock resume text
        self.sample_resume_text = "John Doe\nSoftware Engineer\n10 years experience"
        self.sample_job_desc = "Looking for a Software Engineer with Python experience"
        self.improved_resume_text = "IMPROVED: John Doe\nSenior Software Engineer\nPython Expert"

    def tearDown(self):
        # Clean up any files created during the test
        for root, dirs, files in os.walk(TEMP_MEDIA_ROOT):
            for filename in files:
                os.remove(os.path.join(root, filename))

    # Upload Resume Tests

    @mock.patch('resume_app.views.extract_text') 
    @mock.patch('resume_app.views.rate_limit')
    def test_upload_resume_docx_success(self, mock_rate_limit, mock_extract_text):
        # Disable rate limiting for this test
        mock_rate_limit.return_value = lambda f: f
        
        # Configure the mock
        mock_extract_text.return_value = self.sample_resume_text
        
        # Test uploading a DOCX file
        response = self.client.post(reverse('upload_resume'), {'resume': self.docx_file})
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resume_preview.html')
        self.assertContains(response, self.sample_resume_text)
        mock_extract_text.assert_called_once()

    def test_upload_resume_no_file(self):
        # Test uploading with no file
        response = self.client.post(reverse('upload_resume'), {})
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload.html')
        self.assertContains(response, "No file was uploaded")

    def test_upload_resume_invalid_extension(self):
        # Test uploading a file with invalid extension
        response = self.client.post(reverse('upload_resume'), {'resume': self.invalid_file})
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload.html')
        self.assertContains(response, "Only PDF and DOCX files are supported")

    def test_upload_resume_empty_file(self):
        # Test uploading an empty file
        empty_file = SimpleUploadedFile(
            "empty.pdf",
            b'',
            content_type="application/pdf"
        )
        response = self.client.post(reverse('upload_resume'), {'resume': empty_file})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload.html')
        self.assertContains(response, "Empty files are not allowed")

    def test_upload_resume_file_too_large(self):
        # Create a file that's larger than the limit (5MB)
        large_content = b'x' * (5 * 1024 * 1024 + 1)
        large_file = SimpleUploadedFile(
            "large.pdf",
            large_content,
            content_type="application/pdf"
        )
        
        response = self.client.post(reverse('upload_resume'), {'resume': large_file})
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload.html')
        self.assertContains(response, "File size exceeds 5MB limit")

    @mock.patch('resume_app.views.extract_text')
    def test_upload_resume_extraction_failure(self, mock_extract_text):
        # Configure the mock to return empty text
        mock_extract_text.return_value = ""
        
        response = self.client.post(reverse('upload_resume'), {'resume': self.pdf_file})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload.html')
        self.assertContains(response, "Could not extract text from file")

    @mock.patch('resume_app.views.extract_text')
    def test_upload_resume_extraction_exception(self, mock_extract_text):
        # Configure the mock to raise an exception
        mock_extract_text.side_effect = Exception("Extraction error")
        
        response = self.client.post(reverse('upload_resume'), {'resume': self.pdf_file})
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload.html')
        self.assertContains(response, "Error processing file: Extraction error")

    def test_upload_resume_get_request(self):
        # Test GET request to upload_resume
        response = self.client.get(reverse('upload_resume'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload.html')

    # Enhance Resume Tests
   
    def test_enhance_resume_no_text(self):
        # Test enhancing with no resume text
        response = self.client.post(reverse('enhance_resume'), {
            'resume_text': '',
            'job_desc': self.sample_job_desc
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resume_preview.html')
        self.assertContains(response, "Resume text is required")

    
    @mock.patch('resume_app.views.improve_resume')
    @mock.patch('resume_app.views.rate_limit')
    def test_enhance_resume_api_connection_error(self, mock_rate_limit, mock_improve_resume):
        # Disable rate limiting for this test
        mock_rate_limit.return_value = lambda f: f
        
        # Create a proper APIConnectionError with required parameters
        error = APIConnectionError(
            message="Connection error",
            request=mock.MagicMock()
        )
        mock_improve_resume.side_effect = error
        
        response = self.client.post(reverse('enhance_resume'), {
            'resume_text': self.sample_resume_text,
            'job_desc': self.sample_job_desc
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resume_preview.html')
        self.assertContains(response, "Unable to connect to AI service")

    @mock.patch('resume_app.views.improve_resume')
    @mock.patch('resume_app.views.rate_limit')
    def test_enhance_resume_generic_exception(self, mock_rate_limit, mock_improve_resume):
        # Disable rate limiting for this test
        mock_rate_limit.return_value = lambda f: f
        
        # Configure the mock to raise a generic Exception
        mock_improve_resume.side_effect = Exception("Unexpected error")
        
        response = self.client.post(reverse('enhance_resume'), {
            'resume_text': self.sample_resume_text,
            'job_desc': self.sample_job_desc
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resume_preview.html')
        self.assertContains(response, "unexpected error occurred")

    def test_enhance_resume_get_request(self):
        # Test GET request to enhance_resume
        response = self.client.get(reverse('enhance_resume'))
        
        self.assertEqual(response.status_code, 302)  # Redirect expected
        self.assertRedirects(response, reverse('upload_resume'))

    # Download Resume Tests
    @mock.patch('resume_app.views.create_document')
    def test_download_resume_pdf_success(self, mock_create_document):
        # Create a temp file for the mock to return
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.write(b'Mock PDF content')
        temp_file.close()
        
        # Configure the mock
        mock_create_document.return_value = temp_file.name
        
        # Set up session data
        session = self.client.session
        session['improved_resume'] = self.improved_resume_text
        session['original_file'] = {
            'path': '/fake/path/resume.pdf',
            'name': 'resume.pdf',
            'mime_type': 'application/pdf'
        }
        session.save()
        
        # Test downloading a PDF
        response = self.client.get(reverse('download_resume') + '?format=pdf')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="improved_resume.pdf"', response['Content-Disposition'])
        
        # Clean up
        os.unlink(temp_file.name)

    @mock.patch('resume_app.views.create_document')
    def test_download_resume_docx_success(self, mock_create_document):
        # Create a temp file for the mock to return
        temp_file = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        temp_file.write(b'Mock DOCX content')
        temp_file.close()
        
        # Configure the mock
        mock_create_document.return_value = temp_file.name
        
        # Set up session data
        session = self.client.session
        session['improved_resume'] = self.improved_resume_text
        session['original_file'] = {
            'path': '/fake/path/resume.docx',
            'name': 'resume.docx',
            'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        session.save()
        
        # Test downloading a DOCX
        response = self.client.get(reverse('download_resume') + '?format=docx')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        self.assertIn('attachment; filename="improved_resume.docx"', response['Content-Disposition'])
        
        # Clean up
        os.unlink(temp_file.name)

    def test_download_resume_no_improved_text(self):
        # Test downloading without improved resume in session
        session = self.client.session
        if 'improved_resume' in session:
            del session['improved_resume']
        session.save()
        
        response = self.client.get(reverse('download_resume'))
        
        # Assertions
        self.assertEqual(response.status_code, 302)  # Redirect expected
        self.assertRedirects(response, reverse('upload_resume'))

    @mock.patch('resume_app.views.create_document')
    def test_download_resume_invalid_format(self, mock_create_document):
        # Create a temp file for the mock to return
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.write(b'Mock PDF content')
        temp_file.close()
        
        # Configure the mock
        mock_create_document.return_value = temp_file.name
        
        # Set up session data
        session = self.client.session
        session['improved_resume'] = self.improved_resume_text
        session.save()
        
        # Test downloading with invalid format
        response = self.client.get(reverse('download_resume') + '?format=invalid')
        
        # Should default to PDF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Clean up
        os.unlink(temp_file.name)

    @mock.patch('resume_app.views.create_document')
    def test_download_resume_document_creation_error(self, mock_create_document):
        # Configure the mock to raise an exception
        mock_create_document.side_effect = Exception("Document creation error")
        
        # Set up session data
        session = self.client.session
        session['improved_resume'] = self.improved_resume_text
        session.save()
        
        response = self.client.get(reverse('download_resume'))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'improved_resume.html')
        self.assertContains(response, "Download failed")

   
    @mock.patch('resume_app.views.improve_resume')
    def test_enhance_resume_rate_limiting(self, mock_improve_resume):
        # Configure mock
        mock_improve_resume.return_value = self.improved_resume_text
        
        # First request should succeed
        response1 = self.client.post(reverse('enhance_resume'), {
            'resume_text': self.sample_resume_text,
            'job_desc': self.sample_job_desc
        })
        self.assertEqual(response1.status_code, 200)
        
        # Subsequent requests should be rate limited
        response2 = self.client.post(reverse('enhance_resume'), {
            'resume_text': self.sample_resume_text,
            'job_desc': self.sample_job_desc
        })
        self.assertEqual(response2.status_code, 429)  # Too Many Requests
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up old temporary files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Delete files older than this many days',
        )

    def handle(self, *args, **options):
        days = options['days']
        seconds = days * 24 * 60 * 60
        now = time.time()
        
        # Directories to clean
        directories = [
            os.path.join(settings.MEDIA_ROOT),
            os.path.join(settings.MEDIA_ROOT, 'improved_resumes'),
        ]
        
        total_removed = 0
        
        for directory in directories:
            if not os.path.exists(directory):
                continue
                
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                # Skip directories and non-resume files
                if os.path.isdir(file_path):
                    continue
                    
                # Check if file is a resume file (adjust patterns as needed)
                if not any(pattern in filename for pattern in ['resume', 'improved', '.pdf', '.docx']):
                    continue
                
                # Check file age
                file_age = now - os.path.getmtime(file_path)
                
                if file_age > seconds:
                    try:
                        os.remove(file_path)
                        total_removed += 1
                        logger.info(f"Removed old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error removing {file_path}: {str(e)}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully removed {total_removed} old files')
        )
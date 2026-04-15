import os
import time
import logging
from django.core.management.base import BaseCommand
from contacts.models import Contact, ProcessedFile
from django.db import transaction
from tqdm import tqdm

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='import_contacts.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Command(BaseCommand):
    help = "Ultimate import command with progress, ETA, resume, error handling, and logging."

    def add_arguments(self, parser):
        parser.add_argument(
            '--folder',
            type=str,
            help="Optional: specify a base folder (e.g., C:\\Users\\sunday\\Documents\\boite de pandor)"
        )

    def handle(self, *args, **options):
        base_folder = options['folder'] or r"C:\Users\sunday\Documents\boite de pandor"
        prefixes = ["070", "080", "081", "090", "091"]

        for prefix in prefixes:
            folder_path = os.path.join(base_folder, prefix)
            if not os.path.exists(folder_path):
                self.stdout.write(self.style.WARNING(f"Folder not found: {folder_path}"))
                logger.warning(f"Folder not found: {folder_path}")
                continue

            # Scan files first
            all_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".txt")])
            files_to_import = [f for f in all_files if not ProcessedFile.objects.filter(file_name=f).exists()]

            total_files = len(files_to_import)
            if total_files == 0:
                self.stdout.write(self.style.SUCCESS(f"All files already imported in folder {prefix}."))
                continue

            self.stdout.write(self.style.SUCCESS(f"Importing folder {prefix} ({total_files} files)."))
            logger.info(f"Start importing {total_files} files from {folder_path}")

            start_time = time.time()

            for idx, file_name in enumerate(files_to_import, start=1):
                file_path = os.path.join(folder_path, file_name)
                try:
                    self.import_file(file_path)
                    ProcessedFile.objects.create(file_name=file_name)
                    logger.info(f"Imported file: {file_name}")
                except Exception as e:
                    logger.error(f"Failed to import {file_name}: {e}")
                    continue  # skip to next file

                # ETA calculation
                elapsed = time.time() - start_time
                avg_time = elapsed / idx
                remaining = total_files - idx
                eta_seconds = avg_time * remaining
                eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
                progress = (idx / total_files) * 100

                self.stdout.write(f"[{progress:.2f}%] Imported {idx}/{total_files} files | ETA: {eta_str}", ending="\r")

            self.stdout.write(self.style.SUCCESS(f"\nCompleted import for folder {prefix}"))
            logger.info(f"Completed folder {prefix}")

    def import_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        contacts = [Contact(phone_number=line) for line in lines]

        batch_size = 1000
        for i in range(0, len(contacts), batch_size):
            batch = contacts[i:i + batch_size]
            with transaction.atomic():
                Contact.objects.bulk_create(batch, ignore_conflicts=True)

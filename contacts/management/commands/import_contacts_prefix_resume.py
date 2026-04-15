from django.core.management.base import BaseCommand
from contacts.models import Contact, ProcessedFile
from django.db import transaction
import os
from tqdm import tqdm

class Command(BaseCommand):
    help = "Import contacts for a given prefix with resume support"

    def add_arguments(self, parser):
        parser.add_argument("--prefix", required=True, help="Phone number prefix")
        parser.add_argument("--base-folder", default="", help="Folder containing contact files")

    def handle(self, *args, **options):
        prefix = options["prefix"]
        base_folder = options["base_folder"]
        folder_path = os.path.join(base_folder, prefix)

        if not os.path.exists(folder_path):
            self.stdout.write(self.style.ERROR(f"Folder not found: {folder_path}"))
            return

        # Load processed files
        processed_filenames = set(
            ProcessedFile.objects.using(f"contacts_{prefix}")
            .values_list("filename", flat=True)
        )

        # All files in folder
        all_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".txt")])

        # Filter out processed files
        files_to_process = [f for f in all_files if f not in processed_filenames]

        if not files_to_process:
            self.stdout.write(self.style.SUCCESS(f"✔ No new files to import for prefix {prefix}."))
            return

        for file_name in tqdm(files_to_process, desc=f"Importing {prefix} contacts", unit="file"):
            file_path = os.path.join(folder_path, file_name)

            # Import file
            self.import_file(file_path, prefix)

            # Mark file as processed
            ProcessedFile.objects.using(f"contacts_{prefix}").create(
                filename=file_name, 
                prefix=prefix
            )

        self.stdout.write(self.style.SUCCESS(f"✅ Completed import for prefix {prefix}."))

    def import_file(self, file_path, prefix):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        contacts = [Contact(phone_number=line) for line in lines]

        batch_size = 1000
        for i in tqdm(range(0, len(contacts), batch_size), 
                      desc=f"Importing contacts in {os.path.basename(file_path)}",
                      leave=False):
            batch = contacts[i:i + batch_size]
            with transaction.atomic(using=f"contacts_{prefix}"):
                Contact.objects.using(f"contacts_{prefix}").bulk_create(
                    batch, 
                    ignore_conflicts=True
                )

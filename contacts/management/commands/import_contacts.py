import os
from django.core.management.base import BaseCommand
from contacts.models import Contact

# Path to the folder that contains the 070 subfolder
BASE_FOLDER = r"C:\Users\sunday\Documents\boite de pandor"

class Command(BaseCommand):
    help = "Import contacts only from the 070 folder for testing"

    def handle(self, *args, **kwargs):
        prefix = "070"  # We only process this folder
        folder_path = os.path.join(BASE_FOLDER, prefix)

        if not os.path.exists(folder_path):
            self.stdout.write(self.style.ERROR(f"Folder not found: {folder_path}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Processing folder: {folder_path}"))

        for file_name in os.listdir(folder_path):
            if file_name.endswith(".txt"):
                file_path = os.path.join(folder_path, file_name)
                self.import_file(file_path)

        self.stdout.write(self.style.SUCCESS("✅ Finished importing 070 contacts."))

    def import_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]

        contacts = [Contact(phone_number=line) for line in lines]

        batch_size = 1000
        total_imported = 0

        for i in range(0, len(contacts), batch_size):
            batch = contacts[i:i + batch_size]
            Contact.objects.bulk_create(batch, ignore_conflicts=True)
            total_imported += len(batch)

        self.stdout.write(self.style.SUCCESS(f"Imported {total_imported} contacts from {file_path}"))

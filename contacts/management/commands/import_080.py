import os
from django.core.management.base import BaseCommand
from contacts.models import Contact

BASE_FOLDER = r"C:\Users\sunday\Documents\boite de pandor"

class Command(BaseCommand):
    help = "Import all contacts from the 080 folder"

    def handle(self, *args, **kwargs):
        folder_path = os.path.join(BASE_FOLDER, "080")
        if not os.path.exists(folder_path):
            self.stdout.write(self.style.WARNING(f"Folder not found: {folder_path}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Processing folder: {folder_path}"))

        for file_name in os.listdir(folder_path):
            if file_name.endswith(".txt"):
                file_path = os.path.join(folder_path, file_name)
                self.import_file(file_path)

    def import_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        contacts = [Contact(phone_number=line) for line in lines]

        batch_size = 1000
        for i in range(0, len(contacts), batch_size):
            Contact.objects.bulk_create(contacts[i:i + batch_size], ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f"Imported {len(lines)} contacts from {file_path}"))

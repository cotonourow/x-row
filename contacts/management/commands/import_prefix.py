import os
import time
from django.core.management.base import BaseCommand
from contacts.models import Contact

class Command(BaseCommand):
    help = "Import contacts from a folder based on prefix (e.g. 080, 081)"

    def add_arguments(self, parser):
        parser.add_argument("prefix", type=str, help="Phone number prefix folder to import (e.g. 080)")

    def handle(self, *args, **options):
        prefix = options["prefix"]
        base_folder = rf"C:\Users\sunday\Documents\boite de pandor\{prefix}"

        if not os.path.exists(base_folder):
            self.stdout.write(self.style.ERROR(f"Folder does NOT exist: {base_folder}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Processing folder: {base_folder}"))

        files = sorted(
            [f for f in os.listdir(base_folder) if f.endswith(".txt")],
            key=lambda x: int("".join(filter(str.isdigit, x)) or 0)
        )

        total_files = len(files)
        if total_files == 0:
            self.stdout.write(self.style.ERROR("No .txt files found in folder."))
            return

        start_time = time.time()
        processed_files = 0

        for file_name in files:
            file_path = os.path.join(base_folder, file_name)

            # Skip files already processed
            processed_count = Contact.objects.filter(file_name=file_name).count()
            if processed_count > 0:
                processed_files += 1
                continue

            self.import_file(file_path, file_name)

            processed_files += 1

            # Progress %
            progress = (processed_files / total_files) * 100

            elapsed = time.time() - start_time
            avg_time = elapsed / processed_files
            remaining_files = total_files - processed_files
            eta_seconds = avg_time * remaining_files
            eta_min = eta_seconds / 60

            self.stdout.write(
                self.style.SUCCESS(
                    f"[{progress:.2f}%] Imported {file_name} "
                    f"({processed_files}/{total_files}) | ETA: {eta_min:.1f} min"
                )
            )

        self.stdout.write(self.style.SUCCESS("✔ IMPORT COMPLETED SUCCESSFULLY ✔"))

    def import_file(self, path, file_name):
        batch = []
        with open(path, "r") as f:
            for line in f:
                num = line.strip()
                if num:
                    batch.append(Contact(phone_number=num, file_name=file_name))

        Contact.objects.bulk_create(batch, ignore_conflicts=True)

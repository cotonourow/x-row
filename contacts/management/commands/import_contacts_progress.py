import os
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from contacts.models import Contact


class Command(BaseCommand):
    help = "Import contacts with progress bar and ETA"

    def add_arguments(self, parser):
        parser.add_argument(
            "--folder",
            type=str,
            required=True,
            help="Folder containing phone number files",
        )

    def handle(self, *args, **options):
        folder = options["folder"]

        if not os.path.exists(folder):
            self.stdout.write(self.style.ERROR(f"Folder not found: {folder}"))
            return

        # Get all .txt files
        files = sorted(
            [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".txt")]
        )

        total_files = len(files)
        if total_files == 0:
            self.stdout.write(self.style.ERROR("No .txt files found in folder."))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {total_files} files."))

        start_time = time.time()

        for index, file_path in enumerate(files, start=1):
            file_start = time.time()

            self.import_file(file_path)
            self.show_progress(index, total_files, start_time)

        self.stdout.write(self.style.SUCCESS("\n✔ DONE — All contacts imported."))

    def import_file(self, file_path):
        batch = []
        with open(file_path, "r") as file:
            for line in file:
                phone = line.strip()
                if phone:
                    batch.append(Contact(phone_number=phone))

        if batch:
            with transaction.atomic():
                Contact.objects.bulk_create(batch, ignore_conflicts=True)

    def show_progress(self, current, total, start_time):
        percent = (current / total) * 100

        elapsed = time.time() - start_time
        speed = current / elapsed  # files per second
        remaining_files = total - current

        if speed > 0:
            eta = remaining_files / speed
        else:
            eta = 0

        bar_length = 30
        filled = int(bar_length * percent / 100)
        bar = "█" * filled + "-" * (bar_length - filled)

        print(
            f"\r[{bar}] {percent:5.1f}%  "
            f"{current}/{total} files  "
            f"ETA: {eta:6.1f}s  "
            f"Speed: {speed:4.2f} files/s",
            end="",
            flush=True,
        )

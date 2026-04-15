import os
import sqlite3
from django.core.management.base import BaseCommand
from contacts.models import Contact
from django.db import transaction, connections

CHUNK_SIZE = 50000  # how many rows to migrate per batch

class Command(BaseCommand):
    help = "Migrate a SQLite contacts DB to PostgreSQL"

    def add_arguments(self, parser):
        parser.add_argument(
            '--sqlite',
            type=str,
            help='Path to the SQLite database'
        )
        parser.add_argument(
            '--pg_db',
            type=str,
            help='Target PostgreSQL database alias'
        )

    def handle(self, *args, **options):
        sqlite_path = options['sqlite']
        pg_db_alias = options['pg_db']

        if not sqlite_path or not pg_db_alias:
            self.stdout.write(self.style.ERROR("Both --sqlite and --pg_db are required"))
            return

        if not os.path.exists(sqlite_path):
            self.stdout.write(self.style.ERROR(f"SQLite file {sqlite_path} does not exist"))
            return

        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        cursor = sqlite_conn.cursor()

        # Count total rows
        cursor.execute("SELECT COUNT(*) FROM contacts_contact")
        total_rows = cursor.fetchone()[0]
        self.stdout.write(f"Total rows to migrate: {total_rows}")

        # Find last migrated ID in PostgreSQL to resume
        with connections[pg_db_alias].cursor() as pg_cursor:
            pg_cursor.execute("SELECT MAX(id) FROM contacts_contact")
            last_id = pg_cursor.fetchone()[0] or 0

        self.stdout.write(f"Resuming from ID: {last_id + 1}")

        # Migrate in chunks
        offset = last_id
        while offset < total_rows:
            cursor.execute(
                "SELECT * FROM contacts_contact WHERE id > ? ORDER BY id LIMIT ?",
                (offset, CHUNK_SIZE)
            )
            rows = cursor.fetchall()
            if not rows:
                break

            with transaction.atomic(using=pg_db_alias):
                for row in rows:
                    Contact.objects.using(pg_db_alias).update_or_create(
                        id=row['id'],
                        defaults={
                            'name': row['name'],
                            'phone_number': row['phone_number'],
                            'email': row['email'],
                            'created_at': row['created_at'],
                        }
                    )

            offset = rows[-1]['id']
            percent = (offset / total_rows) * 100
            self.stdout.write(f"Migrated up to ID {offset} ({percent:.2f}%)")

        self.stdout.write(self.style.SUCCESS("Migration complete!"))
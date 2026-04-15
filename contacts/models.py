from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Keep your existing database routing if you have it
        pass

    def __str__(self):
        return f"{self.name} - {self.phone_number}"


class ProcessedFile(models.Model):
    filename = models.CharField(max_length=512, unique=True)
    prefix = models.CharField(max_length=10)
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class Worker(models.Model):
    SKILL_CHOICES = [
        ('engineer', 'Engineer'),
        ('electrician', 'Electrician'),
        ('painter', 'Painter'),
        ('mason', 'Bricklayer / Mason'),
        ('screeder', 'Screeder'),
        ('pop_installer', 'POP Installer'),
        ('welder', 'Welder'),
        ('tiler', 'Tiler'),
        ('carpenter', 'Carpenter'),
        ('furniture_maker', 'Furniture Maker'),
        ('plumber', 'Plumber'),
        ('iron_bender', 'Iron Bender'),
        ('fabricator', 'Fabricator'),
        ('window_hood_installer', 'Window Hood Installer'),
        ('concrete_specialist', 'Concrete Specialist'),
        ('scaffolder', 'Scaffolder'),
        ('borehole_specialist', 'Borehole Specialist'),
        ('plaster_board', 'Plaster Board'),
        ('interlock', 'Interlock'),
        ('aluminium_work', 'Aluminium Work'),
        ('site_manager', 'Site Manager'),
        ('site_supervisor', 'Site Supervisor'),
        ('labourer', 'Labourer'),
    ]

    name = models.CharField(max_length=100)
    skill = models.CharField(max_length=50, choices=SKILL_CHOICES)
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, db_index=True)  # Added index for faster search
    experience_years = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Years of experience in this skill"
    )
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text="Rating from 0.0 to 5.0"
    )
    is_available = models.BooleanField(default=True, help_text="Is worker currently available?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', 'skill', 'name']  # Highest rated first
        indexes = [
            models.Index(fields=['skill', 'location']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_skill_display()}) - ⭐{self.rating}"

    def save(self, *args, **kwargs):
        # Auto-normalize phone before saving
        self.phone = self.normalize_phone(self.phone)
        super().save(*args, **kwargs)

    @staticmethod
    def normalize_phone(phone):
        """Normalize phone number for consistent storage"""
        if not phone:
            return phone
        phone = str(phone).strip()
        # Remove spaces, dashes, parentheses, dots
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "")
        # Remove +234 and replace with 0
        if phone.startswith("+234"):
            phone = "0" + phone[4:]
        # Remove 234 prefix and replace with 0 if length is 13
        elif phone.startswith("234") and len(phone) == 13:
            phone = "0" + phone[3:]
        return phone
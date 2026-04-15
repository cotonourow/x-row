from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0003_alter_worker_options_contact_created_at_and_more'),
    ]

    operations = [
        # Add missing fields to Worker
        migrations.AddField(
            model_name='worker',
            name='experience_years',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='worker',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=2),
        ),
        migrations.AddField(
            model_name='worker',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='worker',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
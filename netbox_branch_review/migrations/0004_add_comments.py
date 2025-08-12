from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("netbox_branch_review", "0003_merge_0002_add_description_0002_repair_ticket_column"),
    ]

    operations = [
        migrations.AddField(
            model_name="changerequest",
            name="comments",
            field=models.TextField(blank=True),
        ),
    ]

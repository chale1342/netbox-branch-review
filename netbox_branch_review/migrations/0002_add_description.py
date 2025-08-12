from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('netbox_branch_review', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='changerequest',
            name='description',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]

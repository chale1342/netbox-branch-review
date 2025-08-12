from django.db import migrations

SQL_ADD_TICKET = """
ALTER TABLE netbox_branch_review_changerequest
    ADD COLUMN IF NOT EXISTS ticket varchar(100) NOT NULL DEFAULT '';
ALTER TABLE netbox_branch_review_changerequest
    ALTER COLUMN ticket DROP DEFAULT;
"""

class Migration(migrations.Migration):
    dependencies = [
        ("netbox_branch_review", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(SQL_ADD_TICKET, reverse_sql="""ALTER TABLE netbox_branch_review_changerequest DROP COLUMN IF EXISTS ticket;"""),
    ]

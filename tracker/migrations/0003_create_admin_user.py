import os
from django.db import migrations

def create_admin(apps, schema_editor):
    from django.contrib.auth import get_user_model
    U = get_user_model()
    password = os.environ.get('ADMIN_PASSWORD', 'mvrs12345')
    if not U.objects.filter(username='admin').exists():
        U.objects.create_superuser('admin', '', password)
    else:
        u = U.objects.get(username='admin')
        u.set_password(password)
        u.save()

class Migration(migrations.Migration):
    dependencies = [
        ('tracker', '0002_seed_vendors'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]
    operations = [migrations.RunPython(create_admin, migrations.RunPython.noop)]

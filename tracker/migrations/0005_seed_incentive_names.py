from django.db import migrations


def seed_incentive_names(apps, schema_editor):
    IncentiveName = apps.get_model('tracker', 'IncentiveName')
    for i, name in enumerate(['Rakesh', 'Lokesh', 'Siva']):
        IncentiveName.objects.get_or_create(name=name, defaults={'order': i})


class Migration(migrations.Migration):
    dependencies = [
        ('tracker', '0004_new_fields'),
    ]
    operations = [
        migrations.RunPython(seed_incentive_names, migrations.RunPython.noop),
    ]

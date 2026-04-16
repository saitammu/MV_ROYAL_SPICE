from django.db import migrations

FIXED_STAFF = [
    ('Lokesh',         'waiter',   1100),
    ('Siphou',         'helper',    600),
    ('Khaleem',        'cook',     1200),
    ('Sibou',          'helper',    333),
    ('Siva',           'cook',      899),
    ('Banty',          'waiter',    733),
    ('Khislam',        'helper',    633),
    ('Khana',          'helper',    300),
    ('Toofan',         'waiter',    640),
    ('Rakesh',         'waiter',    799),
    ('Fillu',          'cleaner',   400),
    ('Anusha',         'cleaner',   300),
    ('Priya',          'cashier',   333),
    ('Mori Aunty Morning', 'cook',  800),
    ('Evening Aunty Morning', 'cook', 800),
    ('Security',       'security',  370),
]


def seed_staff(apps, schema_editor):
    Staff = apps.get_model('tracker', 'Staff')
    for name, role, salary in FIXED_STAFF:
        obj, created = Staff.objects.get_or_create(name=name, defaults={
            'role': role,
            'fixed_salary': salary,
            'is_active': True,
        })
        if not created:
            obj.fixed_salary = salary
            obj.role = role
            obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0006_staff_attendance_updates'),
    ]

    operations = [
        migrations.RunPython(seed_staff, migrations.RunPython.noop),
    ]

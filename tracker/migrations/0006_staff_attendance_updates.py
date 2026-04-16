from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0005_seed_incentive_names'),
    ]

    operations = [
        # Add fixed_salary to Staff
        migrations.AddField(
            model_name='staff',
            name='fixed_salary',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        # Add attendance_status to StaffPayment
        migrations.AddField(
            model_name='staffpayment',
            name='attendance_status',
            field=models.CharField(
                choices=[('full_day', 'Full Day'), ('half_day', 'Half Day'), ('absent', 'Absent')],
                default='full_day', max_length=20),
        ),
        # Add staff_submitted flag
        migrations.AddField(
            model_name='staffpayment',
            name='staff_submitted',
            field=models.BooleanField(default=False),
        ),
        # Expand role choices
        migrations.AlterField(
            model_name='staff',
            name='role',
            field=models.CharField(
                choices=[('cook', 'Cook'), ('waiter', 'Waiter'), ('cleaner', 'Cleaner'),
                         ('cashier', 'Cashier'), ('manager', 'Manager'),
                         ('security', 'Security'), ('helper', 'Helper'), ('other', 'Other')],
                default='other', max_length=50),
        ),
    ]

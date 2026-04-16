import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('last_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='tracker.vendor')),
            ],
            options={'ordering': ['name'], 'unique_together': {('vendor', 'name')}},
        ),
        migrations.CreateModel(
            name='DailyEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('weight', models.DecimalField(decimal_places=3, max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subcategory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='tracker.subcategory')),
            ],
            options={'ordering': ['-date']},
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('role', models.CharField(
                    choices=[('cook','Cook'),('waiter','Waiter'),('cleaner','Cleaner'),
                             ('cashier','Cashier'),('manager','Manager'),('other','Other')],
                    default='other', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='DailyFinance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('card', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('upi', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('swiggy_zomato', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('other_expenses', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('other_expenses_note', models.CharField(blank=True, max_length=300)),
                ('carry_forward', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('is_closed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-date']},
        ),
        migrations.CreateModel(
            name='StaffPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_present', models.BooleanField(default=True)),
                ('salary', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('incentive', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('finance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_payments', to='tracker.dailyfinance')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.staff')),
            ],
            options={'ordering': ['staff__name'], 'unique_together': {('finance', 'staff')}},
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0007_seed_fixed_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyfinance',
            name='swiggy_zomato',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]

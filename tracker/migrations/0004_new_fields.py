from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0003_create_admin_user'),
    ]

    operations = [
        # Add new DailyFinance fields
        migrations.AddField(
            model_name='dailyfinance',
            name='zomato',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='dailyfinance',
            name='swiggy',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='dailyfinance',
            name='card_expense',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        # IncentiveName model
        migrations.CreateModel(
            name='IncentiveName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['order', 'name']},
        ),
        # DailyIncentive model
        migrations.CreateModel(
            name='DailyIncentive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('finance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incentives', to='tracker.dailyfinance')),
                ('incentive_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.incentivename')),
            ],
            options={'unique_together': {('finance', 'incentive_name')}},
        ),
    ]

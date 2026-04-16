from django.db import models


class Vendor(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class SubCategory(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=200)
    last_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.vendor.name} - {self.name}"

    class Meta:
        unique_together = ['vendor', 'name']
        ordering = ['name']


class DailyEntry(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='entries')
    date = models.DateField()
    weight = models.DecimalField(max_digits=10, decimal_places=3)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total = float(self.weight) * float(self.price)
        self.subcategory.last_price = self.price
        self.subcategory.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.subcategory} - {self.weight}kg @ {self.price}"

    class Meta:
        ordering = ['-date']


class IncentiveName(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name']


class DailyFinance(models.Model):
    date = models.DateField(unique=True)
    cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    card = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    upi = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    zomato = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    swiggy = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    swiggy_zomato = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    card_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_expenses_note = models.CharField(max_length=300, blank=True)
    carry_forward = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_earnings(self):
        return float(self.cash)

    @property
    def total_vendor_expense(self):
        from django.db.models import Sum
        result = DailyEntry.objects.filter(date=self.date).aggregate(t=Sum('total'))['t']
        return float(result or 0)

    @property
    def total_staff_cost(self):
        result = 0
        for sp in StaffPayment.objects.filter(finance=self):
            result += sp.total
        return result

    @property
    def total_incentives(self):
        from django.db.models import Sum
        result = DailyIncentive.objects.filter(finance=self).aggregate(t=Sum('amount'))['t']
        return float(result or 0)

    @property
    def total_deductions(self):
        return (self.total_vendor_expense + self.total_staff_cost +
                float(self.other_expenses) + float(self.card_expense) +
                self.total_incentives)

    @property
    def net_profit(self):
        return float(self.carry_forward) + self.total_earnings - self.total_deductions

    def __str__(self):
        return f"Finance {self.date}"

    class Meta:
        ordering = ['-date']


class DailyIncentive(models.Model):
    finance = models.ForeignKey(DailyFinance, on_delete=models.CASCADE, related_name='incentives')
    incentive_name = models.ForeignKey(IncentiveName, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ['finance', 'incentive_name']

    def __str__(self):
        return f"{self.finance.date} - {self.incentive_name.name}: {self.amount}"


class Staff(models.Model):
    ROLE_CHOICES = [
        ('cook', 'Cook'),
        ('waiter', 'Waiter'),
        ('cleaner', 'Cleaner'),
        ('cashier', 'Cashier'),
        ('manager', 'Manager'),
        ('security', 'Security'),
        ('helper', 'Helper'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='other')
    fixed_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class StaffPayment(models.Model):
    ATTENDANCE_CHOICES = [
        ('full_day', 'Full Day'),
        ('half_day', 'Half Day'),
        ('absent', 'Absent'),
    ]
    finance = models.ForeignKey(DailyFinance, on_delete=models.CASCADE, related_name='staff_payments')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    attendance_status = models.CharField(
        max_length=20, choices=ATTENDANCE_CHOICES, default='full_day')
    is_present = models.BooleanField(default=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    incentive = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    staff_submitted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.is_present = self.attendance_status != 'absent'
        super().save(*args, **kwargs)

    @property
    def effective_salary(self):
        if self.attendance_status == 'absent':
            return 0
        elif self.attendance_status == 'half_day':
            return round(float(self.salary) / 2, 2)
        return float(self.salary)

    @property
    def total(self):
        return self.effective_salary + float(self.incentive)

    class Meta:
        unique_together = ['finance', 'staff']
        ordering = ['staff__name']

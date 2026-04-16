import csv
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum
from django.conf import settings
from .models import (Vendor, SubCategory, DailyEntry, DailyFinance,
                     Staff, StaffPayment, IncentiveName, DailyIncentive)


# ── Auth ──────────────────────────────────────────────────────────
def login_view(request):
    error = ''
    if request.method == 'POST':
        role     = request.POST.get('role', 'admin')
        password = request.POST.get('password', '')
        if role == 'staff':
            if password == settings.STAFF_PASSWORD:
                request.session['staff_auth'] = True
                return redirect('staff_attendance')
            error = 'Wrong staff password'
        else:
            user = authenticate(request, username='admin', password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
            error = 'Wrong admin password'
    return render(request, 'tracker/login.html', {'error': error})

def logout_view(request):
    logout(request)
    request.session.pop('staff_auth', None)
    return redirect('login')


# ── Dashboard ─────────────────────────────────────────────────────
@login_required
def dashboard(request):
    today = date.today()

    selected_date_str = request.GET.get('date', str(today))
    try:
        selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = today

    finance, created = DailyFinance.objects.get_or_create(date=selected_date)

    if created and selected_date == today:
        yesterday = today - timedelta(days=1)
        try:
            yf = DailyFinance.objects.get(date=yesterday)
            profit = yf.net_profit
            finance.carry_forward = profit if profit > 0 else 0
            finance.save()
        except DailyFinance.DoesNotExist:
            pass

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'reset_day':
            finance.cash = 0; finance.card = 0; finance.upi = 0
            finance.zomato = 0; finance.swiggy = 0; finance.swiggy_zomato = 0
            finance.card_expense = 0; finance.other_expenses = 0
            finance.other_expenses_note = ''
            finance.save()
            DailyIncentive.objects.filter(finance=finance).update(amount=0)
            return redirect(f'/dashboard/?date={selected_date}')

        elif action == 'save_earnings':
            finance.cash = request.POST.get('cash', 0) or 0
            finance.save()

        elif action == 'save_zomato':
            finance.zomato = request.POST.get('zomato', 0) or 0
            finance.save()

        elif action == 'save_swiggy':
            finance.swiggy = request.POST.get('swiggy', 0) or 0
            finance.save()

        elif action == 'save_expenses':
            finance.other_expenses      = request.POST.get('other_expenses', 0) or 0
            finance.other_expenses_note = request.POST.get('other_expenses_note', '')
            finance.card_expense        = request.POST.get('card_expense', 0) or 0
            finance.save()

        elif action == 'save_incentives':
            incentive_names = IncentiveName.objects.all()
            for iname in incentive_names:
                amt = request.POST.get(f'incentive_{iname.id}', 0) or 0
                obj, _ = DailyIncentive.objects.get_or_create(
                    finance=finance, incentive_name=iname)
                obj.amount = amt
                obj.save()

        elif action == 'add_incentive_name':
            name = request.POST.get('new_incentive_name', '').strip()
            if name:
                max_order = IncentiveName.objects.count()
                IncentiveName.objects.get_or_create(name=name, defaults={'order': max_order})

        elif action == 'delete_incentive_name':
            iid = request.POST.get('incentive_name_id')
            IncentiveName.objects.filter(id=iid).delete()

        elif action == 'rename_incentive_name':
            iid  = request.POST.get('incentive_name_id')
            name = request.POST.get('new_name', '').strip()
            if name and iid:
                IncentiveName.objects.filter(id=iid).update(name=name)

        return redirect(f'/dashboard/?date={selected_date}')

    incentive_names = IncentiveName.objects.all()
    incentive_data = []
    for iname in incentive_names:
        inc, _ = DailyIncentive.objects.get_or_create(finance=finance, incentive_name=iname)
        incentive_data.append({'name': iname, 'entry': inc})

    return render(request, 'tracker/dashboard.html', {
        'finance': finance,
        'today': today,
        'selected_date': selected_date,
        'is_today': selected_date == today,
        'incentive_data': incentive_data,
    })


# ── Zomato Report ─────────────────────────────────────────────────
@login_required
def zomato_report(request):
    entries = DailyFinance.objects.exclude(zomato=0).order_by('-date')
    total = entries.aggregate(t=Sum('zomato'))['t'] or 0
    return render(request, 'tracker/zomato_report.html', {
        'entries': entries, 'total': total, 'platform': 'Zomato'})


# ── Swiggy Report ─────────────────────────────────────────────────
@login_required
def swiggy_report(request):
    entries = DailyFinance.objects.exclude(swiggy=0).order_by('-date')
    total = entries.aggregate(t=Sum('swiggy'))['t'] or 0
    return render(request, 'tracker/swiggy_report.html', {
        'entries': entries, 'total': total, 'platform': 'Swiggy'})


# ── CSV for platforms ─────────────────────────────────────────────
@login_required
def export_platform_csv(request):
    platform = request.GET.get('platform', 'zomato').lower()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="mvrs_{platform}_report.csv"'
    w = csv.writer(response)
    w.writerow([f'{platform.upper()} REPORT'])
    w.writerow(['Date', 'Amount (₹)'])
    field = 'zomato' if platform == 'zomato' else 'swiggy'
    qs = DailyFinance.objects.exclude(**{field: 0}).order_by('-date')
    total = 0
    for f in qs:
        amt = float(getattr(f, field))
        w.writerow([str(f.date), amt])
        total += amt
    w.writerow(['', ''])
    w.writerow(['TOTAL', total])
    return response


# ── Staff Attendance — ADMIN PAGE ─────────────────────────────────
def attendance(request):
    is_admin      = request.user.is_authenticated
    is_staff_auth = request.session.get('staff_auth', False)
    if not is_admin and not is_staff_auth:
        return redirect('login')

    today = date.today()
    finance, _ = DailyFinance.objects.get_or_create(date=today)

    # Ensure all active staff have a payment record; pre-fill salary from fixed_salary
    for s in Staff.objects.filter(is_active=True):
        p, created = StaffPayment.objects.get_or_create(finance=finance, staff=s)
        if created and float(s.fixed_salary) > 0 and float(p.salary) == 0:
            p.salary = s.fixed_salary
            p.save()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_staff' and is_admin:
            name   = request.POST.get('name', '').strip()
            role   = request.POST.get('role', 'other')
            salary = request.POST.get('fixed_salary', 0) or 0
            if name:
                s, _ = Staff.objects.get_or_create(name=name, defaults={
                    'role': role, 'fixed_salary': salary})
                s.is_active = True
                if not _:
                    s.role = role
                    s.fixed_salary = salary
                s.save()
                p, created = StaffPayment.objects.get_or_create(finance=finance, staff=s)
                if float(salary) > 0 and float(p.salary) == 0:
                    p.salary = salary
                    p.save()

        elif action == 'edit_staff' and is_admin:
            staff_id = request.POST.get('staff_id')
            role     = request.POST.get('role', 'other')
            salary   = request.POST.get('fixed_salary', 0) or 0
            Staff.objects.filter(id=staff_id).update(role=role, fixed_salary=salary)
            # Also update today's payment salary if unchanged from old fixed
            try:
                s = Staff.objects.get(id=staff_id)
                p = StaffPayment.objects.get(finance=finance, staff=s)
                p.salary = salary
                p.save()
            except (Staff.DoesNotExist, StaffPayment.DoesNotExist):
                pass

        elif action == 'save_payments' and is_admin:
            for key in request.POST:
                if key.startswith('salary_'):
                    pid = key.split('_', 1)[1]
                    try:
                        p = StaffPayment.objects.get(id=pid, finance=finance)
                        att = request.POST.get(f'attendance_{pid}', 'full_day')
                        p.attendance_status = att
                        p.salary     = request.POST.get(f'salary_{pid}') or 0
                        p.incentive  = request.POST.get(f'incentive_{pid}') or 0
                        p.save()
                    except StaffPayment.DoesNotExist:
                        pass

        elif action == 'remove_staff' and is_admin:
            Staff.objects.filter(id=request.POST.get('staff_id')).update(is_active=False)

        return redirect('attendance')

    payments     = StaffPayment.objects.filter(finance=finance).select_related('staff')
    total_salary = sum(p.effective_salary for p in payments)
    total_inc    = sum(float(p.incentive) for p in payments if p.is_present)

    return render(request, 'tracker/attendance.html', {
        'payments': payments,
        'finance': finance,
        'today': today,
        'total_salary': total_salary,
        'total_incentive': total_inc,
        'total_staff_cost': total_salary + total_inc,
        'roles': Staff.ROLE_CHOICES,
        'is_admin': is_admin,
    })


# ── Staff Self-Attendance (Staff Login Page) ──────────────────────
def staff_attendance(request):
    if not request.session.get('staff_auth', False):
        return redirect('login')

    today = date.today()
    finance, _ = DailyFinance.objects.get_or_create(date=today)

    # Ensure all active staff have records
    for s in Staff.objects.filter(is_active=True):
        p, created = StaffPayment.objects.get_or_create(finance=finance, staff=s)
        if created and float(s.fixed_salary) > 0 and float(p.salary) == 0:
            p.salary = s.fixed_salary
            p.save()

    success_msg = ''
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'staff_mark_attendance':
            staff_id = request.POST.get('staff_id')
            att      = request.POST.get('attendance_status', 'full_day')
            try:
                p = StaffPayment.objects.get(finance=finance, staff_id=staff_id)
                p.attendance_status = att
                p.staff_submitted = True
                p.save()
                success_msg = f"Attendance marked successfully!"
            except StaffPayment.DoesNotExist:
                pass
        return redirect('staff_attendance')

    payments = StaffPayment.objects.filter(finance=finance).select_related('staff').order_by('staff__name')
    return render(request, 'tracker/staff_login_attendance.html', {
        'payments': payments,
        'today': today,
        'success_msg': success_msg,
    })


# ── Staff detail (admin only) ─────────────────────────────────────
@login_required
def staff_list(request):
    all_staff = Staff.objects.filter(is_active=True).order_by('name')
    return render(request, 'tracker/staff_list.html', {'staff_list': all_staff})

@login_required
def staff_detail(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    payments = StaffPayment.objects.filter(staff=staff)\
        .select_related('finance').order_by('-finance__date')[:30]
    return render(request, 'tracker/staff_detail.html', {
        'staff': staff, 'payments': payments})


# ── Vendors ───────────────────────────────────────────────────────
@login_required
def vendors(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Vendor.objects.get_or_create(name=name)
        return redirect('vendors')

    today = date.today()
    vendor_data = []
    for v in Vendor.objects.all():
        today_entries = DailyEntry.objects.filter(subcategory__vendor=v, date=today)
        today_count   = today_entries.count()
        today_total   = today_entries.aggregate(t=Sum('total'))['t'] or 0
        vendor_data.append({
            'vendor': v, 'today_count': today_count,
            'today_total': today_total, 'done': today_count > 0,
        })
    grand_total = sum(vd['today_total'] for vd in vendor_data)
    done_count  = sum(1 for vd in vendor_data if vd['done'])
    return render(request, 'tracker/vendors.html', {
        'vendor_data': vendor_data, 'today': today,
        'grand_total': grand_total, 'done_count': done_count,
    })


@login_required
def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    today  = date.today()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_entry':
            subcat = get_object_or_404(SubCategory, id=request.POST.get('subcategory'), vendor=vendor)
            w = request.POST.get('weight'); p = request.POST.get('price')
            d = request.POST.get('date') or today
            if w and p:
                DailyEntry.objects.create(subcategory=subcat, date=d,
                    weight=w, price=p, total=float(w)*float(p))
        elif action == 'delete_entry':
            DailyEntry.objects.filter(id=request.POST.get('entry_id')).delete()
        elif action == 'add_subcategory':
            name = request.POST.get('name', '').strip()
            if name:
                SubCategory.objects.get_or_create(vendor=vendor, name=name)
        elif action == 'delete_subcategory':
            SubCategory.objects.filter(id=request.POST.get('sub_id'), vendor=vendor).delete()
        return redirect('vendor_detail', vendor_id=vendor_id)

    today_entries = DailyEntry.objects.filter(
        subcategory__vendor=vendor, date=today).select_related('subcategory')
    return render(request, 'tracker/vendor_detail.html', {
        'vendor': vendor,
        'subcategories': vendor.subcategories.all(),
        'today_entries': today_entries,
        'today_total': today_entries.aggregate(t=Sum('total'))['t'] or 0,
        'today': today,
    })


# ── Reports ───────────────────────────────────────────────────────
@login_required
def reports(request):
    selected = request.GET.get('date', str(date.today()))
    try:
        report_date = date.fromisoformat(selected)
    except ValueError:
        report_date = date.today()

    entries     = DailyEntry.objects.filter(date=report_date).select_related('subcategory__vendor')
    grand_total = entries.aggregate(t=Sum('total'))['t'] or 0

    try:
        finance = DailyFinance.objects.get(date=report_date)
    except DailyFinance.DoesNotExist:
        finance = None

    incentive_entries = []
    if finance:
        incentive_entries = DailyIncentive.objects.filter(
            finance=finance, amount__gt=0).select_related('incentive_name')

    return render(request, 'tracker/reports.html', {
        'entries': entries, 'grand_total': grand_total,
        'report_date': report_date, 'finance': finance,
        'today': date.today(), 'incentive_entries': incentive_entries,
    })


# ── CSV Export ────────────────────────────────────────────────────
@login_required
def export_csv(request):
    export_date_str = request.GET.get('date', str(date.today()))
    try:
        export_date = date.fromisoformat(export_date_str)
    except ValueError:
        export_date = date.today()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="mvrs_{export_date}.csv"'
    w = csv.writer(response)
    w.writerow(['MVRS DAILY REPORT', str(export_date)])
    w.writerow([])
    fin = None
    try:
        fin = DailyFinance.objects.get(date=export_date)
        w.writerow(['--- EARNINGS ---'])
        w.writerow(['Cash', fin.cash])
        w.writerow(['Carry Forward', fin.carry_forward])
        w.writerow(['Total Earnings', fin.total_earnings])
        w.writerow([])
        w.writerow(['--- DELIVERY (record only) ---'])
        w.writerow(['Zomato', fin.zomato])
        w.writerow(['Swiggy', fin.swiggy])
        w.writerow([])
        w.writerow(['--- EXPENSE BREAKDOWN ---'])
        w.writerow(['Card Expense', fin.card_expense])
        incentives = DailyIncentive.objects.filter(finance=fin, amount__gt=0).select_related('incentive_name')
        for inc in incentives:
            w.writerow([f'Incentive - {inc.incentive_name.name}', inc.amount])
    except DailyFinance.DoesNotExist:
        pass

    w.writerow([])
    w.writerow(['--- VENDOR EXPENSES ---'])
    w.writerow(['Vendor', 'Item', 'Weight', 'Price', 'Total'])
    entries = DailyEntry.objects.filter(date=export_date).select_related('subcategory__vendor')
    for e in entries:
        w.writerow([e.subcategory.vendor.name, e.subcategory.name, e.weight, e.price, e.total])
    w.writerow(['', '', '', 'Vendor Total', entries.aggregate(t=Sum('total'))['t'] or 0])

    w.writerow([])
    w.writerow(['--- STAFF ---'])
    w.writerow(['Name', 'Role', 'Attendance', 'Salary', 'Incentive', 'Total'])
    if fin:
        for sp in fin.staff_payments.select_related('staff').all():
            w.writerow([sp.staff.name, sp.staff.get_role_display(),
                        sp.get_attendance_status_display(),
                        sp.salary, sp.incentive, sp.total])
        w.writerow(['', '', '', '', 'Staff Total', fin.total_staff_cost])
        w.writerow([])
        w.writerow(['--- SUMMARY ---'])
        w.writerow(['Total Earnings',  fin.total_earnings])
        w.writerow(['Vendor Expenses', fin.total_vendor_expense])
        w.writerow(['Staff Cost',      fin.total_staff_cost])
        w.writerow(['Card Expense',    fin.card_expense])
        w.writerow(['Incentives',      fin.total_incentives])
        w.writerow(['Other Expenses',  fin.other_expenses])
        w.writerow(['NET PROFIT',      fin.net_profit])

    return response

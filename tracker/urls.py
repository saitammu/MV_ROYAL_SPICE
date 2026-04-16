from django.urls import path
from . import views

urlpatterns = [
    path('',               views.dashboard,         name='dashboard'),
    path('dashboard/',     views.dashboard,          name='dashboard_date'),
    path('login/',         views.login_view,         name='login'),
    path('logout/',        views.logout_view,        name='logout'),
    path('vendors/',       views.vendors,            name='vendors'),
    path('vendors/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    path('reports/',       views.reports,            name='reports'),
    path('export-csv/',    views.export_csv,         name='export_csv'),
    path('attendance/',    views.attendance,         name='attendance'),
    path('staff-attendance/', views.staff_attendance, name='staff_attendance'),
    path('staff/',         views.staff_list,         name='staff_list'),
    path('staff/<int:staff_id>/', views.staff_detail, name='staff_detail'),
    path('zomato-report/', views.zomato_report,     name='zomato_report'),
    path('swiggy-report/', views.swiggy_report,     name='swiggy_report'),
    path('export-platform-csv/', views.export_platform_csv, name='export_platform_csv'),
]

# reports/views.py

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Report

@staff_member_required
def report_list(request):
    reports = Report.objects.all().order_by('-report_date')
    return render(request, 'reports/report_list.html', {'reports': reports})

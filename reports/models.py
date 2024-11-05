# reports/models.py

from django.db import models

class Report(models.Model):
    report_date = models.DateField()
    sales = models.DecimalField(max_digits=12, decimal_places=2)
    profit = models.DecimalField(max_digits=12, decimal_places=2)
    expenses = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Report for {self.report_date}"

from django.db import models

class Report(models.Model):
    date = models.DateField(auto_now_add=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    expenses = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Report for {self.date}"

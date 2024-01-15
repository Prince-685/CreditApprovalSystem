from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator,RegexValidator


class CustomerData(models.Model):
    phone_number_validator = RegexValidator(
        regex=r'^\d{10}$',
        message='invalid_phone_number',
        
    )

    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message='Age must be at least 1 year.'),
            MaxValueValidator(120, message='Age cannot exceed 120 years.')
        ]
    )
    phone_number = models.CharField(max_length=10, validators=[phone_number_validator])
    monthly_salary = models.PositiveIntegerField()
    approved_limit = models.PositiveIntegerField()
    

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"


class LoanData(models.Model):
    customer_id = models.ForeignKey(CustomerData, on_delete=models.CASCADE)
    loan_id = models.AutoField(primary_key=True)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tenure = models.PositiveIntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    monthly_repayment = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    emis_paid_on_time = models.PositiveIntegerField(default=0)
    start_date = models.CharField(max_length=255)
    end_date = models.CharField(max_length=255)

    def __str__(self):
        return f"Customer ID: {self.customer_id.customer_id} - Loan ID: {self.loan_id} - Loan Amount: {self.loan_amount}"
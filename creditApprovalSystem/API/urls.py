from django.urls import path
from . import views

urlpatterns = [
    path('register', views.Register_Customer),
    path('check-eligibility',views.Loan_Eligibility),
    path('create-loan',views.Create_Loan),
    path('view-loan/<int:loan_id>',views.Loan_Detail),
    path('view-loans/<int:customer_id>',views.View_loan)

]
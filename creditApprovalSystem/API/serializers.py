from rest_framework import serializers
from .models import CustomerData,LoanData


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanData
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    loans = LoanSerializer(many=True, read_only=True)
    class Meta:
        model = CustomerData
        fields = ['customer_id','first_name','last_name','phone_number','age','loans']





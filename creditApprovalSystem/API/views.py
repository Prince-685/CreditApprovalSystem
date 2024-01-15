import json
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from .models import CustomerData,LoanData
from .serializers import CustomerSerializer,LoanSerializer
from datetime import datetime, date
from rest_framework.permissions import AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])
def Register_Customer(request):
    if request.method == 'POST':
        data= json.loads(request.body)
        fname=data.get('first_name')
        lname=data.get('last_name')
        age=data.get('age')
        phone_number=data.get('phone_number')
        monthly_salary=data.get('monthly_income')
        approved_limit = round(36 * monthly_salary, -5)
        customer_detail=CustomerData(
            first_name=fname,
            last_name=lname,
            age=age,
            phone_number=phone_number,
            monthly_salary=monthly_salary,
            approved_limit=approved_limit
        )   
        customer_detail.save()
        customer_instance=CustomerData.objects.get(first_name=fname,phone_number=phone_number)  
        customer_data = {
            'customer_id': customer_instance.customer_id,
            'first_name': customer_instance.first_name,
            'last_name': customer_instance.last_name,
            'phone_number': customer_instance.phone_number,
            'monthly_salary': customer_instance.monthly_salary,
            'approved_limit': customer_instance.approved_limit,
        }  
        return JsonResponse(customer_data,status=status.HTTP_201_CREATED) 
    else:
        return Response({'error': 'POST method is required'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@permission_classes([AllowAny])
def get_credit_score(customer_id,interest_rate,loan_amount):
    current_date=date.today()
    customer_instance=CustomerData.objects.get(customer_id=customer_id)
    loan_instance=LoanData.objects.filter(customer_id=customer_id)
    current_emi=0
    current_loan_sum=loan_amount
    approval=False
    corrected_interest_rate=interest_rate
    if loan_instance.exists():
        for i in loan_instance:
            end_date=datetime.strptime(i.end_date,'%d-%m-%Y').date()
            if end_date>current_date:
                current_loan_sum+=i.loan_amount
                current_emi+=i.monthly_repayment
        if current_emi>customer_instance.monthly_salary/2:
            return {'approval':approval,'corrected_interest_rate':corrected_interest_rate,'message':'Loan can not be approved due to your current running emis are more than your the half of your salary'}
    
        if current_loan_sum>=customer_instance.approved_limit:
            return {'approval':approval,'corrected_interest_rate':corrected_interest_rate,'message':'Loan can not be approved due to your current running loans are greater than your approved loan limit'}
    
    else:
        return {'approval':True,'corrected_interest_rate':16}
   
    sum_loan_approved=0
    no_loan_past=0
    cYear_activity=0
    sum_past_loan_tenure=0
    sum_emis_paid_on_time=0
    
    for i in loan_instance:
        start_date=datetime.strptime(i.start_date,'%d-%m-%Y').date()
        end_date=datetime.strptime(i.end_date,'%d-%m-%Y').date()
        if start_date.year==current_date.year or end_date>current_date:
            cYear_activity+=1
            sum_loan_approved+=i.loan_amount
        if end_date<current_date:
            no_loan_past+=1
            sum_past_loan_tenure+=i.tenure
            sum_emis_paid_on_time+=i.emis_paid_on_time
        
    credit_score=0
    
    if no_loan_past>=5:
        credit_score+=25
    elif no_loan_past>=3:
        credit_score+=20
    elif no_loan_past>=1: 
        credit_score+=10
    
    
    if cYear_activity>0:
        credit_score+=15

    if sum_loan_approved>=0.4*customer_instance.approved_limit:
        credit_score+=25
    elif sum_loan_approved>=0.2*customer_instance.approved_limit:
        credit_score+=20
    elif sum_loan_approved>=0.1*customer_instance.approved_limit: 
        credit_score+=10

    if sum_past_loan_tenure>0:
        per=sum_emis_paid_on_time*100/sum_past_loan_tenure
        if per>=80:
            credit_score+=35
        elif per>=60:
            credit_score+=25
        elif per>=40:
            credit_score+=15
        elif per>=20: 
            credit_score+=5

    
    if credit_score>50:
        approval=True
        corrected_interest_rate=8
    elif credit_score>30:
        approval=True
        corrected_interest_rate=12.5
    elif credit_score>10:
        approval=True
        corrected_interest_rate=16.5
    else:
        approval=False
        return{'approval':approval,'corrected_interest_rate':corrected_interest_rate,'message':'Loan cannot approved due to your low credit score'}

    return {'approval':approval,'corrected_interest_rate':corrected_interest_rate}


@api_view(['POST'])
@permission_classes([AllowAny])
def Loan_Eligibility(request):
    if request.method=='POST':
        data= json.loads(request.body)
        c_id=data.get('customer_id')
        interest_rate=data.get('interest_rate')
        tenure=data.get('tenure')
        loan_amount=data.get('loan_amount')

        eligibility_data=get_credit_score(c_id,interest_rate,loan_amount)
        
        
        total_amount=loan_amount+(loan_amount*eligibility_data['corrected_interest_rate']*tenure/12)/100
        monthly_installment=total_amount/tenure
        
        responseData=({'customer_id':c_id,'approval':eligibility_data['approval'],'interest_rate':interest_rate,'corrected_interest_rate':eligibility_data['corrected_interest_rate'],'tenure':tenure,'monthly_installment':monthly_installment})
        return JsonResponse(responseData,status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error': 'POST method is required'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)    


@api_view(['POST'])
@permission_classes([AllowAny])
def Create_Loan(request):
    if request.method=='POST':
        data= json.loads(request.body)
        c_id=data.get('customer_id')
        loan_amount=data.get('loan_amount')
        interest_rate=data.get('interest_rate')
        tenure=data.get('tenure')
        customer_instance=CustomerData.objects.get(customer_id=c_id)

        eligibility_data=get_credit_score(c_id,interest_rate,loan_amount)
        total_amount=loan_amount+(loan_amount*eligibility_data['corrected_interest_rate']*tenure/12)/100
        monthly_installment=total_amount/tenure

        if 'message' in eligibility_data:
            return JsonResponse({'loan_id':'','customer_id':c_id,'loan_approved':eligibility_data['approval'],'message':eligibility_data['message'],'monthly_installment':monthly_installment},status=status.HTTP_400_BAD_REQUEST)
        else:
            today_date=date.today()
            start_date=today_date.strftime('%d-%m-%Y')
            end_year=today_date.year+int(tenure/12)
            end_month=today_date.month+tenure%12
            if len(str(end_month))==1:
                end_month='0'+str(end_month)
            end_day=today_date.day
            end_date=str(end_year)+'-'+end_month+'-'+str(end_day)
            end_date=datetime.strptime(end_date,'%Y-%m-%d').strftime('%d-%m-%Y')

            loan_data=LoanData(
                customer_id=customer_instance,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=interest_rate,
                monthly_repayment=monthly_installment,
                start_date=start_date,
                end_date=end_date
            )
            loan_data.save()
            loan_instance=LoanData.objects.get(customer_id=c_id,start_date=start_date)
            return JsonResponse({'loan_id':loan_instance.loan_id,'customer_id':c_id,'loan_approved':eligibility_data['approval'],'monthly_installment':monthly_installment},status=status.HTTP_201_CREATED)
    else:
        return JsonResponse({'error': 'POST method is required'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        

@api_view(['GET'])
@permission_classes([AllowAny])
def Loan_Detail(request,loan_id):
    if request.method=='GET':
        loan_instance=LoanData.objects.get(loan_id=loan_id)
        customer_id=loan_instance.customer_id.customer_id
        customer_instance=CustomerData.objects.get(customer_id=customer_id)
        serializer = CustomerSerializer(customer_instance)
        serializer.data.pop
        
        return JsonResponse({'loan_id':loan_instance.loan_id,'customer':serializer.data,'loan_amount':loan_instance.loan_amount,'interest_rate':loan_instance.interest_rate,'monthly_installment':loan_instance.monthly_repayment,'tenure':loan_instance.tenure},status=status.HTTP_200_OK)
    
    else:
        return JsonResponse({'error': 'POST method is required'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def View_loan(request,customer_id):
    if request.method=='GET':
        loan_instance=LoanData.objects.filter(customer_id=customer_id)
        serializer=LoanSerializer(loan_instance,many=True)
        for i in serializer.data:
            repayment_left=i['tenure']-i['emis_paid_on_time']
            i.pop('customer_id', None)
            i.pop('tenure',None)
            i.pop('emis_paid_on_time',None)
            i.pop('start_date',None)
            i.pop('end_date',None)

            i['repayment_left']=repayment_left
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    else:
        return Response({'error': 'POST method is required'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

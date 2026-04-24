from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return HttpResponse("Welcome to the CRM Home Page!")


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer

@api_view(['POST'])
def create_customer(request):
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Customer created", "data": serializer.data})
    return Response(serializer.errors)



@api_view(['GET'])
def get_customers(request):
    customers = Customer.objects.all()

    if not customers.exists():
        return Response({
            "status": "success",
            "message": "No customers found",
            "data": []
        }, status=status.HTTP_200_OK)

    serializer = CustomerSerializer(customers, many=True)

    return Response({
        "status": "success",
        "message": "Customers fetched successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)
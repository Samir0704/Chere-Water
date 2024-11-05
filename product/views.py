from django.shortcuts import render
# Create your views here.
from django.shortcuts import render
from rest_framework import generics
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAuthenticated, AllowAny
from product.models import Product, WebOrder,Action
from .serializers import ProductHomeListSerializer, WebOrderSerializer, ProductListSerializer,ActionSerializer
from rest_framework.generics import ListAPIView


class ProductHomeListView(generics.ListAPIView):
    queryset = Product.objects.all()[:10]
    serializer_class = ProductHomeListSerializer



class WebOrderCreateView(generics.CreateAPIView):
    queryset = WebOrder.objects.all()
    serializer_class = WebOrderSerializer
    throttle_classes = [UserRateThrottle, ]


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer


class DiscountListView(ListAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    throttle_classes = []
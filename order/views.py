from django.shortcuts import render
from rest_framework.generics import ListAPIView,CreateAPIView
from rest_framework import generics
from order.serializers import *
from order.models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from order.serializers import *
from django.db import transaction

# Create your views here.


class CartItemListView(ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = []

    def get_queryset(self):
        user = self.request.user
        return CartItem.objects.filter(user=user, is_visible=True)
    

class AddItemToCartView(CreateAPIView):
    serializer_class = CartItemAddSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = Product.objects.get(pk=kwargs.get('product_id'))
        if product.quantity <= 0:
            return Response({"error": "Извините, товар временно недоступен"}, status=status.HTTP_400_BAD_REQUEST)
        cart_items = CartItem.objects.filter(user=request.user, product=product, is_visible=True)
        if not cart_items.exists():
            CartItem.objects.create(user=request.user, product=product, quantity=1, is_visible=True)

        else:
            cart_item = cart_items
            cart_item.quantity += 1
            cart_item.save()
        return Response({"status": "Вы добавили товар в корзину"}, status=status.HTTP_201_CREATED)


class CartItemUpdate(generics.UpdateAPIView):
    serializer_class = CartItemAddSerializer
    queryset = CartItem.objects.all()
    lookup_field = 'pk'

class CartItemRemove(generics.DestroyAPIView):
    serializer_class = RemoveItemFromCartSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = []

    def get_queryset(self):
        qs = CartItem.objects.filter(user=self.request.user, is_visible=True)
        return qs

    def destroy(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product_in_cart = CartItem.objects.filter(user=request.user, product=product_id, is_visible=True).first()
        if product_in_cart.exists() is None:
            return Response({"В вашей корзине нет такого товара!"}, status=status.HTTP_404_NOT_FOUND)
        elif product_in_cart.quantity > 1:
            product_in_cart.quantity -= 1
            product_in_cart.save()
            return Response({"Количество товара уменьшено"}, status=status.HTTP_200_OK)
        else:
            product_in_cart.delete()
        return Response({"Товар удален из вашей корзины"}, status=status.HTTP_200_OK)


class OrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = []
    serializer_class = OrderCreateSerializer

    def get_queryset(self):
        qs = Order.objects.filter(user=self.request.user).all()
        return qs
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_items = CartItem.objects.filter(user=request.user, id__in=serializer.validated_data['cart_items'],
                                             is_visible=True)
        if not cart_items.exists():
            return Response(data={_("Ваша корзина пуста. Добавьте товары перед оформлением заказа.")},
                            status=status.HTTP_404_NOT_FOUND)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                address=serializer.validated_data['address'],
                phone_number=serializer.validated_data['phone_number'],

                total_price=total_price
            )

            for item in cart_items:
                item.order = order
                item.is_visible = False
                item.product.quantity -= item.quantity
                item.product.save()
                item.save()
        return Response({_("Заказ успешно создан")}, status=status.HTTP_201_CREATED)


class OrderCancelView(CreateAPIView):
    serializer_class = OrderCancelSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = []

    def create(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')
        try:
            order = Order.objects.get(user=request.user, id=order_id)
        except Order.DoesNotExist:
            return Response(_("Заказ не найден"), status=status.HTTP_404_NOT_FOUND)
        if order.status == Order.OrderStatus.CANCELLED:
            return Response(_("Заказ уже отменен"), status=status.HTTP_400_BAD_REQUEST)

        # Возврат количества товаров в базу данных

        cart_items = CartItem.objects.filter(user=request.user, order=order)
        for item in cart_items:
            item.product.quantity += item.quantity
            item.product.save()
        order.status = Order.OrderStatus.CANCELLED
        order.save()
        return Response(_("Заказ успешно отменен"), status=status.HTTP_200_OK)


class OrderMinSumView(ListAPIView):
    serializer_class = OrderMinSumSerializer
    throttle_classes = []
    queryset = OrderMinSum.objects.all()
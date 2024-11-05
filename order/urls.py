from django.urls import path
from .views import *

urlpatterns = [
    path('cart-items/', CartItemListView.as_view()),
    path('cart-add/', AddItemToCartView.as_view(),name='cart-add'),
    path('cart-change/<int:pk>', CartItemUpdate.as_view(),name='cart-change'),
    path('cart-remove/<int:pk>', CartItemRemove.as_view(),name='cart-remove'),
    # ORDER
    path('orders-add/', OrderCreateView.as_view(),name='order-add'),
    

]
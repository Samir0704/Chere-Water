from rest_framework import serializers

from order.models import CartItem, Order,OrderMinSum
from product.serializers import ProductListSerializer
from product.views import ProductHomeListView
from django.utils.translation import gettext_lazy as _


class CartItemAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ( "product", "quantity")


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        class Meta:
          model = CartItem
          fields = ("id", "user", "product", "quantity")

class RemoveItemFromCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("id",)

class ListItemsFromCardViewSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "user", "product", "quantity")


class RemoveCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("id",)

class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "user", "phone_number", "status", "address", "created_at", "number")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        cart_items = CartItem.objects.filter(user=self.context.get("request").user, order_id=instance.id).values()
        products = []
        for item in cart_items:
            product = {"id": item['product_id'], "quantity": item['quantity']}
            products.append(product)
        data["products"] = products
        return data
class OrderCreateSerializer(serializers.ModelSerializer):
    cart_items = serializers.ListSerializer(child=serializers.IntegerField())

    class Meta:
        model = Order
        fields = ("id", "address", "phone_number", "cart_items")

    def validate_cart_items(self, value):
        user_cart_items = CartItem.objects.filter(user=self.context["request"].user, is_visible=True).all()
        for item_id in value:
            if item_id not in user_cart_items.values_list('id', flat=True):
                raise serializers.ValidationError(_(f"Товар с ID {item_id} не найден в корзине."))
        return value

class CartRemoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("id",)       
         
class OrderMinSumSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderMinSum
        fields = ("id", "min_order_sum")

class OrderCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "user", "phone_number", "status", "address", "created_at", "number")        
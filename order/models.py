from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import Media
from product.models import Product
from account.models import User
from django.db.models import Sum
# Create your models here.

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        CREATED = 'created', _('Created')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')

    address = models.CharField(_('address'), max_length=255)
    long = models.FloatField(_('longitude'), blank=True, null=True)
    lat = models.FloatField(_('latitude'), blank=True, null=True)
    status = models.CharField(_('status'),choices= OrderStatus, max_length=255)
    phone_number = models.CharField(_('phone_number'), max_length=255)
    number = models.CharField(_('order number'), max_length=20, unique=True, null=True, blank=True)
    total_price = models.FloatField(_('total price'), blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_order') 
    
    def __str__(self):
        return f"Order {self.id} by {self.user.full_name}"
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def save(self, *args, **kwargs):
        total_price = self.cart_items.aggregate(Sum('subtotal_price'))['subtotal_price__sum']
        self.total_price = total_price
        self.save()


       

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('product'))
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    is_visible = models.BooleanField(_('is_visible'), default=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('order'),related_name='cart_items')
    subtotal_price = models.FloatField(_('subtotal price'), blank=True, null=True)
    

    def __str__(self):
        return f"{self.quantity}"
    
    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')

class OrderMinSum(models.Model):
    min_order_sum = models.CharField(_('min_order_sum'), max_length=255)

    def __str__(self):
        return self.min_order_sum
    
    class Meta:
        verbose_name = _('Order min sum')
        verbose_name_plural = _('Order min sums')


class NotificationOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name=_('order'),
                              related_name='notification_orders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'),
                             related_name="notification_orders")
    employee_count = models.PositiveIntegerField(_('employee count'), default=0)
    durations_days = models.PositiveIntegerField(_('durations days'), default=0)
    box_count = models.PositiveIntegerField(_('box count'), default=0)

    def __str__(self):
        return str(self.order.id) + str(self.employee_count)

from sqlite3 import IntegrityError

from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import generate_order_number
from .models import Order


@receiver(post_save, sender=Order)
def create_order(sender, instance, created, **kwargs):
    if created:
        try:
            instance.number = generate_order_number()
            instance.save()
        except IntegrityError:
            instance.number = f"#00000{instance.id}"
            instance.save()
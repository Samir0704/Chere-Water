from django.contrib.auth.hashers import check_password

from asgiref.sync import sync_to_async
from django.db import IntegrityError

from django.db.utils import IntegrityError


@sync_to_async
def create_user_db(user_data):
    try:
        new_user = CustomUser.objects.create(**user_data)
        return new_user
    except IntegrityError:
        raise Exception("User already exists")


@sync_to_async
def login_user(phone, password, tg_id, tg_u, user_lang):
    user = CustomUser.objects.filter(phone_number=phone).last()
    if user and check_password(password, user.password):
        user.telegram_id = tg_id
        user.tg_username = f"https://t.me/{tg_u}"
        user.user_lang = user_lang
        user.save()
        return user
    else:
        return None


@sync_to_async
def get_user_db(telegram_id):
    try:
        user = CustomUser.objects.get()
        return user
    except CustomUser.DoesNotExist:
        return None


@sync_to_async
def get_company_contacts():
    contact = Contacts.objects.last()
    return contact


@sync_to_async
def get_my_orders(phone_number):
    return list(Order.objects.all().filter(phone_number=phone_number))


@sync_to_async
def create_item_db(t_id, p_id, p_quantity):
    user = CustomUser.objects.get(telegram_id=t_id)
    product = Product.objects.get(id=p_id)

    if user and product:
        data = {
            "user": user,
            "product": product,
            "quantity": p_quantity
        }
        item = CartItem.objects.create(**data)
        return item
    else:
        return None


@sync_to_async
def create_order_from_cart(t_id, address, reminder_days):
    try:
        user = CustomUser.objects.get(telegram_id=t_id)

        cart_items = CartItem.objects.filter(user=user, is_visible=True)

        total_price = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            user=user,
            address=address,
            phone_number=user.phone_number,
            total_price=total_price,
            status=Order.OrderStatus.CREATED
        )
        user.reminder_days = reminder_days
        user.save()

        for item in cart_items:
            item.order = order
            item.is_visible = False
            item.save()

        return order
    except CustomUser.DoesNotExist:
        print("Пользователь не найден.")
        return None


@sync_to_async
def create_order_db(order_data, reminder_days, user_id):
    try:
        user = CustomUser.objects.get(telegram_id=user_id)

        # Buyurtma raqami mavjudligini tekshirish
        order_number = order_data.get('order_number')
        if Order.objects.filter(order_number=order_number).exists():
            raise Exception("Order with the same order number already exists")

        new_order = Order.objects.create(
            user=user,
            phone_number=order_data['phone_number'],
            address=order_data['address'],
            total_price=order_data['total_price'],
            status=Order.OrderStatus.CREATED,
            order_number=order_number  # Buyurtma raqamini ham qo'shamiz
        )

        user.reminder_days = reminder_days
        user.save()
        return new_order
    except IntegrityError as e:
        raise Exception(f"Database error: {str(e)}")
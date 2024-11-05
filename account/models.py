from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
    class UserType(models.TextChoices):
        LEGAL = 'legal', _('LEGAL')
        INDIVIDUAL = 'individual', _('INDIVIDUAL')

    full_name = models.CharField(_('full name'), max_length=255)
    email = models.EmailField(_('email'), unique=True)
    username = models.CharField(_('username'), max_length=255, unique=True)
    phone_number = PhoneNumberField(_('phone_number'), unique=True)
    password = models.CharField(_('password'), max_length=255)
    user_type = models.CharField(
        _('user type'),
        max_length=10,
        choices=UserType.choices,
        default=UserType.INDIVIDUAL
    )
    telegram_id = models.CharField(_('telegram id'), max_length=255, unique=True, blank=True, null=True)
    telegram_username = models.CharField(_('telegram username'), max_length=255, unique=True, blank=True, null=True)
    company_name = models.CharField(_('company name'), max_length=255, null=True, blank=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


    def get_token(self):
        refresh = RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    

class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_user')
    telegram_id = models.CharField(_('telegram id'), max_length=255, unique=True)
    telegram_username = models.CharField(_('telegram username'), max_length=255, blank=True, null=True)    
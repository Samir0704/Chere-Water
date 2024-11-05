from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import User

class UserRegisterSerializer(serializers.Serializer):
    user_type = serializers.ChoiceField(choices=User.UserType)
    full_name = serializers.CharField(required=False)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(min_length=8, write_only=True)
    company_name = serializers.CharField(required=False)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                _('Passwords are not match')
            )



class UserLoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)



    def validate(self, attrs):
        try:
            print("attr: ", attrs)
            user = User.objects.get(username=attrs['username'])
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError(_("User password is incorrect"))
            return attrs
        except User.DoesNotExist:
            raise serializers.ValidationError(_("User does not exist"))

class UserLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField(required=True)
    refresh = serializers.CharField(required=True)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'full_name', 'username', 'email', 'first_name', 'last_name', 'phone_number',
            )    
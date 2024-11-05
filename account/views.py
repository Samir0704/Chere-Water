from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from .serializers import UserRegisterSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from account.serializers import UserLoginRequestSerializer,UserLoginResponseSerializer,UserProfileSerializer
from django.contrib.auth import authenticate
from account.models import User
# Create your views here.-




class UserRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer



class UserLoginView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserLoginRequestSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            user = User.objects.get(username=data['username'])
            logged_user = authenticate(username=user.username, password=data['password'])
            if logged_user:
                return Response(data=user.get_token())
            return Response(data={"User not found"})
        except User.DoesNotExist:
            return Response(data={"User not found"}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileAPIView(RetrieveUpdateAPIView):
    throttle_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
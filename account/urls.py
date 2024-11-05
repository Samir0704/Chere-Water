from django.urls import path
from account.views import UserLoginView,UserRegisterView,UserProfileAPIView

urlpatterns = [
    path('register/',UserRegisterView.as_view(), name='register'),
    path('login/',UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileAPIView.as_view(), name='profile-view'),
    # path('logout/',UserLogoutAPIView.as_view(),name = 'logout'),
    

]   
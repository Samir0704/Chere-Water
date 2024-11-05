from django.urls import path
from .views import *

urlpatterns = [
    path('banners/', BannerListView.as_view(), name='banner-list'),
    path('about-us/home/', AboutUsHomeView.as_view(), name='about-us-home'),
    path('social-media/', SocialMediaView.as_view(), name='social-media'),
    path('contacts/', ContactsWithUsView.as_view(), name='contacts'),
]
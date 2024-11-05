from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Banner
from common.models import Media
from unittest import mock

class TestBannerListView(APITestCase):
    url = reverse("banner-list")

    def setUp(self):
        pass

    def test_happy(self):
        banner1 = Banner.objects.create(title="Banner 1", subtitle="subtitle1")
        media = Media.objects.create(type=Media.MediaType.IMAGE, file="image.png")
        banner2 = Banner.objects.create(title="Banner 2", subtitle="subtitle2", bg_image=media)
        resp = self.client.get(self.url)
        expected_data = {'bg_image': 'http://testserver/media/image.png', 'title': 'Banner 2', 'subtitle': 'subtitle2'}
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)
        self.assertDictEqual(resp.data[1], expected_data)


    def test_with_no_banner(self, send_otp_code):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.data['error'], 'No banners found')
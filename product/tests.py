from django.test import TestCase
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import WebOrder
from common.models import Media

class TestWebOrderCreateView(APITestCase):
    url = reverse("web-order")

    def setUp(self):
        pass

    def test_happy(self):
        web_order1 = WebOrder.objects.create(full_name="Order 1", phone_number="subtitle1")
        resp = self.client.get(self.url)
        expected_data = {'full_name':'Samir Abdurahimov','phone_number':'+998996464531'}
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)
        self.assertDictEqual(resp.data[1], expected_data)


    def test_with_no_order(self, send_otp_code):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.data['error'], 'No orders found')


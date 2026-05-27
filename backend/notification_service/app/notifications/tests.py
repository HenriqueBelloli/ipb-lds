from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class HealthTests(APITestCase):
	def setUp(self):
		self.url = reverse('notification-health')

	def test_health_retorna_payload_estavel_sem_autenticacao(self):
		resp = self.client.get(self.url)

		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data['status'], 'ok')
		self.assertEqual(resp.data['service'], 'notification-service')

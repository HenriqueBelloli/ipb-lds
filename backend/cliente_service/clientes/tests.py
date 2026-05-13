from django.test import TestCase
from rest_framework.test import APIClient
from .models import Cliente
import uuid

class ClienteAPITestCase(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.client = Cliente.objects.create(
            nif='123456789',
            nome='João Silva',
            email='joao@email.com'
        )
    def tes_listar_clientes(self):
        response = self.client_api.get('/api/clientes/')
        self.assertEqual(response.status_code, 200)
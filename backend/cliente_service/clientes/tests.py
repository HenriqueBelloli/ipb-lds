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

    
    def test_criar_cliente(self):
        response = self.client_api.post('/api/clientes/', {
            'nif': '987654321',
            'nome': 'Maria Santos',
            'email': 'maria@email.com'
        }, format='json')
        self.assertEqual(response.status_code, 201)

    def test_detalhe_cliente(self):
        response = self.client_api.get(f'/api/clientes/{self.client.id}/')
        self.assertEqual(response.status_code, 200)

    def test_atualizar_cliente(self):
        response = self.client_api.patch(f'/api/clientes/{self.cliente.id}/', {
            'telefone':'912345678'
        }, format='json')
        self.assertEqual(response.status_code, 200)

    def test_eliminar_cliente(self):
        response = self.client_api.delete(f'/api/clientes/{self.cliente.id}/')
        self.assertEqual(response.status_code, 204)

    


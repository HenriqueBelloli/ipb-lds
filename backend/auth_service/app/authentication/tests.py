import uuid
from unittest.mock import patch

from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Credencial


def _criar_credencial(email='user@test.com', password='senha123', perfil='OPERADOR', ativo=True):
    return Credencial.objects.create(
        usuarioId=uuid.uuid4(),
        delegacaoId=uuid.uuid4(),
        email=email,
        passwordHash=make_password(password),
        perfil=perfil,
        ativo=ativo,
    )


def _token_para(credencial: Credencial) -> str:
    refresh = RefreshToken()
    refresh['usuarioId'] = str(credencial.usuarioId)
    refresh['email'] = credencial.email
    refresh['delegacaoId'] = str(credencial.delegacaoId)
    refresh['perfil'] = credencial.perfil
    refresh['ativo'] = credencial.ativo
    return str(refresh.access_token)


class LoginTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth-login')
        self.cred = _criar_credencial()

    @patch('authentication.views.publish_login_success')
    @patch('authentication.views.publish_login_failed')
    def test_login_valido_retorna_tokens(self, mock_failed, mock_success):
        resp = self.client.post(self.url, {'email': 'user@test.com', 'password': 'senha123'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        mock_success.assert_called_once()
        mock_failed.assert_not_called()

    @patch('authentication.views.publish_login_failed')
    def test_login_password_errada_retorna_401(self, mock_failed):
        resp = self.client.post(self.url, {'email': 'user@test.com', 'password': 'errada'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_failed.assert_called_once()

    @patch('authentication.views.publish_login_failed')
    def test_login_email_inexistente_retorna_401(self, mock_failed):
        resp = self.client.post(self.url, {'email': 'nao@existe.com', 'password': 'x'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_failed.assert_called_once()

    @patch('authentication.views.publish_login_failed')
    def test_utilizador_inativo_retorna_403(self, mock_failed):
        _criar_credencial(email='inativo@test.com', ativo=False)
        resp = self.client.post(self.url, {'email': 'inativo@test.com', 'password': 'senha123'})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        mock_failed.assert_called_once()


class RefreshTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth-refresh')
        self.cred = _criar_credencial(email='refresh@test.com')

    def test_refresh_valido_retorna_novo_access_com_dados(self):
        refresh = RefreshToken()
        refresh['usuarioId'] = str(self.cred.usuarioId)
        refresh['delegacaoId'] = str(self.cred.delegacaoId)
        refresh['perfil'] = self.cred.perfil
        refresh['email'] = self.cred.email
        refresh['ativo'] = self.cred.ativo
        
        resp = self.client.post(self.url, {'refresh': str(refresh)})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertIn('usuarioId', resp.data)
        self.assertIn('delegacaoId', resp.data)
        self.assertIn('perfil', resp.data)
        self.assertEqual(resp.data['perfil'], 'OPERADOR')

    def test_refresh_invalido_retorna_401(self):
        resp = self.client.post(self.url, {'refresh': 'token.invalido.aqui'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class MeTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth-me')
        self.cred = _criar_credencial(email='me@test.com', perfil='GESTOR')

    def test_me_com_token_valido_retorna_dados(self):
        token = _token_para(self.cred)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['email'], 'me@test.com')
        self.assertEqual(resp.data['perfil'], 'GESTOR')
        self.assertIn('usuarioId', resp.data)
        self.assertIn('delegacaoId', resp.data)
        self.assertIn('ativo', resp.data)

    def test_me_sem_token_retorna_401(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth-change-password')
        self.cred = _criar_credencial(email='password@test.com', password='senha123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_token_para(self.cred)}')

    def test_altera_password_com_password_atual_valida(self):
        resp = self.client.put(
            self.url,
            {'currentPassword': 'senha123', 'newPassword': 'novaSenha123'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        self.cred.refresh_from_db()
        self.assertTrue(self.cred.check_password('novaSenha123'))

    def test_rejeita_password_atual_incorreta(self):
        resp = self.client.put(
            self.url,
            {'currentPassword': 'errada', 'newPassword': 'novaSenha123'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        self.cred.refresh_from_db()
        self.assertTrue(self.cred.check_password('senha123'))

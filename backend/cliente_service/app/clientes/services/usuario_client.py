import os
import requests


class UsuarioServiceClient:
    BASE_URL = os.environ.get('USUARIO_SERVICE_URL', 'http://usuario-service:8002')

    @staticmethod
    def mapa_nomes_delegacoes(token: str) -> dict:
        """
        Devolve {delegacaoId (str): nome (str)}.
        Em caso de falha retorna dict vazio — o chamador exibe o UUID como fallback.
        """
        try:
            response = requests.get(
                f"{UsuarioServiceClient.BASE_URL}/api/delegacoes/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                items = data.get('results', data) if isinstance(data, dict) else data
                return {str(d['id']): d['nome'] for d in items}
            return {}
        except requests.exceptions.RequestException:
            return {}

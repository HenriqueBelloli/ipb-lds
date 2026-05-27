import os
import requests

class ClienteServiceClient:
    BASE_URL = os.environ.get('CLIENTE_SERVICE_URL', 'http://cliente-service:8003')

    @staticmethod
    def get_cliente_anonimo(cliente_id : str) -> dict:
        """
        Chamada sem token de utilizador - usa token de serviço interno.
        Retorna apenas eamil e nome do cliente.
        Em caso de falha retorna None sem derrubar o serviço
        """

        try:
            response = requests.get(
                f"{ClienteServiceClient.BASE_URL}/api/clientes/{cliente_id}/",
                headers={
                    "Authorization": f"Bearer {os.environ.get('INTERNAL_SERVICE_TOKEN')}"
                },
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            
            return None
        
        except requests.exceptions.RequestException:
            return None
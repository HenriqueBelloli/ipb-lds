import requests
import os

class FinanceiroServiceClient:
    BASE_URL = os.environ.get(
        'FINANCEIRO_SERVICE_URL',
        'http://financeiro-service:8006'
    )

    @staticmethod
    def verificar_inadimplente(cliente_id: str, token: str) -> bool:
        """
        Consulta o financeiro-service para saber se o cliente
        tem mensalidades em aberto no mês vigente.
        A lógica de inadimplência é responsabilidade do financeiro-service.
        Em caso de falha de comunicação retorna False por omissão —
        não deve bloquear o fluxo por indisponibilidade de outro serviço.
        """
        try:
            response = requests.get(
                f"{FinanceiroServiceClient.BASE_URL}"
                f"/api/financeiro/clientes/{cliente_id}/inadimplente/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get('inadimplente', False)
            return False
        except requests.exceptions.RequestException:
            return False

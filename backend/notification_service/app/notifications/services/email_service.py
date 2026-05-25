import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    SMTP_HOST = os.environ.get('SMTP_HOST', 'mailhog')
    SMTP_PORT = os.environ.get('SMTP_PORT', 1025)
    EMAIL_FROM = os.environ.get('EMAIL_FROM', 'noreply@erp-associacao.pt')

    @staticmethod
    def enviar(destinatario : str, assunto: str, corpo: str) -> bool:
        """
        Envia email via SMTP
        Em desenvolvimento usa Mailhog - sem autenticação
        Retorna True se enviado com sucesso, False em caso de erro
        """

        try:
            msg = MIMEMultipart()
            msg['From'] = EmailService.EMAIL_FROM
            msg['To'] = destinatario
            msg['Subject'] = assunto
            msg.attach(MIMEText(corpo, 'plain', 'utf-8'))

            with smtplib.SMTP(
                EmailService.SMTP_HOST,
                EmailService.SMTP_PORT
            ) as server:
                server.sendmail(
                    EmailService.EMAIL_FROM,
                    destinatario,
                    msg.as_string()
                )

            return True
        
        except Exception as e:
            print(f"Erro ao enviar email para {destinatario}: {str(e)}")
            return False

"""Abstração para serviço de envio de emails.

Sugestão de implementação real: SendGrid (https://sendgrid.com/docs/api-reference/).
O SendGrid oferece envio transacional, templates dinâmicos, rastreamento de
abertura/cliques, e API REST simples com SDK Python oficial.

Outras alternativas populares:
    - Amazon SES (boto3): baixo custo, alta entregabilidade.
    - Mailgun: fácil validação de domínio, bom para transacionais.
    - Resend (resend.com): moderno, suporte a React Email templates.

Para integrar com SendGrid:
    1. Instalar: pip install sendgrid
    2. Configurar: SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
    3. Implementar esta interface usando sendgrid.SendGridAPIClient
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailMessage:
    """Representa uma mensagem de email a ser enviada."""

    to: str
    subject: str
    body_html: str
    body_text: str = ""
    from_email: str = "noreply@gestao.app"
    reply_to: str | None = None


@dataclass(frozen=True)
class EmailResult:
    """Resultado de uma tentativa de envio de email."""

    success: bool
    message_id: str | None = None
    error: str | None = None


class AbstractEmailService(ABC):
    """
    Abstração para serviços de envio de email transacional.

    Implementação real sugerida: SendGrid API.
    Documentação: https://docs.sendgrid.com/api-reference/mail-send/mail-send

    Exemplo de integração com SendGrid:

        class SendGridEmailService(AbstractEmailService):
            def __init__(self) -> None:
                from sendgrid import SendGridAPIClient
                self._client = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])

            async def send(self, message: EmailMessage) -> EmailResult:
                from sendgrid.helpers.mail import Mail
                mail = Mail(
                    from_email=message.from_email,
                    to_emails=message.to,
                    subject=message.subject,
                    html_content=message.body_html,
                )
                response = self._client.send(mail)
                return EmailResult(
                    success=response.status_code in (200, 202),
                    message_id=response.headers.get("X-Message-Id"),
                )
    """

    @abstractmethod
    async def send(self, message: EmailMessage) -> EmailResult:
        """
        Envia um email genérico.

        Args:
            message: Objeto EmailMessage com todos os campos da mensagem.

        Returns:
            EmailResult indicando sucesso ou falha e ID da mensagem.
        """
        raise NotImplementedError

    @abstractmethod
    async def send_welcome(self, to: str, name: str) -> EmailResult:
        """
        Envia email de boas-vindas para um novo usuário.

        Args:
            to: Endereço de email do destinatário.
            name: Nome do usuário para personalização.

        Returns:
            EmailResult indicando sucesso ou falha.
        """
        raise NotImplementedError

    @abstractmethod
    async def send_payment_overdue(
        self,
        to: str,
        company_name: str,
        due_date: str,
        amount: float,
    ) -> EmailResult:
        """
        Envia email de aviso de pagamento em atraso.

        Args:
            to: Endereço de email do responsável pela empresa.
            company_name: Nome da empresa com pagamento em atraso.
            due_date: Data de vencimento do pagamento (formato legível).
            amount: Valor em atraso.

        Returns:
            EmailResult indicando sucesso ou falha.
        """
        raise NotImplementedError

    @abstractmethod
    async def send_account_deactivated(
        self,
        to: str,
        company_name: str,
    ) -> EmailResult:
        """
        Envia email de notificação de conta desativada por inadimplência.

        Args:
            to: Endereço de email do responsável pela empresa.
            company_name: Nome da empresa desativada.

        Returns:
            EmailResult indicando sucesso ou falha.
        """
        raise NotImplementedError

    @abstractmethod
    async def send_password_reset(self, to: str, reset_token: str) -> EmailResult:
        """
        Envia email com link/token para redefinição de senha.

        Args:
            to: Endereço de email do usuário.
            reset_token: Token seguro para redefinição de senha.

        Returns:
            EmailResult indicando sucesso ou falha.
        """
        raise NotImplementedError

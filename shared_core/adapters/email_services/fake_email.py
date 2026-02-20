"""Implementação fake do serviço de email para testes e desenvolvimento.

Esta implementação não envia emails reais. Armazena todas as mensagens
em memória para validação em testes.

Para usar em produção, substitua pela implementação real (ex: SendGridEmailService).
"""

import uuid

from shared_core.adapters.email_services.abstract_email import (
    AbstractEmailService,
    EmailMessage,
    EmailResult,
)


class FakeEmailService(AbstractEmailService):
    """
    Serviço de email fake para testes e desenvolvimento local.

    Todos os emails são armazenados em memória — nenhum email real é enviado.
    A lista `sent` é acessível nos testes para verificar o conteúdo enviado.
    """

    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []

    async def send(self, message: EmailMessage) -> EmailResult:
        """
        Simula o envio de um email genérico, armazenando em memória.

        Args:
            message: Objeto EmailMessage com os dados da mensagem.

        Returns:
            EmailResult com success=True e message_id gerado localmente.
        """
        self.sent.append(message)
        return EmailResult(
            success=True,
            message_id=f"fake_msg_{uuid.uuid4().hex[:12]}",
        )

    async def send_welcome(self, to: str, name: str) -> EmailResult:
        """
        Simula o envio de email de boas-vindas.

        Args:
            to: Endereço de email do destinatário.
            name: Nome do usuário.

        Returns:
            EmailResult com success=True.
        """
        message = EmailMessage(
            to=to,
            subject="Bem-vindo ao sistema de gestão!",
            body_html=f"<h1>Olá, {name}!</h1><p>Sua conta foi criada com sucesso.</p>",
            body_text=f"Olá, {name}! Sua conta foi criada com sucesso.",
        )
        return await self.send(message)

    async def send_payment_overdue(
        self,
        to: str,
        company_name: str,
        due_date: str,
        amount: float,
    ) -> EmailResult:
        """
        Simula o envio de aviso de pagamento em atraso.

        Args:
            to: Endereço de email do responsável.
            company_name: Nome da empresa.
            due_date: Data de vencimento.
            amount: Valor em atraso.

        Returns:
            EmailResult com success=True.
        """
        message = EmailMessage(
            to=to,
            subject=f"[{company_name}] Pagamento em atraso",
            body_html=(
                f"<p>Identificamos um pagamento em atraso de <strong>R$ {amount:.2f}</strong>"
                f" com vencimento em <strong>{due_date}</strong>.</p>"
                f"<p>Por favor, regularize sua situação para evitar a suspensão do acesso.</p>"
            ),
            body_text=(
                f"Pagamento em atraso: R$ {amount:.2f}, vencimento em {due_date}. "
                f"Regularize para evitar suspensão."
            ),
        )
        return await self.send(message)

    async def send_account_deactivated(
        self,
        to: str,
        company_name: str,
    ) -> EmailResult:
        """
        Simula o envio de notificação de conta desativada.

        Args:
            to: Endereço de email do responsável.
            company_name: Nome da empresa desativada.

        Returns:
            EmailResult com success=True.
        """
        message = EmailMessage(
            to=to,
            subject=f"[{company_name}] Conta suspensa por inadimplência",
            body_html=(
                f"<p>A conta da empresa <strong>{company_name}</strong> foi suspensa "
                f"por falta de pagamento.</p>"
                f"<p>Entre em contato com o suporte para regularizar sua situação.</p>"
            ),
            body_text=(
                f"A conta de {company_name} foi suspensa por inadimplência. "
                f"Entre em contato com o suporte."
            ),
        )
        return await self.send(message)

    async def send_password_reset(self, to: str, reset_token: str) -> EmailResult:
        """
        Simula o envio de link para redefinição de senha.

        Args:
            to: Endereço de email do usuário.
            reset_token: Token seguro de redefinição.

        Returns:
            EmailResult com success=True.
        """
        message = EmailMessage(
            to=to,
            subject="Redefinição de senha",
            body_html=(
                f"<p>Você solicitou a redefinição de senha.</p>"
                f"<p>Token: <strong>{reset_token}</strong></p>"
                f"<p>Este token expira em 30 minutos.</p>"
            ),
            body_text=f"Token de redefinição de senha: {reset_token}. Expira em 30 minutos.",
        )
        return await self.send(message)

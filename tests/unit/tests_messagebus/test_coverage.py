"""Testes de cobertura para o messagebus.

Cobre o comportamento do MessageBus ao receber eventos sem handlers registrados,
TypeError ao processar mensagem inválida, e UnitOfWork sem session_factory.
"""

from unittest.mock import MagicMock

import pytest

from messagebus.messagebus import CommandHandlers, Event, EventHandlers, MessageBus


class TestMessageBusEventNoHandlers:
    """Testes para o MessageBus quando não há handlers registrados para um evento."""

    async def test_event_no_handlers(self) -> None:
        """Verifica que eventos sem handlers são ignorados silenciosamente."""

        class FakeEvent(Event):
            """Evento fake sem handlers registrados."""

        uow = MagicMock()
        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({}),
            command_handlers=CommandHandlers({}),
        )

        await bus._handle_event(FakeEvent())


class TestMessageBusTypeError:
    """Testes para o branch TypeError do MessageBus.handle()."""

    async def test_handle_invalid_message_raises_type_error(self) -> None:
        """Verifica que handle() levanta TypeError para mensagem que não é Event nem Command."""
        uow = MagicMock()
        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({}),
            command_handlers=CommandHandlers({}),
        )

        with pytest.raises(TypeError):
            await bus.handle("not_a_message")  # type: ignore[arg-type]


class TestUnitOfWorkDefaultSessionFactory:
    """Testes para o UnitOfWork sem session_factory explícita."""

    def test_uow_uses_default_session_factory(self) -> None:
        """Verifica que UnitOfWork usa default_async_sql_session_factory quando não fornecida."""
        from messagebus.unity_of_work import UnitOfWork

        uow = UnitOfWork(session_factory=None)
        from infra.database import default_async_sql_session_factory

        assert uow.sql_session_factory is default_async_sql_session_factory

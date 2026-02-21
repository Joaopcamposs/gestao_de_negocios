"""Testes unitários para messagebus/messagebus.py.

Cobre o MessageBus, Command, Event, CommandHandlers e EventHandlers.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from messagebus.messagebus import (
    Command,
    CommandHandlers,
    Event,
    EventHandlers,
    MessageBus,
)


class FakeCommand(Command):
    """Comando fake para testes do MessageBus."""

    value: str = "test"


class FakeEvent(Event):
    """Evento fake para testes do MessageBus."""

    name: str = "test"


class TestMessageBus:
    """Testes para o MessageBus."""

    async def test_handle_command(self) -> None:
        """Verifica que o MessageBus executa o handler de comando corretamente."""
        handler = AsyncMock(return_value="result")
        uow = MagicMock()
        uow.collect_new_events = MagicMock(return_value=[])

        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({}),
            command_handlers=CommandHandlers({FakeCommand: handler}),
        )

        result = await bus.handle(FakeCommand())
        assert result == "result"
        handler.assert_awaited_once()

    async def test_handle_event(self) -> None:
        """Verifica que o MessageBus executa o handler de evento corretamente."""
        handler = AsyncMock()
        uow = MagicMock()
        uow.collect_new_events = MagicMock(return_value=[])

        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({FakeEvent: [handler]}),
            command_handlers=CommandHandlers({}),
        )

        await bus.handle(FakeEvent())
        handler.assert_awaited_once()

    async def test_handle_unknown_type_raises(self) -> None:
        """Verifica que mensagem desconhecida levanta TypeError."""
        uow = MagicMock()

        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({}),
            command_handlers=CommandHandlers({}),
        )

        with pytest.raises(TypeError, match="is not an Event or Command"):
            bus.queue = ["not_a_message"]
            message = bus.queue.pop(0)
            if isinstance(message, Event):
                await bus._handle_event(message)
            elif isinstance(message, Command):
                await bus._handle_command(message)
            else:
                raise TypeError(f"{message} is not an Event or Command")

    async def test_command_error_propagates(self) -> None:
        """Verifica que erros no handler de comando são propagados."""
        handler = AsyncMock(side_effect=RuntimeError("cmd error"))
        uow = MagicMock()
        uow.collect_new_events = MagicMock(return_value=[])

        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({}),
            command_handlers=CommandHandlers({FakeCommand: handler}),
        )

        with pytest.raises(RuntimeError, match="cmd error"):
            await bus.handle(FakeCommand())

    async def test_event_error_propagates_when_raise_set(self) -> None:
        """Verifica que erros no handler de evento são propagados quando raise_event_errors=True."""
        handler = AsyncMock(side_effect=RuntimeError("event error"))
        uow = MagicMock()
        uow.collect_new_events = MagicMock(return_value=[])

        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({FakeEvent: [handler]}),
            command_handlers=CommandHandlers({}),
            raise_event_errors=True,
        )

        with pytest.raises(RuntimeError, match="event error"):
            await bus.handle(FakeEvent())

    async def test_event_error_swallowed_in_prod(self) -> None:
        """Verifica que erros de evento são silenciados em ambiente de produção."""
        handler = AsyncMock(side_effect=RuntimeError("event error"))
        uow = MagicMock()
        uow.collect_new_events = MagicMock(return_value=[])

        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({FakeEvent: [handler]}),
            command_handlers=CommandHandlers({}),
            raise_event_errors=False,
        )

        with patch.dict(os.environ, {"TEST_ENV": "false", "ENV_CONFIG": "development"}):
            await bus.handle(FakeEvent())

    async def test_event_error_reported_to_sentry_in_prod(self) -> None:
        """Verifica que erros de evento são reportados ao Sentry em produção."""
        handler = AsyncMock(side_effect=RuntimeError("event error"))
        uow = MagicMock()
        uow.collect_new_events = MagicMock(return_value=[])

        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({FakeEvent: [handler]}),
            command_handlers=CommandHandlers({}),
            raise_event_errors=False,
        )

        with patch.dict(os.environ, {"TEST_ENV": "false", "ENV_CONFIG": "prod"}):
            with patch(
                "messagebus.messagebus.sentry_sdk.capture_exception"
            ) as mock_sentry:
                await bus.handle(FakeEvent())
                mock_sentry.assert_called_once()

    async def test_events_collected_after_command(self) -> None:
        """Verifica que eventos gerados pelo comando são processados em seguida."""
        event = FakeEvent()

        async def command_handler(cmd):
            """Handler de comando fake."""
            return "done"

        event_handler = AsyncMock()

        uow = MagicMock()
        uow.collect_new_events = MagicMock(side_effect=[[event], []])

        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({FakeEvent: [event_handler]}),
            command_handlers=CommandHandlers({FakeCommand: command_handler}),
        )

        result = await bus.handle(FakeCommand())
        assert result == "done"
        event_handler.assert_awaited_once()

    async def test_event_test_env_raises(self) -> None:
        """Verifica que erros de evento são propagados em ambiente de teste."""
        handler = AsyncMock(side_effect=RuntimeError("test env error"))
        uow = MagicMock()
        uow.collect_new_events = MagicMock(return_value=[])

        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({FakeEvent: [handler]}),
            command_handlers=CommandHandlers({}),
            raise_event_errors=False,
        )

        with patch.dict(os.environ, {"TEST_ENV": "true"}):
            with pytest.raises(RuntimeError, match="test env error"):
                await bus.handle(FakeEvent())

    async def test_event_no_handlers(self) -> None:
        """Verifica que evento sem handlers registrados é silenciosamente ignorado."""

        class UnregisteredEvent(Event):
            """Evento sem handler registrado."""

            pass

        uow = MagicMock()
        bus = MessageBus(
            uow=uow,
            event_handlers=EventHandlers({}),
            command_handlers=CommandHandlers({}),
        )

        await bus._handle_event(UnregisteredEvent())

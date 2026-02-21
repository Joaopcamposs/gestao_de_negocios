"""Testes unitários para messagebus/bootstrap.py.

Cobre bootstrap_base e inject_dependencies do messagebus.
"""

from unittest.mock import MagicMock

from messagebus.bootstrap import bootstrap_base, inject_dependencies
from messagebus.messagebus import (
    Command,
    CommandHandlers,
    Event,
    EventHandlers,
    MessageBus,
)


class FakeCommand(Command):
    """Comando fake para testes de bootstrap."""

    value: str = "test"


class FakeEvent(Event):
    """Evento fake para testes de bootstrap."""

    value: str = "test"


class TestBootstrapBase:
    """Testes para a função bootstrap_base do messagebus."""

    def test_bootstrap_returns_messagebus(self) -> None:
        """Verifica que bootstrap_base retorna uma instância de MessageBus."""
        uow = MagicMock()

        async def fake_handler(cmd, uow):
            """Handler de comando fake."""
            pass

        async def fake_event_handler(event, uow):
            """Handler de evento fake."""
            pass

        command_handlers = CommandHandlers({FakeCommand: fake_handler})
        event_handlers = EventHandlers({FakeEvent: [fake_event_handler]})

        bus = bootstrap_base(
            uow=uow,
            command_handlers=command_handlers,
            event_handlers=event_handlers,
        )

        assert isinstance(bus, MessageBus)
        assert bus.uow == uow

    def test_bootstrap_with_raise_event_errors(self) -> None:
        """Verifica que raise_event_errors é repassado corretamente ao MessageBus."""
        uow = MagicMock()
        command_handlers = CommandHandlers({})
        event_handlers = EventHandlers({})

        bus = bootstrap_base(
            uow=uow,
            command_handlers=command_handlers,
            event_handlers=event_handlers,
            raise_event_errors=True,
        )

        assert bus.raise_event_errors is True


class TestInjectDependencies:
    """Testes para a função inject_dependencies do messagebus."""

    async def test_inject_uow_dependency(self) -> None:
        """Verifica que inject_dependencies injeta o UoW corretamente no handler."""
        mock_uow = MagicMock()
        call_args = {}

        async def handler(message, uow):
            """Handler que captura o uow injetado."""
            call_args["uow"] = uow

        injected = inject_dependencies(handler, {"uow": mock_uow})

        fake_cmd = FakeCommand()
        await injected(fake_cmd)

        assert call_args["uow"] == mock_uow

    async def test_inject_no_matching_dependency(self) -> None:
        """Verifica que handler sem parâmetro uow é chamado normalmente."""
        called = False

        async def handler(message):
            """Handler sem dependências injetadas."""
            nonlocal called
            called = True

        injected = inject_dependencies(handler, {"uow": MagicMock()})
        await injected(FakeCommand())

        assert called is True

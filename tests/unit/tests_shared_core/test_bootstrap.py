"""Testes unitários para shared_core/bootstrap.py.

Cobre a função bootstrap do shared_core com diferentes configurações.
"""

from unittest.mock import MagicMock, patch

from messagebus.messagebus import CommandHandlers, EventHandlers, MessageBus
from shared_core.bootstrap import bootstrap


class TestSharedBootstrap:
    """Testes para a função bootstrap do shared_core."""

    def test_bootstrap_with_custom_uow(self) -> None:
        """Verifica que bootstrap retorna MessageBus com UoW customizado."""
        mock_uow = MagicMock()
        bus = bootstrap(uow=mock_uow)

        assert isinstance(bus, MessageBus)
        assert bus.uow == mock_uow

    def test_bootstrap_with_custom_handlers(self) -> None:
        """Verifica que bootstrap aceita handlers customizados."""
        mock_uow = MagicMock()
        custom_cmd = CommandHandlers({})
        custom_evt = EventHandlers({})

        bus = bootstrap(
            uow=mock_uow,
            command_handlers=custom_cmd,
            event_handlers=custom_evt,
        )

        assert isinstance(bus, MessageBus)

    @patch("shared_core.bootstrap.UnitOfWork")
    def test_bootstrap_creates_default_uow(self, MockUoW) -> None:
        """Verifica que bootstrap cria UoW padrão quando não fornecido."""
        mock_uow_instance = MagicMock()
        MockUoW.return_value = mock_uow_instance

        bus = bootstrap(
            user=MagicMock(),
            schema="test_schema",
            service_type="dentist",
        )

        assert isinstance(bus, MessageBus)
        MockUoW.assert_called_once()

    def test_bootstrap_with_raise_event_errors(self) -> None:
        """Verifica que raise_event_errors é repassado corretamente ao MessageBus."""
        mock_uow = MagicMock()
        bus = bootstrap(uow=mock_uow, raise_event_errors=True)

        assert bus.raise_event_errors is True

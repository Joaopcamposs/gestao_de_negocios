"""Testes unitários para os bootstraps dos serviços dentist e lawyer.

Cobre bootstrap_dentist e bootstrap_lawyer com diferentes configurações.
"""

from unittest.mock import MagicMock, patch

from messagebus.messagebus import CommandHandlers, EventHandlers, MessageBus


class TestDentistBootstrap:
    """Testes para a função bootstrap_dentist."""

    def test_bootstrap_dentist_with_custom_uow(self) -> None:
        """Verifica que bootstrap_dentist retorna MessageBus com UoW customizado."""
        from services.dentist.bootstrap import bootstrap_dentist

        mock_uow = MagicMock()
        bus = bootstrap_dentist(uow=mock_uow)

        assert isinstance(bus, MessageBus)
        assert bus.uow == mock_uow

    def test_bootstrap_dentist_default_uow(self) -> None:
        """Verifica que bootstrap_dentist cria UoW padrão quando não fornecido."""
        from services.dentist.bootstrap import bootstrap_dentist

        with patch("services.dentist.bootstrap.UnitOfWork") as MockUoW:
            mock_uow = MagicMock()
            MockUoW.return_value = mock_uow

            bus = bootstrap_dentist(user=MagicMock())
            assert isinstance(bus, MessageBus)
            MockUoW.assert_called_once()

    def test_bootstrap_dentist_custom_handlers(self) -> None:
        """Verifica que bootstrap_dentist aceita handlers customizados."""
        from services.dentist.bootstrap import bootstrap_dentist

        mock_uow = MagicMock()
        custom_cmd = CommandHandlers({})
        custom_evt = EventHandlers({})

        bus = bootstrap_dentist(
            uow=mock_uow,
            command_handlers=custom_cmd,
            event_handlers=custom_evt,
        )
        assert isinstance(bus, MessageBus)

    def test_bootstrap_dentist_raise_events(self) -> None:
        """Verifica que raise_event_errors é repassado corretamente ao MessageBus."""
        from services.dentist.bootstrap import bootstrap_dentist

        mock_uow = MagicMock()
        bus = bootstrap_dentist(uow=mock_uow, raise_event_errors=True)
        assert bus.raise_event_errors is True


class TestLawyerBootstrap:
    """Testes para a função bootstrap_lawyer."""

    def test_bootstrap_lawyer_with_custom_uow(self) -> None:
        """Verifica que bootstrap_lawyer retorna MessageBus com UoW customizado."""
        from services.lawyer.bootstrap import bootstrap_lawyer

        mock_uow = MagicMock()
        bus = bootstrap_lawyer(uow=mock_uow)

        assert isinstance(bus, MessageBus)
        assert bus.uow == mock_uow

    def test_bootstrap_lawyer_default_uow(self) -> None:
        """Verifica que bootstrap_lawyer cria UoW padrão quando não fornecido."""
        from services.lawyer.bootstrap import bootstrap_lawyer

        with patch("services.lawyer.bootstrap.UnitOfWork") as MockUoW:
            mock_uow = MagicMock()
            MockUoW.return_value = mock_uow

            bus = bootstrap_lawyer(user=MagicMock())
            assert isinstance(bus, MessageBus)
            MockUoW.assert_called_once()

    def test_bootstrap_lawyer_custom_handlers(self) -> None:
        """Verifica que bootstrap_lawyer aceita handlers customizados."""
        from services.lawyer.bootstrap import bootstrap_lawyer

        mock_uow = MagicMock()
        custom_cmd = CommandHandlers({})
        custom_evt = EventHandlers({})

        bus = bootstrap_lawyer(
            uow=mock_uow,
            command_handlers=custom_cmd,
            event_handlers=custom_evt,
        )
        assert isinstance(bus, MessageBus)

    def test_bootstrap_lawyer_raise_events(self) -> None:
        """Verifica que raise_event_errors é repassado corretamente ao MessageBus."""
        from services.lawyer.bootstrap import bootstrap_lawyer

        mock_uow = MagicMock()
        bus = bootstrap_lawyer(uow=mock_uow, raise_event_errors=True)
        assert bus.raise_event_errors is True

"""Testes de cobertura para os serviços dentist e lawyer.

Cobre importação dos módulos main, health_check e lifespan dos serviços.
"""

from unittest.mock import AsyncMock, patch


class TestDentistMain:
    """Testes para o módulo main do serviço dentist."""

    def test_import(self) -> None:
        """Verifica que o módulo main do dentist importa corretamente."""
        import services.dentist.main as dentist_main

        assert hasattr(dentist_main, "app")

    async def test_health_check(self) -> None:
        """Verifica que o endpoint health_check retorna mensagem correta."""
        from services.dentist.main import health_check

        result = await health_check()
        assert result == {"message": "Dentist Service is running!"}

    async def test_lifespan(self) -> None:
        """Verifica que o lifespan do dentist chama create_first_company_and_user."""
        from services.dentist.main import lifespan, app

        with patch(
            "infra.database.initializers.create_first_company_and_user",
            new_callable=AsyncMock,
        ) as mock_init:
            async with lifespan(app):
                pass
            mock_init.assert_awaited_once_with(service_type="dentist")


class TestLawyerMain:
    """Testes para o módulo main do serviço lawyer."""

    def test_import(self) -> None:
        """Verifica que o módulo main do lawyer importa corretamente."""
        import services.lawyer.main as lawyer_main

        assert hasattr(lawyer_main, "app")

    async def test_health_check(self) -> None:
        """Verifica que o endpoint health_check retorna mensagem correta."""
        from services.lawyer.main import health_check

        result = await health_check()
        assert result == {"message": "Lawyer Service is running!"}

    async def test_lifespan(self) -> None:
        """Verifica que o lifespan do lawyer chama create_first_company_and_user."""
        from services.lawyer.main import lifespan, app

        with patch(
            "infra.database.initializers.create_first_company_and_user",
            new_callable=AsyncMock,
        ) as mock_init:
            async with lifespan(app):
                pass
            mock_init.assert_awaited_once_with(service_type="lawyer")

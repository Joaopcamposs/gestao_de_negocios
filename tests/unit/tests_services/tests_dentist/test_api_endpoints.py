"""Testes unitários para os endpoints da API do serviço Dentist."""

from unittest.mock import AsyncMock, MagicMock, patch

import uuid7

_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


def _make_mock_user():
    """Cria um usuário mockado para testes de API."""
    user = MagicMock()
    user.id = _USER_ID
    user.company = _COMPANY_ID
    user.email = "test@test.com"
    user.cpf = "12345678901"
    user.name = "Test"
    user.phone = "11999"
    user.admin = False
    user.active = True
    user.is_owner = False
    return user


class TestDentistPatientAPI:
    """Testes para os endpoints de Patient do serviço Dentist."""

    @patch("services.dentist.entrypoints.api.patient.bootstrap_dentist")
    @patch("services.dentist.entrypoints.api.patient.current_user")
    async def test_post_patient(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que POST /patient cria um paciente com sucesso."""
        from services.dentist.entrypoints.api.patient import post_patient
        from services.dentist.entrypoints.schemas.patient import CreatePatientSchema

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(return_value=uuid7.create())
        mock_bootstrap.return_value = mock_bus

        body = CreatePatientSchema(name="Patient", cpf="12345678901")

        result = await post_patient(body)
        assert result is not None

    @patch("services.dentist.entrypoints.api.patient.bootstrap_dentist")
    @patch("services.dentist.entrypoints.api.patient.current_user")
    async def test_put_patient(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que PUT /patient atualiza um paciente com sucesso."""
        from services.dentist.entrypoints.api.patient import put_patient
        from services.dentist.entrypoints.schemas.patient import UpdatePatientSchema

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bootstrap.return_value = mock_bus

        body = UpdatePatientSchema(cpf="12345678901", new_name="New")
        await put_patient(body)
        mock_bus.handle.assert_awaited_once()

    @patch(
        "services.dentist.entrypoints.api.patient.view_patient", new_callable=AsyncMock
    )
    @patch("services.dentist.entrypoints.api.patient.UnitOfWork")
    @patch("services.dentist.entrypoints.api.patient.current_user")
    async def test_get_patient(self, mock_ctx, MockUoW, mock_view) -> None:
        """Verifica que GET /patient retorna lista de pacientes."""
        from services.dentist.entrypoints.api.patient import get_patient

        mock_ctx.get.return_value = _make_mock_user()
        mock_view.return_value = []

        result = await get_patient()
        assert result == []

    @patch("services.dentist.entrypoints.api.patient.bootstrap_dentist")
    @patch("services.dentist.entrypoints.api.patient.current_user")
    async def test_delete_patient(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que DELETE /patient remove um paciente com sucesso."""
        from services.dentist.entrypoints.api.patient import delete_patient_endpoint

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bootstrap.return_value = mock_bus

        await delete_patient_endpoint("12345678901")
        mock_bus.handle.assert_awaited_once()

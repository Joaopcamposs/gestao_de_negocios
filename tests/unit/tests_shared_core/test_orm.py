"""Testes unitários para a inicialização do ORM e módulos de main dos serviços."""


class TestORMInit:
    """Testes para a inicialização do módulo ORM."""

    def test_orm_module_has_mappers(self) -> None:
        """Verifica que o módulo ORM importa sem erros."""
        import shared_core.adapters.orm as orm_module

        assert hasattr(orm_module, "__name__")


class TestDentistMain:
    """Testes para o módulo main do serviço Dentist."""

    def test_import(self) -> None:
        """Verifica que o módulo main do Dentist importa sem erros."""
        import services.dentist.main as dentist_main

        assert hasattr(dentist_main, "app")


class TestLawyerMain:
    """Testes para o módulo main do serviço Lawyer."""

    def test_import(self) -> None:
        """Verifica que o módulo main do Lawyer importa sem erros."""
        import services.lawyer.main as lawyer_main

        assert hasattr(lawyer_main, "app")

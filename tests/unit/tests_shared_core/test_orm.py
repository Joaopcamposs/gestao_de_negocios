"""Testes unitários para a inicialização do ORM e módulos de main dos serviços."""


class TestORMInit:
    """Testes para a inicialização do módulo ORM."""

    def test_orm_module_has_mappers(self) -> None:
        """Verifica que o módulo ORM importa e start_mappers() executa sem erros."""
        import shared_core.adapters.orm as orm_module

        assert hasattr(orm_module, "__name__")
        orm_module.start_mappers()

"""Módulo de registro de handlers de comandos e eventos do contexto advogado.

Combina os handlers do shared_core (user, company, auth) com os handlers
específicos do contexto advogado (legal_case).
"""

from messagebus.messagebus import CommandHandlers, EventHandlers
from services.lawyer.domain.commands.legal_case import (
    CreateLegalCase,
    DeleteLegalCase,
    UpdateLegalCase,
)
from services.lawyer.domain.events.legal_case import (
    LegalCaseCreated,
    LegalCaseDeleted,
    LegalCaseUpdated,
)
from services.lawyer.services.handlers.legal_case import (
    create_legal_case,
    delete_legal_case,
    legal_case_created,
    legal_case_deleted,
    legal_case_updated,
    update_legal_case,
)
from shared_core.handlers import (
    COMMAND_HANDLERS as CORE_COMMAND_HANDLERS,
    EVENT_HANDLERS as CORE_EVENT_HANDLERS,
)
from shared_core.services.handlers.audit_log import (
    audit_entity_created,
    audit_entity_deleted,
    audit_entity_updated,
)

COMMAND_HANDLERS: CommandHandlers = CommandHandlers(
    {
        **CORE_COMMAND_HANDLERS,
        CreateLegalCase: create_legal_case,
        UpdateLegalCase: update_legal_case,
        DeleteLegalCase: delete_legal_case,
    }
)

EVENT_HANDLERS: EventHandlers = EventHandlers(
    {
        **CORE_EVENT_HANDLERS,
        LegalCaseCreated: [legal_case_created, audit_entity_created],
        LegalCaseUpdated: [legal_case_updated, audit_entity_updated],
        LegalCaseDeleted: [legal_case_deleted, audit_entity_deleted],
    }
)

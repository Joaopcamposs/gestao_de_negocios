"""Módulo de registro de handlers de comandos e eventos do contexto dentista.

Combina os handlers do shared_core (user, company, auth) com os handlers
específicos do contexto dentista (patient).
"""

from messagebus.messagebus import CommandHandlers, EventHandlers
from services.dentist.domain.commands.patient import (
    CreatePatient,
    DeletePatient,
    UpdatePatient,
)
from services.dentist.domain.events.patient import (
    PatientCreated,
    PatientDeleted,
    PatientUpdated,
)
from services.dentist.services.handlers.patient import (
    create_patient,
    delete_patient,
    patient_created,
    patient_deleted,
    patient_updated,
    update_patient,
)
from shared_core.handlers import (
    COMMAND_HANDLERS as CORE_COMMAND_HANDLERS,
    EVENT_HANDLERS as CORE_EVENT_HANDLERS,
)

# Combina handlers do core com handlers específicos do dentista
COMMAND_HANDLERS: CommandHandlers = CommandHandlers(
    {
        **CORE_COMMAND_HANDLERS,
        CreatePatient: create_patient,
        UpdatePatient: update_patient,
        DeletePatient: delete_patient,
    }
)

EVENT_HANDLERS: EventHandlers = EventHandlers(
    {
        **CORE_EVENT_HANDLERS,
        PatientCreated: [patient_created],
        PatientUpdated: [patient_updated],
        PatientDeleted: [patient_deleted],
    }
)

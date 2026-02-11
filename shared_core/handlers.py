"""Módulo de registro de handlers de comandos e eventos."""

from shared_core.domain.commands.company import (
    CreateCompany,
    DeleteCompany,
    UpdateCompany,
)
from shared_core.domain.commands.security import AuthenticateUser
from shared_core.domain.commands.user import (
    CreateUser,
    DeleteUser,
    UpdateUser,
)
from shared_core.domain.events.company import (
    CompanyCreated,
    CompanyDeleted,
    CompanyUpdated,
)
from shared_core.domain.events.user import (
    TimeToCreateCompanyAdminUser,
    TimeToCreateInitialCompanyUser,
    UserCreated,
    UserDeleted,
    UserUpdated,
)
from shared_core.services.handlers.company import (
    company_created,
    company_deleted,
    company_updated,
    create_company,
    delete_company,
    update_company,
)
from shared_core.services.handlers.security import authenticate_user
from shared_core.services.handlers.user import (
    create_public_user,
    create_user,
    delete_user,
    remove_public_user,
    update_public_user,
    update_user,
    user_created,
    user_deleted,
    user_updated,
)
from messagebus.messagebus import CommandHandlers, EventHandlers

COMMAND_HANDLERS: CommandHandlers = CommandHandlers(
    {
        CreateCompany: create_company,
        UpdateCompany: update_company,
        DeleteCompany: delete_company,
        CreateUser: create_user,
        UpdateUser: update_user,
        DeleteUser: delete_user,
        AuthenticateUser: authenticate_user,
    }
)

EVENT_HANDLERS: EventHandlers = EventHandlers(
    {
        CompanyCreated: [company_created],
        CompanyUpdated: [company_updated],
        CompanyDeleted: [company_deleted],
        UserCreated: [user_created, create_public_user],
        UserUpdated: [user_updated, update_public_user],
        UserDeleted: [user_deleted, remove_public_user],
        TimeToCreateInitialCompanyUser: [create_user],
        TimeToCreateCompanyAdminUser: [create_user],
    }
)

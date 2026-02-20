"""Módulo de registro de handlers de comandos e eventos."""

from shared_core.domain.commands.company import (
    CreateCompany,
    DeleteCompany,
    UpdateCompany,
)
from shared_core.domain.commands.credit_card import CreateCreditCard, DeleteCreditCard
from shared_core.domain.commands.payment import (
    CheckAndDeactivateOverdueCompanies,
    CreatePayment,
    MarkPaymentAsOverdue,
    MarkPaymentAsPaid,
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
    CompanyPaymentStatusUpdated,
    CompanyUpdated,
)
from shared_core.domain.events.credit_card import CreditCardCreated, CreditCardDeleted
from shared_core.domain.events.payment import (
    CompanyAndUsersDeactivated,
    CompanyPaymentOverdue,
    CompanyPaymentPaid,
    PaymentCreated,
    PaymentUpdated,
)
from shared_core.domain.events.user import (
    TimeToCreateCompanyAdminUser,
    TimeToCreateInitialCompanyUser,
    UserCreated,
    UserDeleted,
    UserUpdated,
)
from shared_core.services.handlers.audit_log import (
    audit_entity_created,
    audit_entity_deleted,
    audit_entity_updated,
)
from shared_core.services.handlers.company import (
    company_created,
    company_deleted,
    company_updated,
    create_company,
    delete_company,
    update_company,
)
from shared_core.services.handlers.credit_card import (
    create_credit_card,
    credit_card_created,
    credit_card_deleted,
    delete_credit_card,
)
from shared_core.services.handlers.payment import (
    check_and_deactivate_overdue_companies,
    company_and_users_deactivated,
    company_payment_overdue,
    company_payment_paid,
    create_payment,
    mark_payment_as_overdue,
    mark_payment_as_paid,
    payment_created,
    payment_updated,
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
        CreateCreditCard: create_credit_card,
        DeleteCreditCard: delete_credit_card,
        CreatePayment: create_payment,
        MarkPaymentAsPaid: mark_payment_as_paid,
        MarkPaymentAsOverdue: mark_payment_as_overdue,
        CheckAndDeactivateOverdueCompanies: check_and_deactivate_overdue_companies,
    }
)

EVENT_HANDLERS: EventHandlers = EventHandlers(
    {
        CompanyCreated: [company_created, audit_entity_created],
        CompanyUpdated: [company_updated, audit_entity_updated],
        CompanyDeleted: [company_deleted, audit_entity_deleted],
        CompanyPaymentStatusUpdated: [audit_entity_updated],
        UserCreated: [user_created, create_public_user, audit_entity_created],
        UserUpdated: [user_updated, update_public_user, audit_entity_updated],
        UserDeleted: [user_deleted, remove_public_user, audit_entity_deleted],
        TimeToCreateInitialCompanyUser: [create_user],
        TimeToCreateCompanyAdminUser: [create_user],
        CreditCardCreated: [credit_card_created, audit_entity_created],
        CreditCardDeleted: [credit_card_deleted, audit_entity_deleted],
        PaymentCreated: [payment_created, audit_entity_created],
        PaymentUpdated: [payment_updated, audit_entity_updated],
        CompanyPaymentPaid: [company_payment_paid],
        CompanyPaymentOverdue: [company_payment_overdue],
        CompanyAndUsersDeactivated: [company_and_users_deactivated],
    }
)

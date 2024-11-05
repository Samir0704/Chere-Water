from aiogram.fsm.state import State, StatesGroup

class LegalRegisterState(StatesGroup):
    company_name = State()
    employee_name = State()
    company_contact = State()
    employee_count = State()
    duration_days = State()
    working_days = State()
    password = State()

class IndividualRegisterState(StatesGroup):
    full_name = State()
    contact = State()
    password = State()

class LoginStates(StatesGroup):
    phone = State()
    password = State()

class LegalAddressReminderState(StatesGroup):
    order_address = State()
    reminder_days = State()

class IndividualAddressReminderState(StatesGroup):
    order_address = State()
    reminder_days = State()
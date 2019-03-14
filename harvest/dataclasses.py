from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Auth:
    auth_type: str

@dataclass
class PersonalAccessToken(Auth):
    account_id: str
    access_token: str
    put_auth_in_header: bool

    def __init__(self, account_id, access_token, put_auth_in_header= True):
        super().__init__('Personal Access Token')
        self.account_id = account_id
        if access_token.find('Bearer') > -1:
            self.access_token = access_token
        else:
            self.access_token = 'Bearer ' + access_token

        self.put_auth_in_header = put_auth_in_header

# Authorization Code Flow
@dataclass
class OAuth2_ServerSide_Token():
    access_token: str
    refresh_token: str
    expires_in: int
    expires_at: float

    def __init__(self, access_token, refresh_token, expires_in, expires_at, refresh_url=None):
        if access_token.upper().find('BEARER ') > -1:
            self.access_token = access_token
        else:
            self.access_token = 'Bearer ' + access_token

        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.expires_at = expires_at
        self.refresh_url = refresh_url

# Authorization Code Flow
@dataclass
class OAuth2_ServerSide(Auth):
    """Implicit Code Grant Flow for OAuth2"""
    refresh_url: Optional[str]
    client_id: str
    client_secret: str
    token: OAuth2_ServerSide_Token

    def __init__(self, client_id, client_secret, token, refresh_url):
        super().__init__(auth_type = 'Server Side Applications')
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token
        self.refresh_url = refresh_url

# Implicit Code Flow
@dataclass
class OAuth2_ClientSide_Token():
    access_token: str
    expires_in: int
    token_type: str
    scope: List[str]

    def __init__(self, access_token, expires_in, token_type, scope):
        if access_token.upper().find('BEARER') > -1:
            self.access_token = access_token
        else:
            self.access_token = 'Bearer ' + access_token

        self.expires_in = expires_in
        self.token_type = token_type
        self.scope = scope

# # Implicit Code Flow
# @dataclass
# class OAuth2_ClientSide(Auth):
#     """Authorizaton Code Grant Flow for OAuth2"""
#     token: Optional[OAuth2_ClientSide_Token]
#     client_id: str
#     auth_url: str
#     # scopes: List[str]
#
#     def __init__(self, client_id, auth_url):
#         super().__init__('Client Side Applications')
#         self.client_id = client_id
#         self.auth_url = auth_url

@dataclass
class ErrorMessage:
    message: str

@dataclass
class Company:
    base_uri: str = None
    full_domain: str = None
    name: str = None
    is_active: bool = False
    week_start_day: str = None
    wants_timestamp_timers: bool = False
    time_format: str = None
    plan_type: str = None
    expense_feature: bool = False
    invoice_feature: bool = False
    estimate_feature: bool = False
    approval_required: bool = False
    clock: str = None
    decimal_symbol: str = None
    thousands_separator: str = None
    color_scheme: str = None

@dataclass
class ExpenseCategory:
    unit_name: Optional[str]
    unit_price: Optional[float]
    id: int = None
    name: str = None
    is_active: bool = False
    created_at: str = None
    updated_at: str = None

@dataclass
class InvoiceRef:
    id: int = None
    number: str = None

@dataclass
class Receipt:
    url: str = None
    file_name: str = None
    file_size: int = None
    content_type: str = None

@dataclass
class User:
    id: int = None
    name: str = None

@dataclass
class ClientRef:
    id: int = None
    name: str = None

@dataclass
class Client:
    address: Optional[str]
    id: int = None
    name: str = None
    currency: str = None
    is_active: bool = None
    created_at: str = None
    updated_at: str = None


@dataclass
class UserAssignment:
    budget: Optional[float]
    id: int = None
    is_project_manager: bool = None
    is_active: bool = None
    created_at: str = None
    updated_at: str = None
    hourly_rate: float = None

@dataclass
class Project:
    code: Optional[str]
    id: int = None
    name: str = None

@dataclass
class Expense:
    locked_reason: Optional[str]
    user: Optional[User]
    receipt: Optional[Receipt]
    invoice: Optional[InvoiceRef]
    project: Optional[Project]
    notes: Optional[str]
    id: int = None
    total_cost: float = None
    units: float = None
    is_closed: bool = False
    is_locked: bool = False
    is_billed: bool = False
    spent_date: str = None
    created_at: str = None
    updated_at: str = None
    billable: bool = True
    user_assignment: UserAssignment = None
    expense_category: ExpenseCategory = None
    client: Client = None

@dataclass
class LineItem:
    project: Optional[Project]
    id: int = None
    kind: str = None
    description: str = None
    quantity: float = None
    unit_price: float = None
    amount: float = None
    taxed: bool = None
    taxed2: bool = None

@dataclass
class ExpenseImport:
    summary_type: str
    #from: str = None
    to: str = None
    attach_receipt: str = None

@dataclass
class TimeImport:
    summary_type: str
    #from: str = None
    to: str = None

@dataclass
class LineItemImport:
    time: Optional[TimeImport]
    expenses: Optional[ExpenseImport]
    project_ids: List[Project]

@dataclass
class Creator:
    id: int = None
    name: str = None

@dataclass
class Estimate:
    purchase_order: Optional[str]
    tax: Optional[float]
    tax_amount: Optional[float]
    tax2: Optional[float]
    tax2_amount: Optional[float]
    discount: Optional[float]
    discount_amount: Optional[float]
    sent_at: Optional[str]
    accepted_at: Optional[str]
    declined_at: Optional[str]
    line_items: List[LineItem]
    notes: Optional[str]
    id: int = None
    client_key: str = None
    number: str = None
    amount: float = None
    subject: str = None
    state: str = None
    issue_date: str = None
    due_date: str = None
    created_at: str = None
    updated_at: str = None
    currency: str = None
    creator: Creator = None

@dataclass
class Invoice:
    purchase_order: Optional[str]
    tax: Optional[float]
    tax_amount: Optional[float]
    tax2: Optional[float]
    tax2_amount: Optional[float]
    discount: Optional[float]
    discount_amount: Optional[float]
    period_start: Optional[str]
    period_end: Optional[str]
    paid_date: Optional[str]
    closed_at: Optional[str]
    paid_at: Optional[str]
    estimate: Optional[Estimate]
    retainer: Optional[str]
    sent_at: Optional[str]
    line_items: Optional[List[LineItem]]
    notes: Optional[str]
    id: int = None
    client_key: str = None
    number: str = None
    amount: float = None
    due_amount: float = None
    subject: str = None
    state: str = None
    issue_date: str = None
    due_date: str = None
    payment_term: str = None
    created_at: str = None
    updated_at: str = None
    currency: str = None
    creator: Creator = None
    client: ClientRef = None

@dataclass
class FreeFormInvoice:
    notes: Optional[str]
    client_id: int
    retainer_id: int = None
    estimate_id: int = None
    number: str = None
    purchase_order: str = None
    tax: float = None
    tax2: float = None
    discount: float = None
    subject: str = None
    currency: str = None
    issue_date: str = None
    due_date: str = None
    payment_term: str = None
    line_items: List[LineItem] = None
@dataclass
class InvoiceImport:
    notes: Optional[str]
    line_items_import: Optional[LineItemImport]
    client_id: int
    retainer_id: int = None
    estimate_id: int = None
    number: str = None
    purchase_order: str = None
    tax: float = None
    tax2: float = None
    discount: float = None
    subject: str = None
    currency: str = None
    issue_date: str = None
    due_date: str = None
    payment_term: str = None

@dataclass
class ClientContact:
    title: Optional[str]
    last_name: Optional[str]
    id: int = None
    first_name: str = None
    email: str = None
    phone_office: str = None
    phone_mobile: str = None
    fax: str = None
    created_at: str = None
    updated_at: str = None
    client: Client = None

@dataclass
class Recipient:
    name: str = None
    email: str = None

@dataclass
class InvoiceMessage:
    send_reminder_on: Optional[bool]
    event_type: Optional[str]
    recipients: List[Recipient]
    subject: Optional[str]
    body: Optional[str]
    id: int = None
    sent_by: str = None
    sent_by_email: str = None
    sent_from: str = None
    sent_from_email: str = None
    include_link_to_client_invoice: bool = None
    send_me_a_copy: bool = None
    thank_you: bool = None
    reminder: bool = None
    created_at: str = None
    updated_at: str = None
    attach_pdf: bool = None

@dataclass
class PaymentGateway:
    id: Optional[int]
    name: Optional[str]

@dataclass
class InvoicePayment:
    transaction_id: Optional[str]
    payment_gateway: Optional[PaymentGateway]
    id: int = None
    amount: float = None
    paid_at: str = None
    paid_date: str = None
    recorded_by: str = None
    recorded_by_email: str = None
    notes: str = None
    created_at: str = None
    updated_at: str = None

@dataclass
class InvoiceItemCategory:
    id: int = None
    name: str = None
    use_as_service: bool = None
    use_as_expense: bool = None
    created_at: str = None
    updated_at: str = None

@dataclass
class EstimateMessage:
    event_type: Optional[str]
    subject: Optional[str]
    body: Optional[str]
    recipients: List[Recipient]
    id: int = None
    sent_by: str = None
    sent_by_email: str = None
    sent_from: str = None
    sent_from_email: str = None
    send_me_a_copy: bool = None
    created_at: str = None
    updated_at: str = None

@dataclass
class EstimateItemCategory:
    id: int = None
    name: str = None
    created_at: str = None
    updated_at: str = None

@dataclass
class TaskRef:
    id: str = None
    name: str = None

@dataclass
class Task:
    default_hourly_rate: Optional[float]
    id: int = None
    name: str = None
    billable_by_default: bool = None
    is_default: bool = None
    is_active: bool = None
    created_at: str = None
    updated_at: str = None

@dataclass
class TaskAssignmentRef:
    id: int = None
    name: str = None

@dataclass
class TaskAssignment:
    budget: Optional[float]
    hourly_rate: Optional[float]
    id: int = None
    is_project_manager: bool = None
    is_active: bool = None
    created_at: str = None
    updated_at: str = None
    project: Project = None
    task: TaskAssignmentRef = None

@dataclass
class UserAssignment:
    budget: Optional[float]
    hourly_rate: Optional[float]
    id: int = None
    is_project_manager: bool = None
    is_active: bool = None
    created_at: str = None
    updated_at: str = None
    project: Project = None
    user: User = None

@dataclass
class ProjectTaskAssignments:
    hourly_rate: Optional[float]
    budget: Optional[float]
    id: int = None
    billable: bool = None
    is_active: bool = None
    created_at: str = None
    updated_at: str = None
    task: TaskRef = None

@dataclass
class TimeEntry:
    notes: Optional[str]
    locked_reason: Optional[str]
    timer_started_at: Optional[str]
    started_time: Optional[str]
    ended_time: Optional[str]
    invoice: Optional[InvoiceRef]
    external_reference: Optional[str]
    billable_rate: Optional[float]
    id: int = None
    spent_date: str = None
    user: User = None
    client: Client = None
    project: Project = None
    task: Task = None
    user_assignment: UserAssignment = None
    task_assignment: ProjectTaskAssignments = None
    hours: float = None
    created_at: str = None
    updated_at: str = None
    is_locked: bool = None
    is_closed: bool = None
    is_billed: bool = None
    is_running: bool = None
    billable: bool = None
    budgeted: bool = None
    cost_rate: float = None


@dataclass
class Project:
    over_budget_notification_date: Optional[str]
    starts_on: Optional[str]
    ends_on: Optional[str]
    cost_budget: Optional[float]
    hourly_rate: Optional[float]
    fee: Optional[float]
    budget: Optional[float]
    notes: Optional[str]
    code: Optional[str]
    id: int = None
    name: str = None
    is_active: bool = None
    bill_by: str = None
    budget_by: str = None
    budget_is_monthly: bool = None
    notify_when_over_budget: bool = None
    over_budget_notification_percentage: float = None
    show_budget_to_all: bool = None
    created_at: str = None
    updated_at: str = None
    is_billable: bool = None
    is_fixed_fee: bool = None
    client: Client = None
    cost_budget_include_expenses: bool = None

@dataclass
class Role:
    id: int = None
    name: str = None
    user_ids: List[int] = None
    created_at: str = None
    updated_at: str = None

@dataclass
class CostRate:
    start_date: Optional[str]
    end_date: Optional[str]
    id: int = None
    amount: float = None
    created_at: str = None
    updated_at: str = None

@dataclass
class ProjectAssignment:
    budget: Optional[float]
    hourly_rate: Optional[float]
    id: int = None
    is_project_manager: bool = None
    is_active: bool = None
    created_at: str = None
    updated_at: str = None
    project: Project = None
    client: ClientRef = None
    task_assignment: List[ProjectTaskAssignments] = None

@dataclass
class User:
    default_hourly_rate: Optional[float]
    cost_rate: Optional[float]
    id: int = None
    first_name: str = None
    last_name: str = None
    email: str = None
    telephone: str = None
    timezone: str = None
    has_access_to_all_future_projects: bool = None
    is_contractor: bool = None
    is_admin: bool = None
    is_project_manager: bool = None
    can_see_rates: bool = None
    can_create_projects: bool = None
    can_create_invoices: bool = None
    is_active: bool = None
    created_at: str = None
    updated_at: str = None
    weekly_capacity: int = None
    roles: List[str] = None
    avatar_url: str = None

@dataclass
class DetailedTimeEntry:
    notes: Optional[str]
    external_reference_url: Optional[str]
    roles: Optional[str]
    date: str
    client: str
    project: str
    project_code: str
    task: str
    hours: float
    billable: str
    invoiced: str
    approved: str
    first_name: str
    last_name: str
    employee: str
    billable_rate: float
    billable_amount: float
    cost_rate: float
    cost_amount: float
    currency: str

@dataclass
class Links:
    next: Optional[str]
    previous: Optional[str]
    first: str
    last: str

@dataclass
class BasePage:
    previous_page: Optional[int]
    next_page: Optional[int]
    per_page: int = None
    total_pages: int = None
    total_entries: int = None
    page: int = 1
    links: Links = None

@dataclass
class ClientContacts(BasePage):
    contacts: List[ClientContact] = field(init=False)

@dataclass
class Clients(BasePage):
    clients: List[Client] = field(init=False)

@dataclass
class InvoiceMessages(BasePage):
    invoice_messages: List[InvoiceMessage] = field(init=False)

@dataclass
class InvoicePayments(BasePage):
    invoice_payments: List[InvoicePayment] = field(init=False)

@dataclass
class Invoices(BasePage):
    invoices: List[Invoice] = field(init=False)

@dataclass
class InvoiceItemCategories(BasePage):
    invoice_item_categories: List[InvoiceItemCategory] = field(init=False)

@dataclass
class EstimateMessages(BasePage):
    estimate_messages: List[EstimateMessage] = field(init=False)

@dataclass
class Estimates(BasePage):
    estimates: List[Estimate] = field(init=False)

@dataclass
class EstimateItemCategories(BasePage):
    estimate_item_categories: List[EstimateItemCategory] = field(init=False)

@dataclass
class Expenses(BasePage):
    expenses: List[Expense] = field(init=False)

@dataclass
class ExpenseCategories(BasePage):
    expense_categories: List[ExpenseCategory] = field(init=False)

@dataclass
class Tasks(BasePage):
    tasks: List[Task] = field(init=False)

@dataclass
class TimeEntries(BasePage):
    time_entries: List[TimeEntry] = field(init=False)

@dataclass
class UserAssignments(BasePage):
    user_assignments: List[UserAssignment] = field(init=False)

@dataclass
class TaskAssignments(BasePage):
    task_assignments: List[TaskAssignment] = field(init=False)

@dataclass
class Projects(BasePage):
    projects: List[Project] = field(init=False)

@dataclass
class Roles(BasePage):
    roles: List[Role] = field(init=False)

@dataclass
class UserCostRates(BasePage):
    cost_rates: List[CostRate] = field(init=False)

@dataclass
class ProjectAssignments(BasePage):
    project_assignments: List[ProjectAssignment] = field(init=False)

@dataclass
class Users(BasePage):
    users: List[User] = field(init=False)

@dataclass
class DetailedTimeReport():
    detailed_time_entries: List[DetailedTimeEntry]

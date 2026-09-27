# TradeFlowAI

A full-stack trade-finance workflow and compliance monitoring system built with Django REST Framework, PostgreSQL, and React.

TradeFlowAI models operational workflows around foreign-exchange-funded trade cases, including companies, registration orders, currency purchases, payment instruments, shipments, invoices, regulatory deadlines, approvals, notifications, and auditability.

> **Portfolio project:** TradeFlowAI is an independent software project inspired by real-world trade-finance workflow patterns. It is not an official banking product and the repository must not contain real customer, transaction, credential, or confidential institutional data.

## Why TradeFlowAI?

Trade-finance cases can span multiple related records and time-sensitive obligations. A single case may involve a company, registration order, one or more currency purchases, payment instruments, partial shipments, invoices, deadline extensions, approvals, and compliance checks.

TradeFlowAI turns those relationships into structured, testable workflows so an operator can answer questions such as:

- Which cases are approaching or past a regulatory deadline?
- How much of an obligation has already been fulfilled?
- Which shipments or balances are still outstanding?
- Which records require review or approval?
- Who created, submitted, approved, or modified a record?
- Which regulatory rule produced a deadline?

## Core Features

- **Trade case management:** companies, registration orders, currency purchases, payment instruments, shipment parts, customs clearances, invoices, and related records.
- **Compliance and deadline services:** deadline calculation, remaining-day tracking, obligation aggregation, outstanding-balance calculation, deadline extensions, and compliance evaluation.
- **Operational dashboard:** aggregated backend data for approaching deadlines, overdue obligations, incomplete shipments, and other attention items.
- **Approval workflows:** submission and approval requests with review states and maker/checker-style separation.
- **Role-based access control:** backend permissions and protected frontend routes for role-sensitive operations.
- **Audit trail:** request context, middleware, signals, services, and read-only API access for traceable operational events.
- **Notifications:** notification records, recipient handling, deadline processing, delivery tracking, and an SMS abstraction with a safe mock mode.
- **Search and filtering:** Django REST Framework APIs with structured filtering and ordering.
- **Automated tests:** domain-focused tests for regulatory logic, aggregation, workflows, shipment approvals, and SMS behavior.

## Architecture

```text
tradeflow-ai/
├── backend/
│   ├── apps/
│   │   ├── authentication/
│   │   ├── audit/
│   │   ├── common/
│   │   ├── companies/
│   │   ├── documents/
│   │   ├── notifications/
│   │   ├── trade_orders/
│   │   └── workflows/
│   ├── config/
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── performance/
├── docker-compose.yml
├── .env.example
└── README.md
```

Complex domain logic is kept in service modules instead of being concentrated in views. Examples include `deadline_service`, `compliance_service`, `balance_service`, `shipment_service`, `regulatory_rule_service`, `approval_service`, and `notification_service`.

## Technology Stack

**Backend:** Python, Django, Django REST Framework, django-filter, django-cors-headers, django-environ, PostgreSQL, Psycopg

**Frontend:** React, Vite, React Router, i18next

**Development:** Docker, Docker Compose, Git, GitHub

**Additional:** Jalali date support, Excel processing with openpyxl, and optional Kavenegar SMS integration

## Simplified Domain Model

```text
Company
  └── Registration Order
       ├── Currency Purchase
       │    └── Payment Instrument
       ├── Shipment Parts
       ├── Customs Clearances
       └── Documents / Invoices

Users / Roles
  ├── Approval Workflows
  ├── Audit Events
  └── Notifications
```

## Getting Started

### Prerequisites

- Python compatible with the pinned backend dependencies
- Node.js and npm
- Docker and Docker Compose
- Git

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd tradeflow-ai
```

### 2. Configure environment variables

Copy the example environment file:

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Then replace the development placeholders in `.env` as needed. Never commit the real `.env` file.

### 3. Start PostgreSQL

```bash
docker compose up -d
```

### 4. Set up the backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies and initialize Django:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The backend development server normally runs at `http://127.0.0.1:8000/`.

### 5. Set up the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite normally serves the frontend at `http://localhost:5173/`.

## Testing

Run the Django test suite from the backend directory:

```bash
cd backend
python manage.py test
```

The repository includes tests around domain-critical behavior such as regulatory compliance, currency-purchase aggregation, invoice aggregation, workflow submission, shipment/currency-purchase approvals, helper functions, and SMS behavior.

For the frontend:

```bash
cd frontend
npm run lint
npm run build
```

## Configuration and Security

Sensitive configuration is supplied through environment variables rather than hard-coded into source control. The repository ignores local `.env` files while intentionally tracking `.env.example` with placeholder values.

Configuration includes:

- Django secret key and debug mode
- allowed hosts
- PostgreSQL credentials
- CORS and CSRF trusted origins
- production HTTPS/HSTS settings
- SMS provider configuration

The application also includes authenticated API access, role-sensitive permissions, CSRF protections, secure-cookie settings for non-debug deployments, clickjacking protection, audit logging, and approval-workflow separation.

> Before any public or production deployment, perform an environment-specific security review. Development defaults are not a production deployment configuration.

## SMS Integration

Real SMS delivery is opt-in. The safe development defaults are:

```env
SMS_ENABLED=False
SMS_PROVIDER=MOCK
```

If a real provider is enabled, credentials must be supplied only through local/deployment environment variables and must never be committed.

## Data and Privacy

This repository is intended for software-engineering and portfolio purposes.

- Do not commit real customer or company records.
- Do not commit banking documents, transaction identifiers, credentials, or proprietary institutional data.
- Use synthetic or properly anonymized demo/test data only.

## Project Direction

TradeFlowAI sits at the intersection of financial technology, trade-finance operations, compliance systems, backend engineering, and data-oriented software design.

Potential future work includes richer compliance analytics, dashboard visualizations, automated risk indicators, stronger notification scheduling, document validation, reporting/export capabilities, expanded automated tests, CI/CD, and fuller containerized deployment.

Machine learning should only be added when there is a clearly defined problem, appropriate data, a defensible baseline, and a meaningful evaluation methodology. The current repository does **not** claim to be an AI/ML system merely because of the project name.

## Disclaimer

TradeFlowAI is an independent educational and portfolio project. It is not affiliated with, endorsed by, or deployed by any bank, regulator, payment organization, or financial institution. Its regulatory and compliance logic must not be interpreted as legal, financial, or regulatory advice.

## Author

**Alireza Khatiri**

Portfolio interests: financial data, banking-domain software, data science, and backend engineering.

## License

No open-source license is currently granted. Unless a license is added later, the source code remains under the author's copyright.

# AutoGarage Pro

Workshop management platform built for African garages. Track work orders, inventory, customers, payments, and get AI-powered diagnostics — all in one system.

## Features

- Work Orders — Track repairs from intake to completion
- Inventory Management — Real-time stock tracking with low stock alerts
- Customer Records — Database with vehicle service history
- AI Diagnostics — OBD-II fault code analysis with cost estimates
- Appointments — Schedule and manage customer bookings
- Payments & Invoices — Track revenue and generate invoices
- Multi-Tenant — Each garage data is completely isolated
- Role-Based Access — Owner, manager, mechanic, receptionist roles
- Web Dashboard — Full management console
- Android App — Mobile access for mechanics

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django REST Framework |
| Auth | JWT (SimpleJWT) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Web Dashboard | Vanilla HTML/CSS/JS |
| Android App | Kotlin + Jetpack Compose |
| Deployment | Render (backend) + GitHub Actions (APK) |

## Quick Start

git clone https://github.com/BLESS-LAB/AutoGarage-Platform.git
cd AutoGarage-Platform
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver

## Demo Login

URL: http://localhost:8000/api/auth/login-page/
Username: demo
Password: demo1234

## API Endpoints

| Endpoint | Description |
|---|---|
| POST /api/auth/register/ | Register new garage |
| POST /api/auth/login/ | Login (returns JWT) |
| GET /api/customers/ | List customers |
| GET /api/vehicles/ | List vehicles |
| GET /api/work-orders/ | Work orders |
| GET /api/inventory/ | Inventory items |
| GET /api/appointments/ | Appointments |
| GET /api/mechanics/ | Mechanic profiles |
| GET /api/payments/ | Payment history |
| GET /api/invoices/ | Invoices |
| GET /api/services/ | Service catalog |
| POST /api/ai/diagnose/ | AI fault diagnosis |
| GET /api/notifications/ | Notifications |
| GET /api/dashboard/ | Dashboard stats |

## Deployment

API Base URL: https://autogarage-api-wwj4.onrender.com/api/
Web Dashboard: https://autogarage-api-wwj4.onrender.com/api/dashboard-page/

## License

MIT

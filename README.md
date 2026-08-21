# Seva Bandhu

Seva Bandhu is a Django-based service request platform that connects customers with technicians for local home services.

## Main Features

- Customer and technician signup/login flows
- Customer service selection and request creation
- Technician dashboard and job acceptance flow
- Service request status tracking
- Email verification and invoice email flow
- Invoice PDF generation
- Real-time request/tracking updates through Django Channels

## Technology

- Frontend: Django templates currently live in `backend/core/templates`. `SevaBandhu-Frontend/` is separated for a future standalone frontend.
- Backend: Django with Django Channels
- Database: SQLite for local development through `backend/db.sqlite3`

## Project Structure

```text
SevaBandhu/
├── SevaBandhu-Frontend/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3
│   ├── core/
│   └── seva_bandhu/
├── .env.example
├── .gitignore
└── README.md
```

## Local Setup

Create and activate a Python virtual environment, then install backend dependencies:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` at the repository root and fill in local values. Do not commit `.env`.

Run the backend:

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

The current frontend is served by Django templates from the backend routes. A standalone frontend has not been generated yet. The placeholder frontend workspace can be checked with:

```bash
cd SevaBandhu-Frontend
npm start
```

## Environment Variables

Use `.env.example` as the template for required configuration. Keep real values only in `.env` or your deployment provider.

Important variables include:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`
- `FIREBASE_API_KEY`
- `FIREBASE_AUTH_DOMAIN`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_STORAGE_BUCKET`
- `FIREBASE_MESSAGING_SENDER_ID`
- `FIREBASE_APP_ID`

## Security Notes

- Do not commit `.env`, SQLite database files, virtual environments, generated media, or dependency folders.
- `backend/db.sqlite3` is local development data and should stay out of Git.
- Rotate any credential that was ever committed, shared, or exposed before this cleanup.
- Create production admin users manually, or set the explicit superuser environment variables only in a trusted local/deployment environment.

## Future Improvements

- Build a real standalone frontend in `SevaBandhu-Frontend/`.
- Move any remaining Django template UI into the standalone frontend only after API boundaries are defined.
- Remove duplicate password fields from profile models and rely only on Django's built-in password hashing.
- Add automated tests for signup, login, request creation, assignment, payment status, and email flows.

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

## Transactional Email (Brevo)

Customer email verification codes and invoice emails use Django's standard `send_mail`/`EmailMessage` interface. The optional Brevo backend sends those existing messages through Brevo's HTTPS transactional-email API, so Render Free does not need outbound SMTP access.

1. In Brevo, create an API key and verify the sender email address (or sending domain) you will use.
2. In Render → the Seva Bandhu web service → Environment, add:
   - `EMAIL_BACKEND=core.email_backends.BrevoEmailBackend`
   - `BREVO_API_KEY` = your private Brevo API key
   - `BREVO_SENDER_EMAIL` = the sender address verified in Brevo
   - `BREVO_SENDER_NAME=Seva Bandhu`
   - `BREVO_API_TIMEOUT=15`
   - `DEFAULT_FROM_EMAIL` = the same verified sender address
3. Save and wait for Render to redeploy.
4. Test a real OTP to an inbox you control, then verify the code. Also test invoice email if the payment flow can safely be exercised.

Keep the API key only in Render's private environment settings or a local, uncommitted `.env`. Never use a `VITE_*` variable for a secret. A successful Brevo API response means the message was accepted by Brevo, not necessarily delivered to the recipient's inbox; inspect Brevo's transactional logs if delivery is missing.

When the Brevo API key is absent, the settings retain the normal local development behavior (console email in debug mode if SMTP is not configured). Legacy SMTP environment variables remain available if deliberately using an SMTP backend.

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

# Seva Bandhu

Seva Bandhu is a Django-based service management platform that connects customers with technicians for local home-service requests.

The project has evolved beyond a basic booking system and now includes intelligent service recommendations, smart offers, technician earnings and incentives, real-time tracking and chat, customer support, comprehensive admin analytics, and a local admin data assistant.

## Overview

Seva Bandhu provides three main experiences:

- Customer: discover services, create service requests, choose service dates and time slots, use offers/referrals, pay for services, track technicians, chat during active requests, manage a wallet, submit ratings/complaints, and use an AI customer assistant.
- Technician: manage a profile, receive service requests, accept and complete jobs, navigate to customers with live GPS tracking, use real-time chat, view wallet earnings, request withdrawals, and work toward incentive milestones.
- Super Admin: manage customers, technicians, services, requests, offers, referrals, support, incentives, withdrawals, notifications, ratings, and platform analytics, with a natural-language admin data assistant for read-only information retrieval.

## Key Features

### Customer features

- Customer registration and login.
- Email verification with a 6-digit OTP before account creation.
- Phone verification using Firebase.
- Google-based customer sign-in flow.
- Service catalog with service image, price, enabled/disabled status, and dynamically calculated service ratings.
- Service request creation with service selection, problem description, priority, preferred service date, preferred time slot, contact number, and service address.
- Booking/request status tracking.
- Online/offline payment flow as supported by the current application.
- Customer wallet with transaction history and self top-up flow.
- Invoice PDF generation and transactional invoice emails.
- Technician live-location tracking for active requests.
- Real-time customer-technician chat.
- Customer ratings for completed technician services.
- Customer complaints/support tickets linked to bookings and technicians.
- Offers and customer-specific offer assignments.
- Referral codes and referral reward tracking.
- Personalized service recommendations powered by the ML recommendation engine.
- Smart-offer intent tracking based on recent service interest.
- Customer AI assistant using customer-specific platform context.

### Technician features

- Technician registration and login.
- Profile completion with service category, experience, and working locations.
- Availability management.
- Technician dashboard and job/request management.
- Request acceptance and status progression.
- Start Journey / active tracking flow.
- Live GPS location publishing through WebSockets.
- Route navigation with Leaflet and Leaflet Routing Machine.
- OSRM-based road routing, distance, ETA, and turn-by-turn route information.
- Browser voice guidance using the Web Speech API when supported.
- Arrival detection and route recalculation support.
- Real-time customer-technician chat.
- Technician notifications.
- Technician wallet with available balance, total job earnings, total incentive earnings, total withdrawn, and transaction history.
- Withdrawal request workflow with pending, approved, completed, and rejected handling.
- Incentive missions and progress tracking.
- Incentive awards for supported milestones such as daily completed jobs and five-star rating milestones.
- Full-page technician support assistant with predefined troubleshooting flows.
- Escalation from guided support to a human admin support conversation.

### Service rating engine

Service ratings are calculated from completed service bookings and validated complaints rather than being hardcoded.

The current rating engine uses Bayesian smoothing with:

- prior confidence: 10 virtual completed bookings
- prior complaint rate: 2%
- complaint-to-rating penalty multiplier: 10
- final rating clamped to the 1.0 to 5.0 range
- services with no completed bookings show a no-rating state

Validated complaints are based on resolved complaint tickets and exclude tickets explicitly marked as rejected or declined.

### ML recommendation engine

The project contains a collaborative-filtering recommendation engine implemented with scikit-learn.

Current design:

- customer-service interaction matrix
- customer history and similar-customer behavior
- cosine-distance nearest-neighbor model
- up to 5 nearest neighbors
- personalized recommendation ranking
- user's own history receives 70% of the final score
- similar-customer behavior contributes 30%
- interaction values include recency and booking-status weighting during model training
- cold-start/popularity fallback when a personalized model is not available
- up to 3 recommended services are returned by default
- recommendation impressions, clicks, and bookings are logged through RecommendationLog

Relevant files:

- backend/core/ml/recommender.py
- backend/core/ml/train_recommender.py
- backend/core/ml/model/

### Smart offers and promotions

Offers are managed through an eligibility and assignment engine.

Current capabilities include:

- global and segmented offers
- new-customer and frequent-customer targeting
- customer offer assignments
- offer viewing/redemption tracking
- service-specific applicability
- flat and percentage discounts
- maximum discount limits
- minimum order value
- global usage limits
- per-customer usage limits
- offer expiry and activation windows
- recent service-intent tracking
- cooldown protection for repeated popups
- ML recommendation scores can influence which eligible smart offer is prioritized
- recommendation/offer interaction is reflected in platform analytics

Relevant files:

- backend/core/services/offer_engine.py
- backend/core/models.py

### Referrals

Customers can use referral codes and referral records are stored in the platform.

The current implementation tracks:

- referrer
- referee
- reward amount
- referral creation time
- referral-related wallet credit
- admin referral reporting

### Technician wallet and incentives

Technician earnings are maintained separately from customer payments.

The wallet service supports:

- job-earning credits
- incentive credits
- withdrawal reservations
- withdrawal approval/completion
- rejected-withdrawal balance reversal
- transaction records
- concurrency-safe wallet updates using database transactions and row locking

Relevant files:

- backend/core/services/technician_wallet.py
- backend/core/services/incentive_engine.py

### Real-time communication and tracking

Django Channels powers the real-time parts of the platform.

Current WebSocket routes include:

- /ws/requests/ — technician request notifications
- /ws/tracking/<request_id>/ — live technician tracking
- /ws/chat/<request_id>/ — customer-technician chat
- /ws/support/technician/<session_id>/ — technician/admin support communication

Tracking includes authorization of the logged-in participant, coordinate validation, persisted tracking snapshots, route metrics, and technician arrival state.

The technician navigation interface currently uses:

- Leaflet
- Leaflet Routing Machine
- OSRM
- browser geolocation
- browser speechSynthesis voice guidance

### Customer AI assistant

The customer chatbot is a context-aware AI assistant for the currently authenticated customer.

The current backend:

- retrieves customer-specific account and service-request context
- includes active and recent completed requests
- includes enabled services and prices
- uses Google Gemini as the primary AI provider
- uses Groq as a fallback provider
- does not expose unrelated customer records to the model context
- instructs the assistant not to invent booking, price, technician, or status information that is not in the supplied context

Relevant files:

- backend/core/ai/chatbot.py
- backend/core/ai/context.py
- backend/core/ai/prompts.py
- SevaBandhu-Frontend/templates/customer/chatbot.html

The current customer AI implementation does not directly call the OpenAI API. The Groq model name can contain an openai/ prefix because that is the model identifier used by the Groq service.

### Technician support assistant

Technician support is intentionally different from the customer AI chatbot.

It currently uses a deterministic predefined decision tree rather than an external LLM.

Supported areas include:

- payment / earnings
- service / booking
- wallet / withdrawal
- incentives / rewards
- app / technical problems
- account / profile
- other issues
- guided troubleshooting
- solved/still-problem responses
- explicit admin escalation

After escalation, the platform creates a technician support ticket/conversation that can be handled by an admin.

Relevant file:

- backend/core/services/support_flow.py

### Super Admin management

The custom super-admin interface provides management/reporting pages for:

- dashboard overview
- customers
- technicians
- services
- service requests
- service addresses
- service details
- technician notifications
- customer support tickets
- technician support
- offers
- customer offers
- referrals
- incentives
- withdrawals
- platform analytics
- comprehensive analytics
- admin data assistant

## Comprehensive admin analytics

The admin analytics implementation separates important financial concepts instead of treating them as the same number.

The current analytics layer includes:

- sales / customer payments
- technician earnings
- platform income
- offer discounts
- referral rewards
- incentive payouts
- withdrawal requests
- approved withdrawals
- rejected withdrawals
- pending withdrawals
- wallet reversals
- total bookings
- completed bookings
- cancelled bookings
- new customers
- new technicians
- top services by bookings
- service sales

The current platform analytics page additionally exposes:

- ML recommendation performance
- recommendation count
- click-through rate
- conversion rate
- recommendation scores
- top recommended services
- service rating diagnostics
- validated complaint counts
- complaint rates
- smart-offer performance
- offer assignment/view/redemption statistics
- offer-driven bookings and revenue

Authoritative analytics code:

- backend/core/analytics_helper.py
- backend/core/admin_views.py
- backend/core/services/rating_engine.py

## Admin Data Assistant

The project also contains a local, read-only Admin Data Assistant.

It is not a general-purpose chatbot and does not use an external LLM.

It is designed to answer natural-language questions about data already available to the Seva Bandhu admin system, including:

- technicians
- customers
- services
- bookings
- sales
- technician earnings
- platform summary data
- ratings
- complaints
- offers
- referrals
- incentives
- withdrawals
- entity details such as contact information

The assistant is integrated as a floating tool inside the custom admin interface.

Important design rules:

- admin-only access
- read-only behavior
- database-backed answers
- controlled query handling
- no arbitrary Python execution
- no arbitrary SQL generated from user text
- no external AI/API dependency

Relevant files:

- backend/core/services/admin_assistant.py
- backend/core/admin_views.py
- SevaBandhu-Frontend/templates/admin_custom/components/admin_assistant.html

## Technology Stack

### Backend

- Python
- Django 5.2
- Django Channels
- Daphne / ASGI
- Django ORM
- PostgreSQL in deployment
- SQLite fallback for local development
- WhiteNoise for collected static files

### Database

- Supabase PostgreSQL for the deployed environment
- Django migrations are the schema source of truth

### Frontend / UI

The primary application UI is currently implemented with Django templates under:

SevaBandhu-Frontend/templates/

The repository also contains a Vite/React frontend foundation for the Vercel-hosted public frontend.

### Machine learning / data processing

- scikit-learn
- NumPy
- pandas
- joblib

### AI integrations

- Google Gemini
- Groq

### Authentication / verification

- Django authentication/session system
- Firebase configuration for phone verification and related authentication flows
- customer Google-auth endpoint

### Maps / routing

- Leaflet
- Leaflet Routing Machine
- OSRM

### Email

- Django email abstraction
- Brevo transactional email API for deployed email delivery
- legacy SMTP configuration remains available for deliberate use

### Document generation

- ReportLab
- xhtml2pdf
- PDF invoice generation and email attachment flow

### Deployment

- Render — Django backend / ASGI application
- Supabase — production PostgreSQL database
- Vercel — public frontend deployment layer

## Architecture

~~~text
                         +----------------------+
                         |       Customer       |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |    Django Web App    |
                         |  Templates + Views   |
                         +----------+-----------+
                                    |
               +--------------------+---------------------+
               |                    |                     |
               v                    v                     v
       +--------------+    +----------------+    +---------------+
       | Django ORM   |    | Django         |    | AI / ML       |
       | + PostgreSQL |    | Channels       |    | Services      |
       +------+-------+    +-------+--------+    +-------+-------+
              |                    |                     |
              v                    v                     v
       +--------------+    +----------------+    +---------------+
       |   Supabase   |    | Tracking/Chat  |    | Recommendations|
       |  PostgreSQL  |    | /Support WS    |    | Offers / AI    |
       +--------------+    +----------------+    +---------------+

       Render  -> Django / Daphne / APIs / Templates / WebSockets
       Vercel  -> Public frontend deployment layer
~~~

## Project structure

~~~text
Seva-Bandhu/
├── SevaBandhu-Frontend/
│   ├── templates/
│   │   ├── admin/
│   │   ├── admin_custom/
│   │   ├── customer/
│   │   ├── technician/
│   │   ├── base.html
│   │   └── home.html
│   ├── assets/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── vercel.json
│   └── .env.example
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── core/
│   │   ├── ai/
│   │   ├── ml/
│   │   ├── services/
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── admin_views.py
│   │   ├── consumers.py
│   │   ├── routing.py
│   │   └── urls.py
│   ├── seva_bandhu/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── render-build.sh
│
├── .github/
│   └── workflows/
│
├── render.yaml
├── .env.example
├── .gitignore
└── README.md
~~~

## Local development

### Backend

Create and activate a virtual environment:

~~~bash
cd backend
python -m venv .venv
~~~

Windows PowerShell:

~~~powershell
.\\.venv\\Scripts\\Activate.ps1
~~~

Linux/macOS:

~~~bash
source .venv/bin/activate
~~~

Install dependencies:

~~~bash
pip install -r requirements.txt
~~~

Copy the environment template:

~~~text
.env.example -> .env
~~~

Keep real secrets only in the local .env.

Run migrations:

~~~bash
python manage.py migrate
~~~

Run the Django development server:

~~~bash
python manage.py runserver
~~~

### ML model training

The recommendation training logic is located at:

~~~text
backend/core/ml/train_recommender.py
~~~

It reads service-request history, applies interaction/status/recency weighting, builds the customer-service matrix, and saves model artifacts under:

~~~text
backend/core/ml/model/
~~~

## Deployment

### Render

The deployed Django application runs as an ASGI service using Daphne.

Deployment configuration is stored in:

~~~text
render.yaml
backend/render-build.sh
~~~

The Render build performs:

~~~bash
pip install -r requirements.txt
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --no-input
python manage.py migrate --noinput
~~~

Important production environment variables include:

- DJANGO_SECRET_KEY
- DJANGO_DEBUG
- DJANGO_ALLOWED_HOSTS
- DJANGO_CSRF_TRUSTED_ORIGINS
- DATABASE_URL
- REDIS_URL when using a shared Redis channel layer
- PUBLIC_BASE_URL
- Brevo email variables
- Gemini/Groq AI variables
- Firebase configuration variables

### Supabase

Supabase PostgreSQL is used as the production database through Django's DATABASE_URL.

The schema is managed by Django migrations.

Do not manually replace the Django schema with unrelated Supabase Auth tables.

### Vercel

The SevaBandhu-Frontend directory contains the standalone frontend/deployment layer.

Important values for Vercel are:

~~~text
Root Directory: SevaBandhu-Frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
~~~

The public backend URL is configured through:

~~~text
VITE_BACKEND_URL
~~~

Do not place private secrets such as Django secret keys, database passwords, Brevo API keys, Gemini/Groq secret keys, or Firebase server-side secrets in frontend environment variables.

## Environment variables

Use .env.example as the reference template.

### Django / deployment

~~~text
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DJANGO_ALLOWED_HOSTS=
DJANGO_CSRF_TRUSTED_ORIGINS=
DATABASE_URL=
PUBLIC_BASE_URL=
REDIS_URL=
DJANGO_TIME_ZONE=
~~~

### Brevo transactional email

~~~text
EMAIL_BACKEND=core.email_backends.BrevoEmailBackend
BREVO_API_KEY=
BREVO_SENDER_EMAIL=
BREVO_SENDER_NAME=Seva Bandhu
BREVO_API_TIMEOUT=15
DEFAULT_FROM_EMAIL=
~~~

The deployed application uses Brevo's HTTPS API so it does not need outbound Gmail SMTP.

### AI

~~~text
GEMINI_API_KEY=
AI_MODEL_NAME=
GROQ_API_KEY=
GROQ_MODEL=
~~~

The current customer AI implementation uses Gemini first and Groq as fallback.

### Firebase

~~~text
FIREBASE_API_KEY=
FIREBASE_AUTH_DOMAIN=
FIREBASE_PROJECT_ID=
FIREBASE_STORAGE_BUCKET=
FIREBASE_MESSAGING_SENDER_ID=
FIREBASE_APP_ID=
~~~

## Testing

The repository includes tests for important flows, including:

- customer account/signup verification behavior
- Brevo email backend behavior
- OTP-related email flow support
- recommendation engine behavior

GitHub Actions is used for automated validation of backend email changes and frontend builds.

Examples:

~~~bash
cd backend
python manage.py check
python manage.py test
~~~

For the Vite frontend:

~~~bash
cd SevaBandhu-Frontend
npm install
npm run build
~~~

## Security notes

- Never commit .env files.
- Never commit real API keys or passwords.
- Rotate credentials if they are exposed or accidentally committed.
- Keep the admin assistant read-only and admin-protected.
- Keep payment, wallet, withdrawal, and account mutation logic server-side.
- Use HTTPS in production.
- Keep the Django production database behind the application rather than exposing unrestricted data directly to the browser.
- Review Supabase Row Level Security and Data API exposure separately if client-side Supabase access is introduced.

## Current production endpoint

Backend:

https://seva-bandhu-src9060.onrender.com

The application also has a Vercel frontend deployment layer using the SevaBandhu-Frontend project directory.

## Main implementation modules

~~~text
backend/core/models.py
backend/core/views.py
backend/core/admin_views.py
backend/core/consumers.py
backend/core/analytics_helper.py

backend/core/ai/chatbot.py
backend/core/ai/context.py
backend/core/ai/prompts.py

backend/core/ml/recommender.py
backend/core/ml/train_recommender.py

backend/core/services/rating_engine.py
backend/core/services/offer_engine.py
backend/core/services/technician_wallet.py
backend/core/services/incentive_engine.py
backend/core/services/support_flow.py
backend/core/services/admin_assistant.py
~~~

## Project status

Seva Bandhu currently combines:

- service request management
- customer and technician workflows
- payments and invoices
- real-time tracking and chat
- AI-assisted customer support
- ML-based service recommendations
- smart offers and referral features
- technician wallet, withdrawals, and incentives
- customer/technician support workflows
- service and technician ratings
- comprehensive admin analytics
- natural-language admin data retrieval
- Render + Supabase + Vercel deployment support

The codebase continues to evolve, so this README should be updated when major architectural or feature changes are introduced.

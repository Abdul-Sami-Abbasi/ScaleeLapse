# Deployment

## Docker target
Install Docker with Compose. Copy `.env.example` to `.env`, set unique secrets/passwords, and keep DEBUG=1 only for local HTTP demos. Run `docker compose up --build`, then open http://localhost:8080. PostgreSQL persists in `pgdata`; uploads persist in `uploads`. Backend waits for PostgreSQL health and runs migrations. Optional demo: `docker compose exec backend python backend/manage.py seed_demo` with DEMO_PASSWORD set in `.env`.

Docker does not include optional heavy ML libraries by default. Install `requirements-ml.txt` in a derived backend image and mount validated model artifacts for transformer/Prophet operation. Without them the UI reports the limitation and ARIMA/keyword assistance work. Do not mount the archive/cookies into containers.

## Local Windows development
Python 3.12 is recommended. Run `python -m venv .venv`, then `.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt`. Run `.\.venv\Scripts\python.exe backend/manage.py migrate` and `.\.venv\Scripts\python.exe backend/manage.py runserver 127.0.0.1:8000`. In another terminal run `npm.cmd --prefix frontend ci` and `npm.cmd --prefix frontend run dev`. Activation is not required. The already-prepared computer can double-click `start.cmd` to restore all three local services after a restart; this leaves persistent execution policies unchanged.

With no POSTGRES_HOST, SQLite is an explicit local fallback. For PostgreSQL set POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER and POSTGRES_PASSWORD in the process environment. Django does not automatically load `.env` outside Compose.

## Production preparation
Set DEBUG=0, a random SECRET_KEY, exact ALLOWED_HOSTS and HTTPS CORS/CSRF origins. Terminate TLS in a configured reverse proxy; secure cookies require HTTPS. Back up database and uploads together. Use a secret store or protected environment file, a managed database user, and private model volumes. Run `manage.py check --deploy` and address infrastructure-specific warnings. Hosting credentials, DNS, TLS and production deployment are not supplied or performed.

Do not run n8n source collection until source authorization is established. No scraping credentials or stored cookies are used.

# Mess Management System 🥗

A **Django 4.2.11** project to manage mess/meal operations with user auth, role control, REST APIs, backups, Google Drive storage, and secure environment variables.

---

## Features

- User authentication (sessions + JWT)
- Role-based access control
- REST API (Django REST Framework)
- WYSIWYG editor (django-summernote)
- Backup & restore (django-dbbackup)
- Google Drive storage integration
- Postgres + PostGIS support
- Optional Redis/Memcached caching
- Secure secrets via `.env` (django-environ)

---

## Requirements

- **Python:** 3.12 (or any 3.8–3.12 compatible with Django 4.2)
- **PostgreSQL:** 13+ (with **PostGIS** installed)
- **GDAL:** Installed and importable (Windows users typically install a wheel that matches Python & CPU)
- **pip & virtualenv/venv**

> If you’re on Windows and use GDAL, install a matching wheel for your Python version and architecture.

---

## Quick Start

### 1) Clone the repo

    git clone https://github.com/<your-username>/mess_management6.git
    cd mess_management6

### 2) Create & activate a virtual environment

    python -m venv venv

Activate it:

- **Windows**

      venv\Scripts\activate

- **Linux/Mac**

      source venv/bin/activate

### 3) Install dependencies

    pip install -r requirements.txt

> If GDAL fails from PyPI on Windows, install a local wheel first, then run `pip install -r requirements.txt`.

### 4) Create a `.env` file (project root)

    # Core
    DEBUG=True
    SECRET_KEY=your-very-secret-key

    # Allowed hosts (comma separated in production)
    ALLOWED_HOSTS=127.0.0.1,localhost

    # Database (PostgreSQL + PostGIS)
    DB_NAME=mess_management
    DB_USER=postgres
    DB_PASSWORD=your-db-password
    DB_HOST=localhost
    DB_PORT=5432

    # Cache (pick one block and configure settings.py accordingly)
    # MEMCACHED_HOST=127.0.0.1
    # MEMCACHED_PORT=11211

    # REDIS_URL=redis://127.0.0.1:6379/1

    # Google Drive Storage (optional)
    # GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=/absolute/path/to/service_account.json
    # GDRIVE_FOLDER_ID=your-drive-folder-id

    # Backups (django-dbbackup)
    # DBBACKUP_STORAGE=gdrive
    # DBBACKUP_GDRIVE_FOLDER_ID=your-backup-folder-id

### 5) Ensure PostGIS is installed in your DB

Connect to your database and run:

    CREATE EXTENSION IF NOT EXISTS postgis;

### 6) Run migrations and create a superuser

    python manage.py migrate
    python manage.py createsuperuser

(Optional) collect static:

    python manage.py collectstatic

### 7) Start the development server

    python manage.py runserver

Visit: http://127.0.0.1:8000/

---

## Environment Variables (summary)

- `DEBUG` — `True`/`False`
- `SECRET_KEY` — Django secret key
- `ALLOWED_HOSTS` — Comma-separated hosts (production)
- `DB_*` — Database connection settings
- `MEMCACHED_HOST`, `MEMCACHED_PORT` — if using Memcached
- `REDIS_URL` — if using Redis
- `GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE`, `GDRIVE_FOLDER_ID` — for Google Drive storage
- `DBBACKUP_STORAGE`, `DBBACKUP_GDRIVE_FOLDER_ID` — for backups

---

## Caching (optional)

### Memcached (pymemcache)

- Install & run Memcached locally, then in `.env` set:

      MEMCACHED_HOST=127.0.0.1
      MEMCACHED_PORT=11211

- Configure `CACHES` in `settings.py` to use `pymemcache`.

### Redis

- Run Redis and set:

      REDIS_URL=redis://127.0.0.1:6379/1

- Configure `CACHES` in `settings.py` to use Redis (e.g., `django-redis` if you add it).

---

## Google Drive Storage (optional)

1. Create a **Google Cloud** project, enable Drive API.
2. Create a **Service Account**, generate a JSON key file.
3. Share your target Drive folder with the service account email.
4. Set in `.env`:

       GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=/absolute/path/to/service_account.json
       GDRIVE_FOLDER_ID=your-drive-folder-id

5. Configure your Django storage backend to use `django-googledrive-storage`.

---

## Backups with `django-dbbackup` (optional)

- Example `.env` for Drive:

      DBBACKUP_STORAGE=gdrive
      DBBACKUP_GDRIVE_FOLDER_ID=your-backup-folder-id

- Run:

      python manage.py dbbackup
      python manage.py dbrestore

---

## API & Docs

- REST API powered by DRF.
- If Swagger/Docs are enabled in `urls.py`, visit `/docs/` or `/swagger/`.

---

## Project Structure (simplified)

    mess_management6/
    ├─ accounts/                 # authentication / users
    ├─ mess/                     # core app (meals, plans, etc.)
    ├─ mess_management6/
    │  ├─ settings.py
    │  ├─ urls.py
    │  └─ wsgi.py / asgi.py
    ├─ static/                   # static files (if collected locally)
    ├─ media/                    # uploaded files
    ├─ requirements.txt
    ├─ .env
    └─ manage.py

---

## Troubleshooting

- **“Set the SECRET_KEY environment variable”**
  - Ensure `.env` exists in project root and is readable.
  - Confirm `django-environ` loads it (e.g., `env = environ.Env(); environ.Env.read_env()` in `settings.py`).

- **PostGIS error (`extension "postgis" is not available`)**
  - Install PostGIS on your PostgreSQL server and run `CREATE EXTENSION postgis;`.

- **GDAL import/build errors**
  - On Windows, install a GDAL wheel matching your Python & architecture.
  - Ensure the GDAL version matches your installed runtime.

- **Memcached backend error**
  - Install `pymemcache` (already in requirements) and ensure Memcached is running.
  - Verify your `CACHES` configuration is correct.

- **JWT / Swagger import errors**
  - Prefer `djangorestframework-simplejwt` for JWT in Django 4.2.
  - If using `django-rest-swagger`, keep versions aligned with DRF 3.14 (already pinned).

---

## Scripts you’ll use most

    # Start dev server
    python manage.py runserver

    # Migrations
    python manage.py makemigrations
    python manage.py migrate

    # Superuser
    python manage.py createsuperuser

    # Static files (prod)
    python manage.py collectstatic

    # Backups (if configured)
    python manage.py dbbackup
    python manage.py dbrestore

---

## Contributing

1. Create a feature branch:  
   
       git checkout -b feature/your-feature

2. Commit and push:

       git commit -m "Add your feature"
       git push origin feature/your-feature

3. Open a Pull Request 🚀

---

## License

This project is licensed under the **MIT License**.

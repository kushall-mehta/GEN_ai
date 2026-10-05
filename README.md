# Local Docker setup

1. Copy `.env.example` to `.env` and set a random `DJANGO_SECRET_KEY` and a
   strong alphanumeric `POSTGRES_PASSWORD`. Keep `api_services/.env` populated
   with the Hugging Face and Groq tokens and optional LangSmith settings;
   Docker Compose overrides `DATABASE_URL` to point at its PostgreSQL service.
2. Start the stack with `docker compose up --build -d`.
3. Index the diet and workout documents into the Compose database:
   `docker compose exec ai-api python -m rag.ingest`.
4. The current local database has the `asus` Django superuser. For a fresh
   database, create one interactively with
   `docker compose exec web python manage.py createsuperuser --username asus`.
   Choose a strong password; passwords are not stored in the image or Compose
   configuration.

Open <http://localhost:8000>. FastAPI is available to the other Compose services
as `http://ai-api:8081`; it is not published on the host. PostgreSQL data is
kept in the `postgres_data` Docker volume.
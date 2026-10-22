# Local Docker setup

1. Copy `.env.example` to `.env` and set a random `DJANGO_SECRET_KEY` and a
   strong alphanumeric `POSTGRES_PASSWORD`. Keep `api_services/.env` populated
   with `GEMINI_API_KEY`, `GROQ_API_KEY`, and optional LangSmith settings;
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

## Gemini embeddings on Render (Docker)

The API uses Gemini `gemini-embedding-2` with 768 dimensions for retrieval;
Groq still generates chat answers. The REST integration uses the existing
`requests` and `langchain-core` dependencies, so no new package is needed.
`HF_TOKEN` and `HF_EMBEDDING_MODEL` are no longer used.

1. Create a Gemini API key at <https://aistudio.google.com/apikey>.
2. Set `GEMINI_API_KEY` in the Render AI API service's Environment settings.
   Keep its existing `DATABASE_URL` and `GROQ_API_KEY` settings.
3. Deploy the updated code using `api_services/Dockerfile` with the repository
   root as the Docker build context.
4. From the Render API service Shell, index both PDFs into the new collection:
   `cd /app/api_services && python -m rag.ingest`.
   For local Compose use `docker compose exec ai-api python -m rag.ingest`.
5. Test `/chat` with diet and workout questions after indexing completes.

Indexing makes external Gemini requests and uses the account's quota. Free tier
availability and quotas are controlled by Google. If indexing hits a quota
limit, wait for the quota to reset and rerun the command; stable chunk IDs make
reruns update the same records. The API reads the new collection
`fitness_knowledge_gemini2_768_v1`; existing Hugging Face vectors are preserved
and must not be copied into it. Diet/workout retrieval needs this indexing step
before the new deployment is ready to serve those requests.

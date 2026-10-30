# Render to Vercel

Keep the existing Neon database. Deploy this repository as **two Vercel projects**:

| Project | Root Directory | Framework | Python |
| --- | --- | --- | --- |
| gym-ai-web | `backend` | Django | 3.14 |
| gym-ai-api | `api_services` | FastAPI | 3.14 |

Leave Install, Build, and Output Directory overrides empty. The service-specific
`pyproject.toml` and `uv.lock` install only that service's dependencies. Vercel's
Django integration collects static assets and serves them through its CDN.
Do not run Docker or Gunicorn on Vercel.

## Environment variables

Enter real values directly in Vercel Settings → Environment Variables; never
commit them or paste them in a chat. Use an isolated Neon branch for previews
if you do not want preview requests to change production data.

**Django website:**

- `DJANGO_SECRET_KEY`: reuse the existing production Django secret to preserve sessions.
- `DJANGO_DEBUG=False`
- `DATABASE_URL`: the existing Neon database's pooled PostgreSQL URL, including `sslmode=require`.
- `AI_API_URL`: `https://<AI-production-domain>/chat`
- `AI_API_KEY`: a random secret shared only with the AI project.
- `DJANGO_ALLOWED_HOSTS`: comma-separated custom domains, if any. The deployment,
  branch, and production Vercel hosts are added automatically.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: `https://` origins for custom domains, if any.

**AI API:**

- `DATABASE_URL`: Neon pooled PostgreSQL URL for the existing vector database.
  Both `postgresql://` and `postgresql+psycopg://` are accepted.
- `CHECKPOINT_DATABASE_URL`: a **direct, unpooled** Neon PostgreSQL URL for chat
  checkpoints. This avoids transaction-pooler prepared statement restrictions.
- `GROQ_API_KEY` and `GEMINI_API_KEY`: reuse the existing values.
- `AI_API_KEY`: the same random value configured on Django. `/chat` checks this header;
  the root health endpoint stays public. Keep Vercel Deployment Protection off for
  this API's production domain so Django can reach it; application authentication
  remains required. Protected preview deployments need a separately configured bypass.
- Optional existing `LANGSMITH_*` settings; keep input/output hiding enabled.

The same Neon database can contain both Django and vector/checkpoint tables.
Keep separate database URLs if your current setup uses different databases.

## Before releasing

Use local, private `.env` files or your terminal's environment. With `uv` installed:

```sh
cd backend
uv sync
uv run python manage.py check --deploy
uv run python manage.py migrate --plan
# Apply pending migrations only after reviewing the plan and taking a backup.
uv run python manage.py migrate --noinput
cd ../api_services
uv sync
uv run python setup_memory.py
```

`setup_memory.py` creates the LangGraph checkpoint tables once; it does not run
during HTTP requests or Vercel builds. Existing in-process chat memory cannot be
transferred from Render, so conversations start fresh. Accounts, profiles, saved
workouts, and indexed vectors stay in Neon.

Only re-index PDFs if the target Neon database lacks the existing collection
`fitness_knowledge_gemini2_768_v1`. Indexing makes billable/quota-limited Gemini calls:

```sh
cd api_services
uv sync --group ingest
uv run python -m rag.ingest
```

The PDFs are intentionally excluded from Vercel uploads; ingestion runs locally.

## Release and verify

1. Deploy the AI project; check `/` returns the API health message.
2. Set Django's `AI_API_URL` to the AI production URL and deploy Django.
3. Verify home, CSS, login, existing profile, a chat response, a follow-up question,
   and saving/reloading a workout. Confirm conversation continuity after redeployment.
4. Move any custom domain after these checks pass. Leave Render running until then.
5. Once the Vercel release is verified, disable the old Render web/API services.
   Retain the Neon database and its backups.

References: [Django](https://vercel.com/docs/frameworks/full-stack/django),
[FastAPI](https://vercel.com/docs/frameworks/backend/fastapi),
[persistent memory](https://docs.langchain.com/oss/python/langgraph/add-memory).

✅ CI/CD (GitHub Actions)

CI pipeline should:
- Trigger on push to `main`
- Run tests (`pytest`)
- Optionally run lint (black/isort, not enforced)
- Auto-deploy backend to Railway (when ready)

Frontend deployment handled separately via Vercel or Netlify (manual for now).

Lint is optional — test coverage is primary concern.

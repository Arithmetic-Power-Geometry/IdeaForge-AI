# Deployment Guide

## GitHub upload
Upload the **contents** of this repository folder, not the ZIP file itself. Keep `.github/workflows/`, `.streamlit/`, `src/`, `app/`, `tests/`, `data/`, `docs/`, `LICENSE`, `NOTICE`, `requirements.txt`, and `pyproject.toml` at repository root.

## Streamlit Community Cloud
1. Create a public or private GitHub repository.
2. Push this folder's contents.
3. In Streamlit Community Cloud choose **Create app**.
4. Select the repository and branch.
5. Main file path: `app/streamlit_app.py`.
6. Deploy.

## Optional OpenAI suggestions
The app does not require an API key for core operation. To enable live LLM suggestions, add secrets in Streamlit Cloud:

```toml
OPENAI_API_KEY = "your-secret-key"
OPENAI_MODEL = "your-supported-model-name"
```

Do not commit `.streamlit/secrets.toml`.

## Health check after deployment
- Load the worked energy case.
- Confirm q3: DC 0.750, QC 0.800, Region IV, utility 0.425, venture screen 79.0.
- Generate five questions from a keyword.
- Add one Manual assessment.
- Add one AI-assisted/guided assessment.
- Confirm Portfolio, Frontier & Sensitivity, Startup Studio, and Report downloads work.

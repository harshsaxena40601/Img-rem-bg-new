# Render + Vercel deployment

This project is split into:

- **Render:** Flask/OpenVINO image-processing API
- **Vercel:** static upload interface

## 1. Deploy the backend to Render

The repository includes `render.yaml`, so the easiest option is to create a
new Render Blueprint from the GitHub repository.

The blueprint:

- Uses Python 3.11
- Installs the lightweight API dependencies from
  `background-remover/requirements.txt`
- Downloads the MODNet ONNX model during the build
- Starts Flask with Gunicorn
- Exposes `/health` as the health check

If creating the service manually, use:

```text
Root Directory: background-remover
Build Command: pip install -r requirements.txt && python scripts/download_model.py
Start Command: gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 180 web_app:app
Health Check Path: /health
```

After the service deploys, verify:

```text
https://YOUR-RENDER-SERVICE.onrender.com/health
```

The first request after an idle period can take longer while the Render
instance wakes up and loads the OpenVINO model.

## 2. Deploy the frontend to Vercel

Create a Vercel project from the same GitHub repository and keep the project
root at the repository root. The included `vercel.json` configures the static
frontend build.

Add this Vercel environment variable:

```text
VITE_API_URL=https://YOUR-RENDER-SERVICE.onrender.com
```

Then redeploy. The build script writes this value into the generated
`frontend/dist/config.js`, and the browser uses it for `/health` and
`/process`.

The Vercel frontend does not need Python, OpenVINO, or the model files.

## 3. Restrict CORS after Vercel is live

The Render blueprint starts with open CORS so the first Vercel deployment can
connect. After you know the Vercel URL, set this Render environment variable:

```text
CORS_ORIGINS=https://YOUR-VERCEL-PROJECT.vercel.app
```

For a custom domain, use the custom domain instead. Separate multiple allowed
origins with commas.

## Local frontend preview

The frontend reads `frontend/.env` automatically. To switch between local
processing and the cloud API, change only `VITE_API_URL` in that file:

```text
# Local
VITE_API_URL=http://127.0.0.1:5000

# Cloud
VITE_API_URL=https://YOUR-RENDER-SERVICE.onrender.com
```

To preview the standalone frontend locally:

```bash
python3 frontend/build.py
cd frontend/dist
python3 -m http.server 4173
```

An environment variable overrides the `.env` file when needed:

```bash
VITE_API_URL=http://127.0.0.1:5000 python3 frontend/build.py
```

The `.env` file is for local use and is ignored by Git. Vercel uses the
`VITE_API_URL` project environment variable from its dashboard instead.
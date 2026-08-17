---
name: Render and Vercel deployment
description: Deployment boundary between the OpenVINO API and the static browser frontend.
---

The image-processing backend and browser frontend are deployed separately:

- Render owns the Flask/OpenVINO API and downloads the ignored MODNet ONNX file during its build.
- Vercel owns only static frontend files and injects the Render API origin at build time.
- Local frontend builds read the same `VITE_API_URL` from `frontend/.env`.
- The backend must expose CORS response headers and expose processing-time headers for the frontend.

**Why:** ONNX model files are intentionally not committed to source control, and Vercel is not an appropriate runtime for the OpenVINO process.

**How to apply:** Keep Render-specific dependencies lightweight and separate from the research/CLI dependencies. Change `frontend/.env` for local/cloud use, use the same `VITE_API_URL` variable in Vercel, then restrict Render `CORS_ORIGINS` to the deployed frontend origin.
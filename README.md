# MediSync Backend

Backend API for MediSync: a medical assistance service that provides text-based triage/diagnosis, medical image analysis, and prescription OCR/cleanup. This README focuses on the backend integration, endpoints, setup, and operations — highlighting how external ML models are integrated rather than how those models work internally.

## Overview

MediSync-Backend is a Python/Flask API that exposes three primary capabilities:

- Text diagnosis: Generate a structured diagnosis summary given basic patient details and symptoms.
- Image analysis: Accept a medical image (e.g., X-ray/MRI) and return an AI-generated assessment.
- Prescription processing: Extract and clean text from photographed prescriptions.

The backend integrates with:

- Google Gemini via `google-generativeai` for text and image reasoning.
- OpenAI for prescription OCR/cleanup (vision-enabled chat models).

The backend itself handles: request validation, file handling, CORS, environment configuration, and uniform JSON responses.

## Stack

- Language: Python 3.10+ (recommended)
- Web framework: Flask (`Flask`, `flask-cors`)
- Model integrations:
  - Google Gemini via `google-generativeai`
  - OpenAI Chat API for vision/OCR
- Serving (production): `gunicorn` (see `render-start.sh`)
- Package manager: pip (`requirements.txt`)

## Project Structure

```
F:/MediSync-Backend
├─ server.py               # Flask app: routes, CORS, startup
├─ TextModel.py            # Gemini text integration for diagnosis
├─ ImageModel.py           # Gemini image integration for image analysis
├─ prescription.py         # OpenAI-based prescription processing
├─ requirements.txt        # Python dependencies
├─ render-start.sh         # Production start command (gunicorn)
└─ README.md               # This file
```

## Entry Points & Scripts

- Development entry point: `server.py` (runs Flask app)
  - Dev server uses environment variable `PORT` if set, defaults to `10000`.
- Production script: `render-start.sh`
  - Command: `gunicorn server:app --bind 0.0.0.0:$PORT`

## API Endpoints

All responses are JSON. CORS is enabled for all routes.

1) Image Analysis (Gemini)
- URL: `POST /analyze`
- Form-data:
  - `image`: binary file (required)
  - `symptoms`: string (optional; defaults to `none`)
- Response: `{ "diagnosis": string }`

Example (curl):
```
curl -X POST http://localhost:10000/analyze \
  -F "image=@/path/to/scan.jpg" \
  -F "symptoms=chest pain and cough"
```

2) Text Diagnosis (Gemini)
- URL: `GET /diagnose`
- Query parameters (all required unless noted):
  - `name`, `age`, `gender`, `symptoms`
  - `medicalHistory` (optional)
- Response: includes input echo and `diagnosis` field.

Example:
```
curl "http://localhost:10000/diagnose?name=Alex&age=42&gender=male&symptoms=fever%2C%20cough&medicalHistory=asthma"
```

3) Prescription Processing (OpenAI)
- URL: `POST /prescriptionanalyze`
- Form-data:
  - `image`: binary file (required)
- Response: `{ "extracted_text": string }`

Example:
```
curl -X POST http://localhost:10000/prescriptionanalyze \
  -F "image=@/path/to/prescription.png"
```

## Environment Variables

- `GOOGLE_API_KEY` (required): Used by `TextModel.py` and `ImageModel.py` via `google-generativeai`.
- `PORT` (optional): Port for Flask/gunicorn. Defaults to `10000` in `server.py`.

Important security note for `prescription.py`:
- The file currently hardcodes an OpenAI API key and prints environment variables. This is not safe for production.
- TODO: Replace the hardcoded key with an environment variable (e.g., `OPENAI_API_KEY`) and remove debug prints. Update code to read `OPENAI_API_KEY` from the environment.

## Requirements

Install Python (3.10+ recommended) and pip. Dependencies are listed in `requirements.txt`.

Note: The requirements file is comprehensive and includes libraries for image processing and Streamlit. Only a subset is used directly by the Flask API. Keep as-is unless you plan to trim it safely.

## Setup (Local)

1) Clone and enter the project directory.
2) Create and activate a virtual environment.
   - Windows (PowerShell):
     ```
     py -3 -m venv .venv
     .\.venv\Scripts\Activate
     ```
   - macOS/Linux:
     ```
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3) Install dependencies:
   ```
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4) Set environment variables:
   - Windows (PowerShell):
     ```
     $env:GOOGLE_API_KEY="<your-gemini-key>"
     $env:PORT="10000"  # optional
     # TODO after code change: $env:OPENAI_API_KEY="<your-openai-key>"
     ```
   - macOS/Linux:
     ```
     export GOOGLE_API_KEY="<your-gemini-key>"
     export PORT=10000  # optional
     # TODO after code change: export OPENAI_API_KEY="<your-openai-key>"
     ```

## Running

Development:
```
python server.py
```
The app binds to `0.0.0.0` on `PORT` (default 10000).

Production (gunicorn):
```
gunicorn server:app --bind 0.0.0.0:$PORT
```
On Render, this is executed via `render-start.sh`.

## How ML Models Are Integrated (Backend Focus)

- TextModel (`TextModel.py`):
  - Loads `GOOGLE_API_KEY` from the environment using `python-dotenv` support if a `.env` file exists.
  - Uses `google-generativeai` to instantiate the Gemini model (`gemini-1.5-flash`).
  - Backend assembles a prompt from request parameters and returns the model's text output, with minimal cleanup to remove disclaimers.

- ImageModel (`ImageModel.py`):
  - Same Gemini setup; accepts raw image bytes from `multipart/form-data` uploads.
  - Sends both the instruction prompt and the image to the model and returns the text output.

- Prescription (`prescription.py`):
  - Uses OpenAI's vision-enabled chat API to extract and correct text from a prescription image. Currently contains hardcoded API key and debug prints — see TODO below.

The backend treats these providers as services: it validates inputs, prepares requests (prompts and image bytes), calls the provider SDKs, and returns normalized JSON responses. Model selection, prompts, and post-processing live in the `*Model.py` modules and can be swapped or refined without changing the HTTP layer.

## Tests

No automated tests are present in the repository.

TODOs:
- Add unit tests for:
  - `clean_text` in `server.py`.
  - Parameter validation for `/diagnose`.
  - File handling and error paths for `/analyze` and `/prescriptionanalyze`.
- Add integration tests that exercise all endpoints with mocked model clients.

## Deployment Notes

- CORS is enabled for all routes via `flask-cors`.
- `render-start.sh` is set up for Render.com style deployments using `PORT`.
- Ensure environment variables are configured in your hosting provider.

## Troubleshooting

- 401/403/permission errors from model providers:
  - Verify `GOOGLE_API_KEY` (and later `OPENAI_API_KEY`) are set and valid.
- 500 errors on `/prescriptionanalyze`:
  - Check that the image was saved successfully; ensure Pillow can read the format.
- Dependencies fail to build:
  - Ensure a compatible Python version and system packages for image/torch libraries.

## Roadmap / TODO

- Replace hardcoded OpenAI key with `OPENAI_API_KEY` env var and remove environment prints from `prescription.py`.
- Consolidate/trim `requirements.txt` to only necessary packages if feasible.
- Add logging, error codes, and structured validation.
- Add authentication/authorization if endpoints require protection.

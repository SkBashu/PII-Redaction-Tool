# Cloud Deployment Readiness & Privacy Specification

**System:** PII Redaction Tool API / Web Service  
**Target Platforms:** Render / Railway / Streamlit Cloud / AWS Lambda

---

## 1. Runtime Specifications

- **Runtime**: Python 3.11+
- **Build Command**: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
- **Start Command**: `python redaction.py` (or web framework entrypoint e.g., `uvicorn main:app --host 0.0.0.0 --port 8000`)
- **Required System Dependencies**: standard C++ runtime for spaCy regex extensions.

---

## 2. Privacy & Data Handling Specification

When deployed as a web service or API:
1. **Zero Permanent Storage**: Uploaded `.docx` files MUST be stored in ephemeral temporary directories (`/tmp`) and deleted immediately after redaction.
2. **Zero Logging of Document Contents**: Application logs MUST NOT print raw paragraph text, detected PII values, or unredacted entity surfaces.
3. **Randomized Output URIs**: Redacted output files must be served via non-predictable UUID-based download links (`/download/<uuid>`).
4. **Automatic Cleanup Cron**: Ephemeral files in `/tmp` must expire after 10 minutes.
5. **No Confidential Source Inclusion**: The original `Red Herring Prospectus.docx` MUST NOT be uploaded to the cloud host.

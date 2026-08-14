# Deployment Error Analysis

Audit date: 2026-08-14

## Evidence status

No Vercel project, deployment URL, or runtime-log connector is available in
this workspace. Therefore the complete production traceback, exception type,
message, failing line, and import that caused `FUNCTION_INVOCATION_FAILED`
are **not available for inspection**. The previous version of this document
asserted a spaCy download traceback without log evidence; that claim has been
removed.

## Local reproduction

The production import path succeeds locally:

```text
py -c "import app; print('app import OK')"
py -c "import redaction; print('redaction import OK')"
```

`api/index.py` was a redundant wrapper around `app.py`, not an independent
application. It has been removed. The project now has one Flask application
entrypoint, `app.py`, which is a Vercel-recognized Flask entrypoint.

## Deployment-relevant findings and fixes

1. The old catch-all rewrite directed all traffic to a second function wrapper.
   Vercel detects Flask applications with a top-level `app` in `app.py`, so
   the deployment now uses that single entrypoint and a minimal bundle-exclude
   configuration.
2. `app.py` does not import the redaction core until a redaction or evaluation
   request needs it. `/`, `/api/health`, `/api/info`, and `/api/demo` therefore
   do not initialize spaCy.
3. The core uses `spacy.blank("en")` when `en_core_web_sm` is unavailable. It
   does not download a model at request time.
4. DOCX uploads are copied to randomized temporary files and deleted in the
   route's `finally` block. The response is buffered before cleanup, so it does
   not depend on a persistent upload or output file.
5. `/api/evaluate` had an independent response bug: it returned F1 as
   `coverage`. It now calculates coverage from `TP / (TP + FP + FN)` and marks
   TN and conventional accuracy as undefined.

## Remaining production diagnostic step

Retrieve the failing deployment's Vercel Runtime Logs and record the complete
traceback before attributing the original 500 to a particular exception. After
deployment, test the actual URL; build completion is not production proof.

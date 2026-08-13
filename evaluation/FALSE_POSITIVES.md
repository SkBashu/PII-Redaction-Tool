# Benchmark False Positives Audit Report

**Audit Date:** 2026-08-14  
**Target Dataset:** `evaluation/gold_standard.json` (33 snippets, 30 canonical gold entities)

---

## Benchmark Audit Finding

> **"No false positives were observed in the current frozen evaluation benchmark."**

---

## Baseline False Positive Resolution Summary

During initial baseline evaluation, 2 false positives were identified in snippet `company_001`:
1. `Predicted: "Managed by Infosys Limited"`
2. `Predicted: "and TCS Private Limited"`

### Root Cause & Resolution
- **Root Cause**: `re.IGNORECASE` in `detect_companies` matched leading preposition phrases ("Managed by") and conjunctions ("and").
- **Resolution**: Updated `clean_company_name` and `looks_like_company` in `redaction.py` and `evaluate.py` to strip leading prepositions/conjunctions (`"managed by"`, `"and"`, `"by"`, `"for"`, `"with"`, `"or"`) and enforce case-sensitive prefix matching.
- **Current False Positives Count**: **0** ($\text{Precision} = 1.0000$).

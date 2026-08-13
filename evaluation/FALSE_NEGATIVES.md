# Benchmark False Negatives Audit Report

**Audit Date:** 2026-08-14  
**Target Dataset:** `evaluation/gold_standard.json` (33 snippets, 30 canonical gold entities)

---

## Benchmark Audit Finding

> **"No false negatives were observed in the current frozen evaluation benchmark."**

---

## Audit Verification Summary

- **Total Canonical Gold Entities**: 30
- **Total True Positives**: 30
- **Total False Negatives**: **0** ($\text{Recall} = 1.0000$)

All 30 annotated gold entities across all 9 PII categories were successfully detected and matched by the system.

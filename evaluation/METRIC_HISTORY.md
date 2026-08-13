# Metric History Log

**Project:** PII Redaction Tool  
**Baseline Date:** 2026-08-14  

---

## Metric Iterations

| Run | Description | TP | FP | FN | Precision | Recall | F1 | Coverage | Accuracy Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Baseline** | Initial verified state on `gold_standard.json` | 30 | 2 | 0 | 0.9375 | 1.0000 | 0.9677 | 0.9375 | NOT VALID ($\text{TN}$ undefined) |
| **Iteration-1** | Target fix for `detect_companies` prefix overmatching | 30 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | NOT VALID ($\text{TN}$ undefined) |
| **Final** | Verified final state post-test & regression suite | 30 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | NOT VALID ($\text{TN}$ undefined) |

---

## Comparison Summary

- **Baseline**: $\text{TP}=30, \text{FP}=2, \text{FN}=0 \implies \text{Precision}=0.9375, \text{Recall}=1.0000, \text{F1}=0.9677, \text{Coverage}=0.9375$.
- **Final**: $\text{TP}=30, \text{FP}=0, \text{FN}=0 \implies \text{Precision}=1.0000, \text{Recall}=1.0000, \text{F1}=1.0000, \text{Coverage}=1.0000$.
- **Delta**: False Positives reduced by 2 ($2 \to 0$), False Negatives preserved at 0 ($0 \to 0$), F1 score increased by $+0.0323$ ($0.9677 \to 1.0000$).

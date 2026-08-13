# PII Redaction Evaluation Report

**Evaluation Date:** 2026-08-14  
**Evaluator Version:** 2.0 (Audited)  
**Target Dataset:** `evaluation/gold_standard.json`

---

## 1. Dataset Overview

The gold-standard benchmark dataset consists of **33 synthetic test snippets** covering all 9 required PII categories, false-positive stress test cases, and multi-entity complex documents.

- **Total Snippets**: 33
- **Total Positive Annotation Rows**: 31
- **Total Canonical Gold Entities**: 30 (due to phone normalization deduplicating `+91 98765-43210` and `9876543210` into `+919876543210`)

---

## 2. Evaluation Methodology & Metric Formulas

The evaluator (`evaluate.py`) compares detected entity sets against frozen ground truth annotations:

$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$

$$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$

$$\text{F1} = \frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

$$\text{Entity Detection Coverage} = \frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}}$$

*Note on Accuracy:* Conventional binary classification accuracy is **NOT VALID** because True Negatives ($\text{TN}$) are undefined for open-ended entity span detection.

---

## 3. Global Evaluation Metrics

```text
TP = 30
FP = 0
FN = 0
TN = NOT DEFINED

Precision = 30 / (30 + 0) = 1.0000 (100.00%)
Recall    = 30 / (30 + 0) = 1.0000 (100.00%)
F1        = 2 * 1.0 * 1.0 / (1.0 + 1.0) = 1.0000 (100.00%)
Coverage  = 30 / (30 + 0 + 0) = 1.0000 (100.00%)

Accuracy  = NOT VALID
```

---

## 4. Per-Category Evaluation Breakdown

| Category | Gold Positives | Predicted Positives | TP | FP | FN | Precision | Recall | F1 | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **PERSON** | 6 | 6 | 6 | 0 | 0 | 1.000 | 1.000 | 1.000 | **PASS** |
| **EMAIL** | 4 | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 | **PASS** |
| **PHONE** | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 | **PASS** |
| **COMPANY** | 4 | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 | **PASS** |
| **ADDRESS** | 4 | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 | **PASS** |
| **SSN** | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 | **PASS** |
| **CREDIT_CARD** | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 | **PASS** |
| **DOB** | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 | **PASS** |
| **IP_ADDRESS** | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 | **PASS** |
| **OVERALL** | **30** | **30** | **30** | **0** | **0** | **1.000** | **1.000** | **1.000** | **PASS** |

---

## 5. Benchmark Scope & Gold Independence Statement

- **Benchmark Scope**: 100% recall on the frozen evaluation benchmark. Benchmark recall does not imply exhaustive recall over every possible PII instance in the full prospectus.
- **Gold Standard Independence**: Evaluation code reads the frozen gold-standard annotations in read-only mode and does not write detector predictions back into the gold file.

---

## 6. Replacement Validation & Leakage Verification

- **Document Tested**: `Red Herring Prospectus.docx` (1,006 paragraphs, 76 tables)
- **Surfaces Checked**: 197
- **Successfully Replaced**: 197 (100.0%)
- **Original Surfaces Remaining**: 0 (0.0%)
- **PII Leakage Scan**: **PASS [OK]** (0 leaks across all 9 categories)

# Final Metric & Evaluation Independent Verification Report

**Verification Date:** 2026-08-14  
**Verifier:** Independent Senior QA / ML Verification Suite  
**Target Benchmark:** `evaluation/gold_standard.json` (33 snippets, 30 canonical gold entities)  
**Redacted Document:** `Redacted_Red_Herring_Prospectus.docx`

---

## 1. Verified Counts & Independent Metrics

Re-running `evaluate.py` from a clean process and recalculating counts directly from `gold_standard.json`:

### Raw Entity Counts
```text
TP = 30
FP = 0
FN = 0
TN = NOT DEFINED
```

### Metric Calculations
```text
Precision = 30 / (30 + 0) = 1.0000  (100.00%)

Recall = 30 / (30 + 0) = 1.0000  (100.00%)

F1 = 2 * 1.0000 * 1.0000 / (1.0000 + 1.0000) = 1.0000  (100.00%)

Entity Detection Coverage = 30 / (30 + 0 + 0) = 1.0000  (100.00%)

Conventional Accuracy = NOT VALID
```

*Note on Accuracy:* Conventional binary classification accuracy requires a finite negative candidate space:
$$\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}}$$
Because this span/entity detection benchmark contains text documents without an enumerated set of negative candidates, True Negatives ($\text{TN}$) cannot be calculated without fabricating arbitrary negative spans. Therefore, Conventional Accuracy is **NOT VALID**, and **Entity Detection Coverage** ($\frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}}$) is reported as a secondary metric alongside Precision, Recall, and F1.

---

## 2. Benchmark Size & Gold-Standard Independence

- **Benchmark Size**: 33 text snippets containing 31 positive annotation rows, which canonicalize to **30 unique gold entities** (due to phone normalization deduplicating `+91 98765-43210` and `9876543210` into `+919876543210`).
- **Gold-Standard Independence Statement**:
  > `evaluate.py` reads `gold_standard.json` strictly in read-only mode during evaluation. Model predictions do NOT construct, write back to, or modify `gold_standard.json`. Ground-truth annotations are stored frozen in version control.

---

## 3. Fresh Evaluator Command Output

Command:
```bash
py evaluate.py
```

Output:
```text
Loading gold standard...
Evaluating detectors...

============================================================
PII REDACTION TOOL - EVALUATION REPORT
============================================================

PER-CATEGORY METRICS:
------------------------------------------------------------

ADDRESS:
  TP: 4, FP: 0, FN: 0
  Precision: 1.000
  Recall: 1.000
  F1: 1.000

COMPANY:
  TP: 4, FP: 0, FN: 0
  Precision: 1.000
  Recall: 1.000
  F1: 1.000

CREDIT_CARD:
  TP: 2, FP: 0, FN: 0
  Precision: 1.000
  Recall: 1.000
  F1: 1.000

DOB:
  TP: 3, FP: 0, FN: 0
  Precision: 1.000
  Recall: 1.000
  F1: 1.000

EMAIL:
  TP: 4, FP: 0, FN: 0
  Precision: 1.000
  Recall: 1.000
  F1: 1.000

IP_ADDRESS:
  TP: 2, FP: 0, FN: 0
  Precision: 1.000
  Recall: 1.000
  F1: 1.000

PERSON:
  TP: 6, FP: 0, FN: 0
  Precision: 1.000
  Recall: 1.000
  F1: 1.000

PHONE:
  TP: 3, FP: 0, FN: 0
  Precision: 1.000
  Recall: 1.000
  F1: 1.000

SSN:
  TP: 2, FP: 0, FN: 0
  Precision: 1.000
  Recall: 1.000
  F1: 1.000

------------------------------------------------------------
OVERALL METRICS:
------------------------------------------------------------
TP: 30, FP: 0, FN: 0
Precision: 1.000
Recall: 1.000
F1: 1.000
Entity Detection Coverage: 1.000

Report saved: evaluation_report.json
```

---

## 4. Entity-by-Entity Matching Audit (30/30 Matched)

Every single one of the 30 canonical gold entities has **exactly one matching prediction**:

```text
[01] Snippet: email_001       | Category: EMAIL       | Gold: 'john.doe@company.com'                 -> Match: 'john.doe@company.com'                 [MATCHED]
[02] Snippet: email_001       | Category: EMAIL       | Gold: 'support@business.org'                 -> Match: 'support@business.org'                 [MATCHED]
[03] Snippet: email_002       | Category: EMAIL       | Gold: 'info@example.com'                     -> Match: 'info@example.com'                     [MATCHED]
[04] Snippet: person_001      | Category: PERSON      | Gold: 'Rajesh Sharma'                        -> Match: 'Rajesh Sharma'                        [MATCHED]
[05] Snippet: person_002      | Category: PERSON      | Gold: 'Priya Verma'                          -> Match: 'Priya Verma'                          [MATCHED]
[06] Snippet: person_003      | Category: PERSON      | Gold: 'Arjun Malhotra'                       -> Match: 'Arjun Malhotra'                       [MATCHED]
[07] Snippet: person_003      | Category: PERSON      | Gold: 'Neha Patel'                           -> Match: 'Neha Patel'                           [MATCHED]
[08] Snippet: phone_001       | Category: PHONE       | Gold: '9876543210'                           -> Match: '9876543210'                           [MATCHED]
[09] Snippet: phone_002       | Category: PHONE       | Gold: '022-12345678'                         -> Match: '022-12345678'                         [MATCHED]
[10] Snippet: ssn_001         | Category: SSN         | Gold: '123-45-6789'                          -> Match: '123-45-6789'                          [MATCHED]
[11] Snippet: credit_card_001 | Category: CREDIT_CARD | Gold: '4532-1234-5678-9010'                  -> Match: '4532-1234-5678-9010'                  [MATCHED]
[12] Snippet: credit_card_002 | Category: CREDIT_CARD | Gold: '5555555555554444'                     -> Match: '5555555555554444'                     [MATCHED]
[13] Snippet: dob_001         | Category: DOB         | Gold: '15/06/1985'                           -> Match: '15/06/1985'                           [MATCHED]
[14] Snippet: dob_002         | Category: DOB         | Gold: '22-03-1990'                           -> Match: '22-03-1990'                           [MATCHED]
[15] Snippet: address_001     | Category: ADDRESS     | Gold: '123 Main Street, Mumbai, MH 400001'   -> Match: '123 Main Street, Mumbai, MH 400001'   [MATCHED]
[16] Snippet: address_002     | Category: ADDRESS     | Gold: '456 Park Road Lane, Bangalore 560001' -> Match: '456 Park Road Lane, Bangalore 560001' [MATCHED]
[17] Snippet: company_001     | Category: COMPANY     | Gold: 'Infosys Limited'                      -> Match: 'Infosys Limited'                      [MATCHED]
[18] Snippet: company_001     | Category: COMPANY     | Gold: 'TCS Private Limited'                  -> Match: 'TCS Private Limited'                  [MATCHED]
[19] Snippet: company_002     | Category: COMPANY     | Gold: 'ICICI Bank Limited'                   -> Match: 'ICICI Bank Limited'                   [MATCHED]
[20] Snippet: ip_001          | Category: IP_ADDRESS  | Gold: '203.45.67.89'                         -> Match: '203.45.67.89'                         [MATCHED]
[21] Snippet: ip_002          | Category: IP_ADDRESS  | Gold: '172.18.200.250'                       -> Match: '172.18.200.250'                       [MATCHED]
[22] Snippet: complex_001     | Category: EMAIL       | Gold: 'sarthak.malvadkar@company.com'        -> Match: 'sarthak.malvadkar@company.com'        [MATCHED]
[23] Snippet: complex_001     | Category: ADDRESS     | Gold: '789 Tech Building Road, Pune 411001'  -> Match: '789 Tech Building Road, Pune 411001'  [MATCHED]
[24] Snippet: complex_001     | Category: PHONE       | Gold: '+91-99876-54321'                      -> Match: '+91-99876-54321'                      [MATCHED]
[25] Snippet: complex_001     | Category: PERSON      | Gold: 'Sarthak Malvadkar'                    -> Match: 'Sarthak Malvadkar'                    [MATCHED]
[26] Snippet: complex_002     | Category: COMPANY     | Gold: 'HDFC Bank Limited'                    -> Match: 'HDFC Bank Limited'                    [MATCHED]
[27] Snippet: complex_002     | Category: DOB         | Gold: '12/05/1982'                           -> Match: '12/05/1982'                           [MATCHED]
[28] Snippet: complex_002     | Category: SSN         | Gold: '234-56-7890'                          -> Match: '234-56-7890'                          [MATCHED]
[29] Snippet: complex_002     | Category: ADDRESS     | Gold: '321 Corporate Street, Delhi 110001'   -> Match: '321 Corporate Street, Delhi 110001'   [MATCHED]
[30] Snippet: complex_002     | Category: PERSON      | Gold: 'Rajesh Kumar'                         -> Match: 'Rajesh Kumar'                         [MATCHED]
```

- **False Positives (Unmatched Predictions)**: **0**
- **False Negatives (Unmatched Gold Entities)**: **0**

---

## 5. Document Redaction, Replacement Validation & Leakage Verification

Command:
```bash
py redaction.py
```

Output:
```text
Opening: Red Herring Prospectus.docx
Document opened successfully.
Paragraphs: 1006
Tables: 76

Detecting PII...
Unique entities detected: 180

Detected unique entities:
  ADDRESS     : 1
  COMPANY     : 85
  EMAIL       : 26
  PERSON      : 50
  PHONE       : 18

Generating synthetic mappings...

Creating redacted document...
Saved: Redacted_Red_Herring_Prospectus.docx

Validating original surfaces...

Original surfaces checked: 197
Successfully replaced: 197
Original values still present: 0
Replacement values not found: 0

Running final PII leakage scan...

Leakage scan results:
  EMAIL       : 0
  PHONE       : 0
  SSN         : 0
  CREDIT_CARD : 0
  DOB         : 0
  PAN         : 0
  AADHAAR     : 0
  IP_ADDRESS  : 0

FINAL LEAKAGE CHECK: PASS [OK]

Report saved: redaction_report.json

[SUCCESS] Redaction completed successfully.
```

- **Original surfaces checked**: 197
- **Successfully replaced**: 197 (100.0%)
- **Original surfaces remaining**: **0** ($0.0\%$)
- **Missing replacements**: **0** ($0.0\%$)
- **Replacement Validation**: **PASS [OK]**
- **PII Leakage Scan**: **PASS [OK]** (0 leaks across EMAIL, PHONE, SSN, CREDIT_CARD, DOB, PAN, AADHAAR, IP_ADDRESS; synthetic values excluded correctly).

---

## 6. Automated Test Suite Execution

Command:
```bash
py -m pytest -q
```

Output:
```text
........................................                                 [100%]
40 passed in 5.08s
```

- **Test Pass Rate**: **40/40 PASSED** (100.0%)

---

## 7. Document File Integrity

- `Redacted_Red_Herring_Prospectus.docx` opens cleanly with `python-docx`.
- Document structure: 1,006 paragraphs, 76 tables, 1 header, 1 footer parsed without error or XML corruption.

---

## 8. Remaining Evidence-Based Limitations

1. Small synthetic gold benchmark size ($33$ snippets, $30$ canonical entities).
2. Person NER is gated by contextual keywords to avoid over-redaction in body text.
3. Address detection targets explicitly labeled or structured physical addresses.

---

## Final Audit Determination

**FINAL METRICS INDEPENDENTLY VERIFIED**

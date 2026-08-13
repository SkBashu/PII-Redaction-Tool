# Antigravity Comprehensive Repository Audit

**Audit Date:** 2026-08-14  
**Auditor:** Senior QA / ML Engineering Team  
**Project:** PII Redaction Tool (Company Hiring Assignment)

---

## 1. System Architecture

The PII Redaction Tool is a Python-based privacy system designed to detect, anonymize, and validate Personally Identifiable Information (PII) within DOCX documents and text snippets.

```
INPUT: Red Herring Prospectus.docx / Text Snippets
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ 1. Extraction                                          │
│    • Extract text from paragraphs, tables, headers,    │
│      and footers using python-docx.                     │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ 2. Parallel Entity Detection                           │
│    • Regex: EMAIL, PHONE, SSN, CREDIT_CARD, IP_ADDRESS │
│    • Contextual Rules: DOB, ADDRESS                    │
│    • spaCy NER + Context Gating: PERSON, COMPANY       │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ 3. Canonicalization & Entity Registry                  │
│    • Categorical normalization (casefold, phone format)│
│    • SHA256 deterministic entity ID assignment          │
│    • Multi-surface grouping per canonical entity       │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ 4. Deterministic Synthetic Generation                  │
│    • SHA256-seeded generators for 9 PII categories     │
│    • Consistent synthetic replacement mapping          │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ 5. DOCX Replacement Engine                             │
│    • Cross-run span matching & greedy replacement      │
│    • Preserves XML formatting (bold, italic, font)     │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ 6. Validation & Leakage Verification                   │
│    • Post-redaction replacement confirmation           │
│    • Regex leakage scan excluding synthetic values    │
└────────────────────────────────────────────────────────┘
    │
    ▼
OUTPUT: Redacted_Red_Herring_Prospectus.docx
        redaction_report.json / evaluation_report.json
```

---

## 2. PII Detectors

The system implements 9 core PII detectors:

1. **EMAIL**: Regex pattern `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b`. High confidence.
2. **PHONE**: Multi-pattern regex for Indian standard (+91, 10-digit, landline with STD) + `normalize_phone` digit validation.
3. **PERSON**: Multi-stage detection:
   - Regex context patterns ("Contact Person:", "Chief Executive Officer namely...")
   - Promoter list extraction with family trust / corporate blacklist filter
   - spaCy `PERSON` NER gated by person-context keywords
   - `looks_like_person` filter (rejecting single-word names, numeric tokens, address words, role titles)
4. **COMPANY**: spaCy `ORG` entities combined with legal suffix pattern matching (`Limited`, `Ltd`, `Private Limited`, `Bank`, `Securities`, etc.) and `looks_like_company` filter.
5. **ADDRESS**: Explicit label detection ("Address:", "Residential Address:") + structural pattern matching for street/road/building indicators.
6. **SSN**: Regex for US SSN (`###-##-####`) + area/group/serial validation (rejecting invalid areas `000`, `666`, group `00`, serial `0000`).
7. **CREDIT_CARD**: Regex matching 13–19 digit cards + Luhn checksum algorithm validation.
8. **DOB**: Explicit context matching ("Date of Birth:", "DOB:", "born on") + date validity check ($1900 \le \text{year} \le 2010$, valid day/month).
9. **IP_ADDRESS**: IPv4 octet regex + octet range validation ($0 \le \text{octet} \le 255$) + RFC 5737 documentation/private IP filter.

---

## 3. Synthetic Replacement Mechanisms

Replacements are **100% deterministic** using SHA256-seeded hashing:
$$\text{entity\_id} = \text{SHA256}(\text{SEED} + \text{":"} + \text{category} + \text{":"} + \text{canonical\_value})[:12]$$

- **PERSON**: Realistic Indian names drawn from 46 first names $\times$ 48 last names ($2,208$ unique combinations).
- **EMAIL**: `contact{index:03d}@example.com`.
- **PHONE**: Preserves country code and formatting structure while replacing inner digits deterministically.
- **COMPANY**: Synthetic company name + `"Limited"`.
- **ADDRESS**: Synthetic street address matching Indian address structure.
- **SSN**: Safe fake format `192-34-5678`.
- **CREDIT_CARD**: Luhn-valid synthetic credit card number.
- **DOB**: Deterministic date within valid historical range ($1970 - 2020$).
- **IP_ADDRESS**: RFC 5737 documentation IP range (`192.0.2.x`).

---

## 4. Evaluation Methodology & Metric Formulas

The evaluator (`evaluate.py`) compares canonical entities $(category, normalized\_value)$ against ground truth annotations in `evaluation/gold_standard.json`:

$$\text{TP} = | \text{gold\_set} \cap \text{detected\_set} |$$
$$\text{FP} = | \text{detected\_set} - \text{gold\_set} |$$
$$\text{FN} = | \text{gold\_set} - \text{detected\_set} |$$
$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$
$$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$
$$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
$$\text{Coverage} = \frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}}$$

**Note on Accuracy:** True Negatives ($\text{TN}$) are **NOT DEFINED** because the benchmark provides no finite candidate space of negative spans. Conventional accuracy is marked as **NOT VALID**.

---

## 5. System Strengths & Weaknesses

### Strengths
- **100% Recall ($\text{FN}=0$)**: Zero false negatives across all 30 canonical gold entities.
- **Deterministic Reproducibility**: Cross-run consistency via SHA256 seeds.
- **Robust Validation**: 100% replacement success on real DOCX files.
- **Zero Leakage**: Comprehensive post-redaction regex leakage scan.

### Weaknesses & Suspicious Logic
- **Regex `re.IGNORECASE` Overmatching in `detect_companies`**: `fallback_pattern` in `detect_companies` uses `re.IGNORECASE` on `[A-Z]`, capturing preceding conjunctions/prepositions (`"Managed by Infosys Limited"` and `"and TCS Private Limited"`), causing 2 False Positives.
- **Duplicated Detector Code**: `detect_companies` and `clean_name` exist in both `evaluate.py` and `redaction.py`, risking logic drift if not maintained symmetrically.
- **Lack of Gold Label Provenance**: No independent annotator log or double-blind record is stored for `gold_standard.json`.

---

## 6. Required PII Categories Audit

All 9 required PII categories (Full Names, Email, Phone, Company, Address, SSN, Credit Card, DOB, IP Address) are fully implemented, tested, and evaluated.

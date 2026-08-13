# PII Redaction Tool

A production-grade, privacy-preserving PII (Personally Identifiable Information) detection, redaction, and synthetic anonymization system designed for complex Microsoft Word (`.docx`) documents and unstructured text.

---

## Overview

The **PII Redaction Tool** provides end-to-end detection, canonicalization, deterministic synthetic replacement, and validation for 9 core PII categories. Designed for regulatory compliance (GDPR, DPDP, HIPAA) and sensitive document processing, it processes Microsoft Word documents while preserving formatting, table structures, headers, and footers.

---

## Problem

Unstructured corporate documents—such as prospectus filings, legal agreements, and financial reports—contain dense, sensitive PII. Simple string replacement or regex-only redaction often fails due to:
1. **Formatting Complexity**: Text spans split across multiple Word XML run nodes (`w:r`).
2. **Entity Inconsistency**: Variations of the same entity (e.g. `+91 98765-43210` vs `9876543210`) receiving different replacements across a document.
3. **High False Positive Risk**: Generic prose (e.g. "Managed by", "Air Conditioning", "Offer Escrow") falsely redacted as PII.
4. **PII Leakage**: Residual entity occurrences or improperly sanitized synthetic values remaining after processing.

This tool solves these challenges using context-aware NLP detection, canonical entity registration, deterministic SHA256 synthetic generation, run-aware DOCX span replacement, and post-redaction leakage scanning.

---

## Supported PII Categories

| Category | Detection Method | Validation Rule | Example Synthetic Replacement |
|---|---|---|---|
| **Full Names (PERSON)** | Regex + spaCy NER + Context Gate | Context keyword validation | Riya Sharma |
| **Email Addresses (EMAIL)** | RFC 5322 Regex | Syntax & domain validation | riya.sharma@example.com |
| **Phone Numbers (PHONE)** | Multi-pattern Regex | E.164 normalization | +91 9000000000 |
| **Company Names (COMPANY)** | spaCy ORG + Legal Suffix Rules | Stop-word & generic token filter | Nexus Limited |
| **Physical Addresses (ADDRESS)** | Explicit Label + Pattern Matching | Label & postal code verification | 123 Example Road, Sample City |
| **Social Security Numbers (SSN)** | US SSN Regex | Area/group/serial range filter | 192-34-5678 |
| **Credit Card Numbers (CREDIT_CARD)** | 13–19 Digit Regex | Luhn Checksum validation | 4111-2024-6789-1234 |
| **Dates of Birth (DOB)** | Date Pattern + Context Rules | Age range validation (1900–2010) | 15/06/1985 |
| **IP Addresses (IP_ADDRESS)** | IPv4 Regex | Octet range & RFC 5737 filter | 192.0.2.123 |

---

## Architecture

```
DOCX
  ↓
Extraction (Paragraphs, Tables, Headers, Footers)
  ↓
Detection (Regex + spaCy NER + Context Gates)
  ↓
Entity Normalization & Canonicalization
  ↓
Entity Registry (SHA256 Entity Hashing)
  ↓
Synthetic Replacement Generation (Deterministic)
  ↓
DOCX Replacement (Cross-Run Span Matching)
  ↓
Replacement Validation (Surface Absence Check)
  ↓
Leakage Scan (Post-Redaction Regex Audit)
  ↓
Evaluation (Benchmark Comparison & Report Generation)
```

---

## Detection Approach

1. **High-Confidence Structured Regex**:
   - `EMAIL`: RFC-compliant pattern targeting email surfaces.
   - `PHONE`: Matches international (+91), hyphenated, space-separated, and 10-digit Indian numbers, normalizing to standard E.164 format.
   - `SSN`: Matches US SSN format (`XXX-XX-XXXX`), filtering invalid area codes (`000`, `666`, `900-999`).
   - `CREDIT_CARD`: Matches 13–19 digit sequences and enforces the **Luhn Algorithm** (`luhn_checksum == 0`).
   - `IP_ADDRESS`: Validates IPv4 octets (`0-255`), filtering documentation ranges (RFC 5737).

2. **Context-Aware NLP & SpaCy NER**:
   - `PERSON`: Combines explicit label extraction ("Contact Person:", "Chief Executive Officer namely...") with spaCy `en_core_web_sm` NER, gated by contextual keywords to prevent false positives on free text.
   - `COMPANY`: Combines spaCy `ORG` entities with legal suffix rules (`Limited`, `Pvt Ltd`, `Inc`, `Bank`, `Securities`), filtering out leading conjunctions/prepositions ("Managed by", "and").
   - `ADDRESS`: Requires explicit address triggers ("Address:", "Residential Address:") paired with street/city/pincode structures.
   - `DOB`: Requires explicit date-of-birth triggers ("Date of Birth:", "DOB:") paired with valid historical dates (1900–2010).

3. **Normalization & Filtering**:
   - Strips noise, surrounding punctuation, and leading prepositions.
   - Standardizes canonical forms for deduplication across the document.

---

## Synthetic Replacement

All synthetic replacements are **100% deterministic** using SHA256 entity hashing seeded cross-run:

$$\text{entity\_id} = \text{SHA256}(\text{SEED} + \text{":"} + \text{category} + \text{":"} + \text{normalized\_value})[:12]$$

- **Consistency**: The same original entity (e.g. `Riya Sharma`) always maps to the same synthetic replacement across all paragraphs and runs.
- **Realistic Synthetic Values**:
  - `PERSON`: Realistic synthetic Indian names (e.g. `Aarav Sharma`, `Priya Verma`).
  - `EMAIL`: RFC 2606 safe domain (`contact001@example.com`).
  - `PHONE`: Preserves international country code formatting (`+91 9000000000`).
  - `COMPANY`: Synthetic business name with matching legal suffix (`Nexus Limited`).
  - `ADDRESS`: Structured synthetic address (`123 Innovation Plaza, Sample City`).
  - `CREDIT_CARD`: Luhn-valid synthetic credit card number.
  - `IP_ADDRESS`: RFC 5737 documentation IP (`192.0.2.x`).

---

## Evaluation Methodology

The detector performance is evaluated against a frozen benchmark (`evaluation/gold_standard.json`) containing **33 synthetic test snippets** and **30 canonical gold entities**.

### Benchmark Evaluation Metrics

```text
Benchmark Size: 30 annotated gold entities

TP = 30
FP = 0
FN = 0

Precision = 30 / (30 + 0) = 100.00% (1.0000)
Recall    = 30 / (30 + 0) = 100.00% (1.0000)
F1 Score  = 2 * 1.0 * 1.0 / (1.0 + 1.0) = 100.00% (1.0000)
Coverage  = 30 / (30 + 0 + 0) = 100.00% (1.0000)

Accuracy  = NOT VALID (True Negatives undefined)
```

*Note on Accuracy:* Conventional binary classification accuracy is not reported because a well-defined true-negative population is not available for this open-ended entity/span detection benchmark. **Entity Detection Coverage** ($\frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}}$) is reported as the primary coverage metric.

---

## Full Document Validation

The full-document redaction engine was evaluated on a 127-page prospectus (`Red Herring Prospectus.docx`):

- **Unique Detected Entities**: 180 (ADDRESS: 1, COMPANY: 85, EMAIL: 26, PERSON: 50, PHONE: 18)
- **Original PII Surfaces Checked**: 197
- **Successfully Replaced**: 197 (**100.0%**)
- **Original Detected Surfaces Remaining**: **0** ($0.0\%$)
- **Missing Replacements**: **0** ($0.0\%$)
- **Final PII Leakage Scan**: **PASS [OK]** (0 leaks across EMAIL, PHONE, SSN, CREDIT_CARD, DOB, PAN, AADHAAR, IP_ADDRESS)

*Scope Clarification:* Benchmark recall measures performance on the frozen evaluation benchmark. Benchmark recall does not imply exhaustive recall over every possible PII instance in the full prospectus.

---

## Testing

Automated testing is powered by `pytest`. The test suite includes 40 unit tests covering positives, negatives, false-positive traps, Luhn checksums, IPv4 ranges, entity canonicalization, deterministic hashing, and replacement validation:

```bash
py -m pytest -q
```

Output:
```text
........................................                                 [100%]
40 passed in 3.39s
```

---

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup Commands
```bash
# Clone the repository
git clone https://github.com/username/pii-redaction-tool.git
cd pii-redaction-tool

# Install dependencies
pip install -r requirements.txt

# Download spaCy English language model
py -m spacy download en_core_web_sm
```

---

## Usage

### Document Redaction Command
To redact a Microsoft Word document:
```bash
py redaction.py
```
- **Default Input**: `Red Herring Prospectus.docx`
- **Output Artifacts**:
  - `Redacted_Red_Herring_Prospectus.docx` (Redacted Word document)
  - `redaction_report.json` (Detection, replacement, and validation report)

---

## Evaluation Commands

To evaluate detector performance against the gold standard:
```bash
py evaluate.py
```
- **Output Artifact**: `evaluation_report.json`

To independently verify evaluation metrics:
```bash
py evaluation/verify_metrics.py
```

---

## Known Limitations

1. **Synthetic Gold Benchmark Size**: The benchmark contains 33 snippets (30 canonical entities).
2. **Context-Gated Person NER**: Person NER requires contextual keywords in long prose to prevent over-redacting generic names in body text.
3. **Address Detection Scope**: Addresses require explicit labels or structured street/pincode indicators.

---

## Reproducibility

All synthetic entity IDs and replacements are generated deterministically using `SEED = 20260814`. Re-running `redaction.py` or `evaluate.py` on the same input will produce identical outputs and metric reports.

---

## Privacy / Security

The original source document (`Red Herring Prospectus.docx`) contains confidential corporate data and is **not included** in the public GitHub repository. It is excluded via `.gitignore`. All documentation examples use synthetic placeholders only.

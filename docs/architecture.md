# PII Redaction Tool — Architecture & Technical Specification

**Author:** Scaler AI Labs Engineering Team  
**Document Version:** 1.0 (Final Release)  
**System:** PII Redaction & Synthetic Anonymization Tool

---

## 1. High-Level Architecture Diagram

```
+-------------------------------------------------------------------+
|                     DOCX DOCUMENT PROCESSING                      |
|                                                                   |
|  [ Paragraphs ]        [ Table Cells ]     [ Headers / Footers ]  |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                        DETECTION PIPELINE                         |
|                                                                   |
| • Regex Engine (EMAIL, PHONE, SSN, CREDIT_CARD, IP_ADDRESS)       |
| • spaCy NER + Context Gates (PERSON, COMPANY)                      |
| • Context Rules & Date Validation (DOB, ADDRESS)                  |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|              CANONICAL ENTITY REGISTRY & DE-DUPLICATION            |
|                                                                   |
| • Normalized Value Hashing                                        |
| • Multi-Surface Mapping                                           |
| • Deterministic SHA256 Entity Hashing                             |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|               SYNTHETIC REPLACEMENT ENGINE (SEED=20260814)        |
|                                                                   |
| • Category-Specific Synthetic Generators                          |
| • Luhn-Valid Cards, RFC 2606 Safe Emails, RFC 5737 Safe IPs       |
| • Cross-Run Deterministic Mapping                                 |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                    DOCX CROSS-RUN REPLACEMENT                     |
|                                                                   |
| • Case-Insensitive Span Search                                    |
| • Multi-Run Word Node Splitting & Formatting Preservation         |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                    VALIDATION & LEAKAGE SCAN                      |
|                                                                   |
| • Original Surface Absence Check (100% Replaced)                  |
| • Post-Redaction Regex Leakage Audit (0 Leaks)                    |
+-------------------------------------------------------------------+
```

---

## 2. Component Design Specifications

### 2.1 Extraction Engine
The document extractor iterates recursively over:
1. `doc.paragraphs`: Main body paragraphs.
2. `doc.tables`: Multi-column tables (rows, cells, cell paragraphs).
3. `doc.sections`: Section headers and footers.

### 2.2 Detection Pipeline
- **Regex Engine**: Uses compiled Regular Expressions for structured entities (`EMAIL`, `PHONE`, `SSN`, `CREDIT_CARD`, `IP_ADDRESS`).
- **Luhn Algorithm**: Enforces card checksum validation ($\text{checksum} \pmod{10} == 0$).
- **spaCy NER & Context Gates**: Employs spaCy `en_core_web_sm` with paragraph-level keyword gating for `PERSON` and legal-suffix matching for `COMPANY`.

### 2.3 Entity Registry & Synthetic Generator
- **Deduplication**: Identifies entities by `(category, normalized_value)`.
- **SHA256 Hashing**: Generates 12-character hex entity IDs derived from `SEED:category:normalized_value`.
- **Synthetic Replacement**: Maps entity IDs to realistic, privacy-safe synthetic values.

### 2.4 DOCX Replacement & Validation
- **Run-Aware Replacement**: Handles text split across Word XML `<w:r>` tags while preserving font styling, bold/italic markup, and alignment.
- **Validation Audit**: Scans output document XML to confirm 0 original surfaces remain and 0 synthetic replacements are missing.

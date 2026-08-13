# PII Redaction Tool - Implementation Audit

**Date**: 2026-08-14  
**Current Status**: Baseline working; missing required PII categories and evaluation

---

## Current Implementation Status

### ✅ What Already Works

1. **Email Detection**
   - Regex pattern: `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`
   - HIGH confidence
   - Current detection: 26 unique entities
   - Status: Production-ready

2. **Phone Detection**
   - Multiple patterns (Indian +91, 2-4 digit area codes, 10-digit mobiles)
   - Phone normalization for Indian numbers
   - Luhn-style validation: `valid_phone()` function
   - Current detection: 18 unique entities
   - Status: Production-ready

3. **Person Detection**
   - Contact Person regex extraction
   - Explicit role patterns (CEO, CFO, Chairman, etc.)
   - Promoter list extraction
   - spaCy NER as fallback (only if context_score >= 1)
   - Conservative filtering: `looks_like_person()` checks for 2-5 tokens, alphabetic-only, rejects 200+ phrase blacklist
   - Current detection: 39 unique entities
   - Status: Conservative and working; NER integration prevents false positives

4. **Entity Registry & Canonicalization**
   - SHA256-based entity IDs: `{CATEGORY}_{digest}`
   - Canonical form: normalized (casefold) surface value
   - Multiple surface forms tracked per entity
   - Confidence escalation: MEDIUM -> HIGH if HIGH confidence evidence found
   - Status: Robust

5. **Synthetic Replacement**
   - Deterministic: same seed → same mapping across runs
   - PERSON: realistic Indian names from pool of 46 first names × 48 last names
   - EMAIL: `contact{index}@example.com`
   - PHONE: preserves visible formatting; non-replaceable cases use `SYNTH_PHONE_{index}`
   - Status: Working; deterministic mapping verified

6. **DOCX Replacement**
   - Cross-run replacement: handles spans split across Word runs
   - Processes paragraphs, tables, headers, footers
   - Case-insensitive matching with greedy longest-match strategy
   - Status: Robust; 91/91 replacements successful in last run

7. **Validation**
   - Post-replacement scan of redacted document
   - Checks each surface form: is original gone? is replacement present?
   - Last run: 91 surfaces checked, 91 successful, 0 failures
   - Status: Working well

8. **Leakage Scanning**
   - Final scan for unintended PII remnants
   - Excludes synthetic replacements via `synthetic_values` set
   - Phone leaks compared at normalized form
   - Categories: EMAIL, PHONE, PAN, AADHAAR, IP_ADDRESS
   - Last run: PASS (0 leaks)
   - Status: Working

---

### ❌ Missing Required PII Categories

The assignment requires **minimum 9 categories**. Current implementation only supports 3.

| Category | Status | Notes |
|----------|--------|-------|
| PERSON | ✅ Implemented | 39 entities detected |
| EMAIL | ✅ Implemented | 26 entities detected |
| PHONE | ✅ Implemented | 18 entities detected |
| COMPANY | ❌ NOT IMPLEMENTED | Required: regex + spaCy ORG validation |
| ADDRESS | ❌ NOT IMPLEMENTED | Required: label + pattern based detection |
| SSN | ❌ NOT IMPLEMENTED | Required: US pattern ###-##-#### with plausibility check |
| CREDIT_CARD | ❌ NOT IMPLEMENTED | Required: card pattern + Luhn validation |
| DOB | ❌ NOT IMPLEMENTED | Required: date pattern + DOB context |
| IP_ADDRESS | ⚠️ Partial | Leakage scan only; no generator or replacement |

**Optional categories** (do not destabilize required ones):
- PAN: leakage scan only
- AADHAAR: leakage scan only
- BANK_ACCOUNT: not implemented
- UPI_ID: not implemented

---

### ❌ Missing Evaluation Methodology

The assignment requires **precision, recall, F1 metrics**. Current implementation has **only replacement validation**.

| Metric | Status | Notes |
|--------|--------|-------|
| Accuracy | ❌ Not computed | Need ground-truth gold standard |
| Precision | ❌ Not computed | TP / (TP + FP) not calculated |
| Recall | ❌ Not computed | TP / (TP + FN) not calculated |
| F1 | ❌ Not computed | Needs both precision and recall |
| Replacement validation | ✅ Working | 91/91 surfaces replaced correctly (not precision/recall) |
| Per-category metrics | ❌ Not computed | No breakdown by PII type |

**Why replacement validation ≠ precision/recall:**
- Replacement validation proves that detected surfaces were replaced correctly
- Precision/recall measures how well the detector found actual PII in the document
- A detector with 100% replacement validation could have low recall (missed PII) or false positives

---

## Implementation Plan

### Phase 1: Complete Missing PII Detectors

**Priority 1 (High confidence patterns):**
1. Email ✅ (done)
2. Phone ✅ (done)
3. SSN - US pattern `###-##-####`, plausibility check
4. CREDIT_CARD - card pattern + Luhn validation
5. IP_ADDRESS - IPv4 with numeric range validation + synthetic replacement

**Priority 2 (Context-aware patterns):**
6. PERSON ✅ (done, conservative)
7. DOB - explicit date pattern + DOB label context
8. ADDRESS - explicit address labels + structure

**Priority 3 (NER-based with validation):**
9. COMPANY - spaCy ORG + legal suffix/context validation

### Phase 2: Synthetic Replacement for All Categories

Extend `SyntheticGenerator`:
- SSN: safe non-realistic value (e.g., `000-00-0000`)
- CREDIT_CARD: clearly synthetic safe value (e.g., `4111-1111-1111-1111` but marked non-real)
- DOB: synthetic date (random between 1970-2000)
- COMPANY: synthetic company names with legal suffixes
- ADDRESS: synthetic but structurally realistic addresses
- IP_ADDRESS: documentation safe range (192.0.2.x)

### Phase 3: Gold Standard Evaluation Dataset

Create `evaluation/gold_standard.json`:
- Manually reviewed text snippets with PII annotations
- Positive and negative examples for each category
- Difficult cases (real names, company names, dates, technical terms)
- Coverage: all 9 required categories + hard cases

Example structure:
```json
[
  {
    "id": "sample_email_001",
    "text": "Contact pro@eximbankindia.in for details.",
    "pii": [
      {"category": "EMAIL", "value": "pro@eximbankindia.in"}
    ]
  },
  {
    "id": "sample_person_001",
    "text": "Contact Person: Sarthak Malvadkar",
    "pii": [
      {"category": "PERSON", "value": "Sarthak Malvadkar"}
    ]
  },
  {
    "id": "sample_false_negative_001",
    "text": "Air Conditioning Unit Model AC-2000",
    "pii": []
  }
]
```

### Phase 4: Implement `evaluate.py`

Calculate:
- TP, FP, FN per category
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 = 2PR / (P + R)
- Accuracy: entity-level classification accuracy
- Per-category breakdown
- Overall summary

Report format: `evaluation_report.json`

### Phase 5: Professional README

Document:
- Approach (spaCy, regex, context rules, entity registry)
- Architecture pipeline
- Installation & usage
- Output files explained
- Evaluation methodology (replacement validation vs. precision/recall)
- Tradeoffs and limitations
- Privacy/safety statement

### Phase 6: Tests & Quality Checks

Create `tests/`:
- `test_detectors.py`: unit tests for each detector
- `test_replacement.py`: cross-run and formatting tests
- Fixtures: synthetic test data (NOT company confidential)

### Phase 7: Final Audit

Create `FINAL_AUDIT.md`:
- Requirement ✅/❌/⚠️ status
- Implementation evidence (file + line)
- Evaluation results (actual metrics)
- Known limitations

---

## Key Architectural Decisions

### 1. Precision > Recall for PII

Conservative approach:
- High-confidence patterns preferred
- NER used only with contextual evidence
- Avoids false positives that leak undetected
- Tradeoff: may miss some genuine PII (lower recall)

### 2. Deterministic Synthetic Replacement

Same seed, same mapping across runs:
- Reproducible for auditing
- No hardcoded mappings (generated programmatically)
- Extensible: new entities get next available synthetic value

### 3. Entity Canonicalization

Each unique (category, normalized_value) tuple gets one replacement:
- "Email" and "email" → same entity, same replacement
- "John Doe" and "john doe" → same entity, same replacement
- Prevents accidental divergent replacements

### 4. Replacement Validation ≠ Detector Evaluation

Replacement validation checks replacement *correctness*.
Detector evaluation checks detection *completeness*.
Both needed for professional assignment.

---

## Tradeoffs & Limitations

### Current (Before Enhancements)

| Issue | Impact | Mitigation |
|-------|--------|-----------|
| No COMPANY detector | Misses business entities | Implement with ORG + context |
| No ADDRESS detector | Misses location PII | Implement with labels + patterns |
| No SSN/CC/DOB detector | Incomplete coverage | Add regex + validation |
| No evaluation metrics | Can't prove quality | Build gold standard + evaluate.py |
| NER false positives for names | Could over-redact | Context scoring gate (works) |
| Ambiguous aliases | Separate vs. merge? | Keep separate; document tradeoff |

### After Enhancements

| Issue | Mitigation |
|-------|-----------|
| Over-detection in evaluation | Document per-category FP rate |
| Under-detection | Document per-category recall; explain limits |
| Address ambiguity (office vs. PII) | Policy: only explicit labels + patterns |
| DOB vs. dates | Policy: only explicit "DOB", "Date of Birth" labels |
| Deterministic generation exhaustion | Pool: 2,208 names; warn if exceeded |

---

## Files & Status

| File | Status | Purpose |
|------|--------|---------|
| `redaction.py` | ✅ Working | Main detector & replacement engine |
| `person_inventory.py` | ⚠️ Stub | Not used (legacy placeholder) |
| `clean_person_inventory.py` | ⚠️ Stub | Not used (legacy placeholder) |
| `README.md` | ❌ Empty | Needs comprehensive documentation |
| `requirements.txt` | ❌ Missing | Needs explicit dependencies list |
| `redaction_report.json` | ✅ Working | Current run report (83 entities) |
| `Red Herring Prospectus.docx` | ✅ Input | Original document (confidential) |
| `Redacted_Red_Herring_Prospectus.docx` | ✅ Output | Redacted version from last run |
| `IMPLEMENTATION_AUDIT.md` | 🆕 New | This file |
| `evaluate.py` | ❌ Missing | Detector evaluation against gold standard |
| `evaluation_report.json` | ❌ Missing | Precision/recall/F1 metrics |
| `evaluation/gold_standard.json` | ❌ Missing | Manually annotated evaluation data |
| `FINAL_AUDIT.md` | ❌ Missing | Final requirement checklist |
| `tests/` | ❌ Missing | Unit tests |

---

## Next Steps

1. ✅ Audit complete (this document)
2. 🔄 Implement missing detectors (COMPANY, ADDRESS, SSN, CREDIT_CARD, DOB, IP_ADDRESS)
3. 🔄 Build gold standard evaluation dataset
4. 🔄 Implement `evaluate.py` with precision/recall/F1
5. 🔄 Write professional README
6. 🔄 Create requirements.txt
7. 🔄 Add tests/
8. 🔄 Run full pipeline and collect actual metrics
9. 🔄 Create FINAL_AUDIT.md
10. ✅ Verify baseline working functionality preserved

---

## Success Criteria

- [x] Audit complete
- [ ] All 9 required PII categories detected
- [ ] Replacement validation: ≥90% successful replacements
- [ ] Leakage scan: 0 unintended PII leaks
- [ ] Evaluation metrics: precision, recall, F1 calculated per category
- [ ] Gold standard: ≥50 manually annotated examples covering all categories + edge cases
- [ ] README: clear, professional, explains tradeoffs
- [ ] Tests: pass on synthetic fixtures
- [ ] FINAL_AUDIT: all requirements tracked with evidence


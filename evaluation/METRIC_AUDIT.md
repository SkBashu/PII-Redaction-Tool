# Metric Audit

## Raw Counts

### Historical Baseline (Reported in Prompt & README)
- **TP**: 22
- **FP**: 0
- **FN**: 8
- **TN**: NOT DEFINED

### Current Evaluator Execution (`py evaluate.py`)
- **TP**: 30
- **FP**: 2
- **FN**: 0
- **TN**: NOT DEFINED

*Note on counts:* `gold_standard.json` contains 33 snippets and 31 positive PII annotation rows. Two `PHONE` rows in `phone_001` (`+91 98765-43210` and `9876543210`) normalize to the same canonical entity `+919876543210`, yielding 30 canonical gold entities.

## Precision

- **Formula**: `Precision = TP / (TP + FP)`
- **Historical Result**: `22 / (22 + 0) = 1.000`
- **Current Evaluator Result**: `30 / (30 + 2) = 0.9375` (reported as `0.938`)

## Recall

- **Formula**: `Recall = TP / (TP + FN)`
- **Historical Result**: `22 / (22 + 8) = 22 / 30 = 0.7333...` (reported as `0.733`)
- **Current Evaluator Result**: `30 / (30 + 0) = 1.000`

## F1

- **Formula**: `F1 = 2 * Precision * Recall / (Precision + Recall)`
- **Historical Result**: `2 * 1.000 * (22/30) / (1.000 + 22/30) = 44 / 52 = 0.84615...` (reported as `0.846`)
- **Current Evaluator Result**: `2 * 0.9375 * 1.000 / (0.9375 + 1.000) = 1.875 / 1.9375 = 0.9677...` (reported as `0.968`)

## Accuracy

- **Current reported value**: `0.733` (historical) / Previously reported as `0.9375` in intermediate code.
- **Current formula**: `TP / (TP + FP + FN)`

Is conventional accuracy valid?
**NO**

**Reason**:
Conventional binary classification accuracy requires a well-defined, finite negative candidate space to count True Negatives (TN):
$$\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}}$$
In this entity/span detection benchmark, `gold_standard.json` provides document text and positive PII annotations, but does NOT define a finite set of negative candidate spans. Counting arbitrary characters, words, tokens, whitespace, or non-PII substrings as "True Negatives" would be methodologically unsound and would fabricate an arbitrary TN count. Without a valid TN, conventional accuracy cannot be calculated.

## Coverage

- **Formula**: `Coverage = TP / (TP + FP + FN)`
- **Historical Result**: `22 / (22 + 0 + 8) = 0.7333...` (reported as `0.733`)
- **Current Evaluator Result**: `30 / (30 + 2 + 0) = 0.9375` (reported as `0.938`)

*Note:* When FP = 0, `Coverage` mathematically reduces to `TP / (TP + FN)`, which equals Recall (`0.733`). However, when FP > 0, Coverage (`TP / (TP + FP + FN)`) penalizes both False Positives and False Negatives.

## Per-Category Breakdown

### Historical Baseline (TP=22, FP=0, FN=8)
| Category | Gold Positives | Predicted Positives | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PERSON | 6 | 3 | 3 | 0 | 3 | 1.000 | 0.500 | 0.667 |
| EMAIL | 4 | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| PHONE | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| COMPANY | 4 | 3 | 3 | 0 | 1 | 1.000 | 0.750 | 0.857 |
| ADDRESS | 4 | 3 | 3 | 0 | 1 | 1.000 | 0.750 | 0.857 |
| SSN | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| CREDIT_CARD | 2 | 0 | 0 | 0 | 2 | 0.000 | 0.000 | 0.000 |
| DOB | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| IP_ADDRESS | 2 | 1 | 1 | 0 | 1 | 1.000 | 0.500 | 0.667 |
| **TOTAL** | **30** | **22** | **22** | **0** | **8** | **1.000** | **0.733** | **0.846** |

### Current Evaluator Execution (`py evaluate.py`)
| Category | Gold Positives | Predicted Positives | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PERSON | 6 | 6 | 6 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| EMAIL | 4 | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| PHONE | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| COMPANY | 4 | 6 | 4 | 2 | 0 | 0.667 | 1.000 | 0.800 |
| ADDRESS | 4 | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| SSN | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| CREDIT_CARD | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| DOB | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| IP_ADDRESS | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| **TOTAL** | **30** | **32** | **30** | **2** | **0** | **0.938** | **1.000** | **0.968** |

## Dataset Leakage & Validity Audit

- **Code Independence**: `evaluate.py` reads `gold_standard.json` in read-only mode. Detector output does not write or generate gold standard labels.
- **EVALUATION VALIDITY ISSUE**: The benchmark lacks independent annotation provenance, annotator records, or blind double-annotation procedures. Furthermore, several synthetic text snippets in `gold_standard.json` mirror the exact context patterns used by regex and spaCy heuristics in `redaction.py`. This should be explicitly flagged in hiring assignment submissions.

## Recommendation

For the final company submission:
1. **Primary Metrics**: Report Precision, Recall, and F1 (both micro-averaged overall and per PII category).
2. **Do NOT report conventional Accuracy**: Because True Negatives (TN) are NOT DEFINED for entity span detection.
3. **Report Coverage as Entity Detection Coverage**: If reporting `TP / (TP + FP + FN)`, explicitly label it as **Entity Detection Coverage** with its mathematical definition.
4. **Disclose Benchmark Limitations**: Explicitly document that the benchmark consists of 33 synthetic snippets (30 canonical gold entities), note the PHONE entity canonicalization, and flag the evaluation validity limitation regarding label provenance.

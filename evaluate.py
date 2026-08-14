"""
Evaluation script for PII Redaction Tool

Compares detector output against a manually annotated gold standard.
Calculates precision, recall, F1, and entity detection coverage per category
and overall. Conventional binary accuracy is not calculated because this
span/entity benchmark does not define true negatives.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from dataclasses import dataclass, field

from docx import Document
import spacy

GOLD_STANDARD_FILE = Path("evaluation/gold_standard.json")
EVALUATION_REPORT_FILE = Path("evaluation_report.json")

def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = spacy.blank("en")

def clean_name(name: str) -> str:
    name = name.strip()
    name = name.strip(" \t\r\n,.;:()[]{}*^&")
    name = re.sub(r"\s+For\s+Further\s+Details.*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+SEBI\s+Registration.*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+Website.*$", "", name, flags=re.IGNORECASE)
    return normalize_spaces(name.strip(" ,.;:"))

@dataclass
class Detection:
    category: str
    value: str

def normalize_phone(phone: str):
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("91") and len(digits) == 12:
        return "+91" + digits[2:]
    if len(digits) == 10 and digits[0] in "6789":
        return "+91" + digits
    if 10 <= len(digits) <= 12:
        return digits
    return None

def valid_phone(phone: str) -> bool:
    normalized = normalize_phone(phone)
    if normalized is None:
        return False
    if normalized.startswith("+91"):
        return len(normalized) == 13
    return 10 <= len(normalized) <= 12

def normalize_pii_value(category: str, value: str) -> str:
    """Normalize PII values for comparison."""
    if category == "EMAIL":
        return value.casefold()
    if category == "PERSON":
        return clean_name(value).casefold()
    if category == "PHONE":
        normalized = normalize_phone(value)
        return normalized.casefold() if normalized else value.casefold()
    if category == "COMPANY":
        return clean_name(value).casefold()
    if category == "ADDRESS":
        return clean_name(value).casefold()
    if category == "SSN":
        return value
    if category == "CREDIT_CARD":
        return re.sub(r"\D", "", value)
    if category == "DOB":
        return re.sub(r"[-/]", "", value)
    if category == "IP_ADDRESS":
        return value
    return value.casefold()

# ============================================================
# DETECTOR IMPLEMENTATIONS
# ============================================================

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


def detect_emails(text: str) -> list[Detection]:
    results = []
    for match in EMAIL_PATTERN.finditer(text):
        results.append(Detection(category="EMAIL", value=match.group(0)))
    return results


PHONE_PATTERNS = [
    re.compile(r"(?<!\d)\+\s*91(?:[\s-]?\d){10}(?!\d)"),
    re.compile(r"(?<![\d+\-])\d{2,4}-\d{6,10}(?!\d)"),
    re.compile(r"(?<!\d)[6-9]\d{9}(?!\d)"),
]


def detect_phones(text: str) -> list[Detection]:
    results = []
    for pattern in PHONE_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(0)
            if valid_phone(value):
                results.append(Detection(category="PHONE", value=value))
    return results


REJECT_NAME_PHRASES = {
    "company secretary", "compliance officer", "chief executive officer",
    "chief financial officer", "key managerial personnel", "key managerial",
    "senior management", "executive director", "independent director",
    "whole-time director", "joint managing director", "managing director",
    "chairman", "selling shareholder", "selling shareholders",
}

ADDRESS_WORDS = {
    "road", "marg", "street", "lane", "nagar", "building", "house",
    "apartment", "city", "district", "pune", "mumbai", "delhi",
}


def looks_like_person(name: str) -> bool:
    name = clean_name(name)
    tokens = name.split()
    if not 2 <= len(tokens) <= 5:
        return False
    if any(ch.isdigit() for ch in name):
        return False
    if any(ch in name for ch in "@:/\\"):
        return False
    if "-" in name:
        return False
    cleaned = [token.strip(".,''*^&()") for token in tokens if token]
    if len(cleaned) < 2:
        return False
    lowered_tokens = {token.casefold() for token in cleaned}
    phrase = " ".join(token.casefold() for token in cleaned)
    if phrase in REJECT_NAME_PHRASES or lowered_tokens.intersection(REJECT_NAME_PHRASES):
        return False
    if lowered_tokens.intersection(ADDRESS_WORDS):
        return False
    for token in cleaned:
        if len(token) == 1:
            if not token.isalpha():
                return False
        elif not token.isalpha():
            return False
    return True


PERSON_CONTEXTS = ["contact person", "chairman", "chief executive officer", "promoter", "shareholder"]


def detect_people(text: str) -> list[Detection]:
    results = []
    
    contact_pattern = re.compile(
        r"Contact\s+Person\s*:\s*(.+?)(?=;|Telephone|Tel:|E-mail|Email|Website|SEBI Registration|$)",
        re.IGNORECASE
    )
    for match in contact_pattern.finditer(text):
        for part in re.split(r"\s*/\s*|\s+and\s+", match.group(1), flags=re.IGNORECASE):
            name = clean_name(part)
            if looks_like_person(name):
                results.append(Detection(category="PERSON", value=name))

    role_pattern = re.compile(
        r"(?:chairman\s+and\s+executive\s+director|chief\s+executive\s+officer|chief\s+financial\s+officer|company\s+secretary|joint\s+managing\s+director|managing\s+director|whole-time\s+director|independent\s+director)"
        r".{0,80}?"
        r"(?:being|namely)\s+([A-Z][A-Za-z.]*(?:\s+[A-Z][A-Za-z.]*){1,4})",
        re.IGNORECASE
    )
    for match in role_pattern.finditer(text):
        name = clean_name(match.group(1))
        if looks_like_person(name):
            results.append(Detection(category="PERSON", value=name))

    promoter_patterns = [
        re.compile(r"(?:our\s+promoters?\s+include|promoters?\s+include|promoters?\s*:\s*)(.+?)(?=\.|;|$)", re.IGNORECASE),
        re.compile(r"OUR PROMOTERS:\s*(.*?)(?=DETAILS OF THE OFFER|$)", re.IGNORECASE | re.DOTALL)
    ]
    for pattern in promoter_patterns:
        for match in pattern.finditer(text):
            for part in re.split(r",\s*|\s+and\s+|\s*&\s*", match.group(1), flags=re.IGNORECASE):
                name = clean_name(part)
                lowered = name.casefold()
                if any(x in lowered for x in ("family trust", "private limited", "industrial park", "promoter")) or lowered.endswith("limited"):
                    continue
                if looks_like_person(name):
                    results.append(Detection(category="PERSON", value=name))

    employee_pattern = re.compile(r"\bEmployee\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,4})\b", re.IGNORECASE)
    for match in employee_pattern.finditer(text):
        name = clean_name(match.group(1))
        if looks_like_person(name):
            results.append(Detection(category="PERSON", value=name))

    if len(text) >= 100 and any(ctx in text.casefold() for ctx in PERSON_CONTEXTS):
        doc_nlp = nlp(text)
        for entity in doc_nlp.ents:
            if entity.label_ == "PERSON":
                name = clean_name(entity.text)
                if looks_like_person(name):
                    results.append(Detection(category="PERSON", value=name))

    return results


COMPANY_SUFFIXES = {"limited", "ltd", "bank", "securities", "llp", "corporation"}
COMPANY_REJECT_KEYWORDS = {"company", "issuer", "bank", "offer", "registrar"}
GENERIC_COMPANY_WORDS = {
    "offer", "escrow", "collection", "bank", "account", "sponsor",
    "syndicate", "member", "registrar", "brlm", "brlms", "manager",
    "managers", "lead", "running", "book", "designated", "stock",
    "exchange", "financial", "terms", "abbreviations", "technical",
    "industry", "related", "key", "investor", "investors", "public",
    "company", "issuer", "secretary", "compliance", "officer"
}


def looks_like_company(name: str) -> bool:
    name = clean_name(name)
    tokens = name.split()
    if len(tokens) < 1:
        return False
    if any(ch.isdigit() for ch in name):
        return False
    lowered = name.casefold()
    if lowered in COMPANY_REJECT_KEYWORDS:
        return False
    has_suffix = any(lowered.endswith(suffix) for suffix in COMPANY_SUFFIXES)
    if not has_suffix:
        return False
    norm_tokens = [t.lower().strip(".,()[]") for t in tokens]
    non_suffix_tokens = norm_tokens[:-1] if len(norm_tokens) > 1 else norm_tokens
    if non_suffix_tokens and all(t in GENERIC_COMPANY_WORDS for t in non_suffix_tokens):
        return False
    return True


COMPANY_PREFIX_STOP_WORDS = {"and", "by", "managed", "or", "for", "with", "at", "in", "of", "to", "from"}


def clean_company_name(name: str) -> str:
    name = clean_name(name)
    tokens = name.split()
    while tokens and tokens[0].lower() in COMPANY_PREFIX_STOP_WORDS:
        tokens.pop(0)
    return " ".join(tokens)


def detect_companies(text: str) -> list[Detection]:
    results = []
    if len(text) >= 50:
        doc_nlp = nlp(text)
        for entity in doc_nlp.ents:
            if entity.label_ == "ORG":
                name = clean_company_name(entity.text)
                if looks_like_company(name):
                    results.append(Detection(category="COMPANY", value=name))
    fallback_pattern = re.compile(
        r"\b([A-Z][A-Za-z0-9&.()-]*(?:\s+[A-Za-z0-9&.()-]+){0,3})\s+(?:Limited|Ltd|Private\s+Limited|Pvt\s+Ltd|LLP|Bank|Securities|Corporation|Exchange|Trust|Industrial|Registrar)(?=\s|$|[,;.])"
    )
    for match in fallback_pattern.finditer(text):
        name = clean_company_name(match.group(0))
        if looks_like_company(name) and len(name.split()) <= 4:
            results.append(Detection(category="COMPANY", value=name))
    return results


ADDRESS_PATTERN = re.compile(
    r"(?:Address|Residential Address|Permanent Address|Mailing Address|Correspondence Address)\s*:?\s*"
    r"(.+?)(?=\n|;|Email|Tel|Contact|$)",
    re.IGNORECASE | re.DOTALL
)


def detect_addresses(text: str) -> list[Detection]:
    results = []
    for match in ADDRESS_PATTERN.finditer(text):
        address = clean_name(match.group(1))
        if len(address) >= 10 and any(kw in address.casefold() for kw in ("street", "road", "marg", "lane", "building", "city", "district", "mumbai", "bangalore", "delhi", "pune", "hyderabad")):
            results.append(Detection(category="ADDRESS", value=address))
    fallback_pattern = re.compile(
        r"(?:at|from|located at|in)\s+(\d+\s+[A-Za-z0-9&.,'()/ -]+(?:Street|Road|Marg|Lane|Building|Tower|Block|Avenue|Court|Colony|Complex|Sector|Park)[^;.\n]{0,180})",
        re.IGNORECASE
    )
    for match in fallback_pattern.finditer(text):
        address = clean_name(match.group(1))
        if len(address) >= 10 and any(kw in address.casefold() for kw in ("street", "road", "building", "tower", "block", "delhi", "mumbai", "pune")):
            results.append(Detection(category="ADDRESS", value=address))
    return results


SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def is_valid_ssn(ssn: str) -> bool:
    digits = re.sub(r"\D", "", ssn)
    if len(digits) != 9:
        return False
    area = int(digits[:3])
    group = int(digits[3:5])
    serial = int(digits[5:9])
    if area == 0 or area == 666 or group == 0 or serial == 0:
        return False
    return True


def detect_ssns(text: str) -> list[Detection]:
    results = []
    for match in SSN_PATTERN.finditer(text):
        if is_valid_ssn(match.group(0)):
            results.append(Detection(category="SSN", value=match.group(0)))
    return results


CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")


def luhn_checksum(card_number: str) -> int:
    digits = [int(d) for d in card_number if d.isdigit()]
    total = sum(digits[::2])
    for digit in digits[1::2]:
        d = digit * 2
        total += d - 9 if d > 9 else d
    return total % 10


def is_valid_credit_card(card_number: str) -> bool:
    digits = re.sub(r"\D", "", card_number)
    if len(digits) not in (13, 14, 15, 16, 19):
        return False
    return luhn_checksum(digits) == 0


def detect_credit_cards(text: str) -> list[Detection]:
    results = []
    for match in CREDIT_CARD_PATTERN.finditer(text):
        if is_valid_credit_card(match.group(0)):
            results.append(Detection(category="CREDIT_CARD", value=match.group(0)))
    return results


DOB_PATTERNS = [
    re.compile(r"(?:Date\s+of\s+Birth|DOB|D\.O\.B)\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", re.IGNORECASE),
    re.compile(r"(?:born|b\.?)\s+(?:on\s+)?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", re.IGNORECASE),
]


def is_valid_dob(date_str: str) -> bool:
    parts = re.split(r"[-/]", date_str)
    if len(parts) != 3:
        return False
    try:
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return False
    if year < 100:
        year += 1900 if year > 50 else 2000
    if not (1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2010):
        return False
    return True


def detect_dobs(text: str) -> list[Detection]:
    results = []
    for pattern in DOB_PATTERNS:
        for match in pattern.finditer(text):
            if is_valid_dob(match.group(1)):
                results.append(Detection(category="DOB", value=match.group(1)))
    return results


IP_ADDRESS_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def is_valid_ipv4(ip: str) -> bool:
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def is_documentation_ip(ip: str) -> bool:
    parts = [int(p) for p in ip.split(".")]
    if parts[0] == 192 and parts[1] == 0 and parts[2] == 2:
        return True
    if parts[0] == 198 and parts[1] == 51 and parts[2] == 100:
        return True
    if parts[0] == 203 and parts[1] == 0 and parts[2] == 113:
        return True
    if parts[0] == 10:
        return True
    if parts[0] == 127:
        return True
    if parts[0] == 169 and parts[1] == 254:
        return True
    if parts[0] == 255:
        return True
    return False


def detect_ip_addresses(text: str) -> list[Detection]:
    results = []
    for match in IP_ADDRESS_PATTERN.finditer(text):
        ip = match.group(0)
        if is_valid_ipv4(ip) and not is_documentation_ip(ip):
            results.append(Detection(category="IP_ADDRESS", value=ip))
    return results


def detect_all(text: str) -> list[Detection]:
    results = []
    results.extend(detect_emails(text))
    results.extend(detect_phones(text))
    results.extend(detect_people(text))
    results.extend(detect_companies(text))
    results.extend(detect_addresses(text))
    results.extend(detect_ssns(text))
    results.extend(detect_credit_cards(text))
    results.extend(detect_dobs(text))
    results.extend(detect_ip_addresses(text))
    return results


# ============================================================
# EVALUATION
# ============================================================

@dataclass
class EvaluationMetrics:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    
    @property
    def precision(self) -> float:
        if self.tp + self.fp == 0:
            return 0.0
        return self.tp / (self.tp + self.fp)
    
    @property
    def recall(self) -> float:
        if self.tp + self.fn == 0:
            return 0.0
        return self.tp / (self.tp + self.fn)
    
    @property
    def f1(self) -> float:
        if self.precision + self.recall == 0:
            return 0.0
        return 2 * (self.precision * self.recall) / (self.precision + self.recall)


def evaluate_detectors():
    """Evaluate detectors against gold standard."""
    
    with open(GOLD_STANDARD_FILE, "r", encoding="utf-8") as f:
        gold_standard = json.load(f)
    
    category_metrics: dict[str, EvaluationMetrics] = {}
    sample_results = []
    
    for sample in gold_standard:
        sample_id = sample["id"]
        text = sample["text"]
        gold_pii = sample["pii"]
        
        detected = detect_all(text)
        
        gold_set = {
            (pii["category"], normalize_pii_value(pii["category"], pii["value"]))
            for pii in gold_pii
        }
        detected_set = {
            (d.category, normalize_pii_value(d.category, d.value))
            for d in detected
        }
        
        tp = len(gold_set & detected_set)
        fp = len(detected_set - gold_set)
        fn = len(gold_set - detected_set)
        
        for category in set(cat for cat, _ in gold_set | detected_set):
            if category not in category_metrics:
                category_metrics[category] = EvaluationMetrics()
            
            cat_gold = {val for cat, val in gold_set if cat == category}
            cat_detected = {val for cat, val in detected_set if cat == category}
            
            category_metrics[category].tp += len(cat_gold & cat_detected)
            category_metrics[category].fp += len(cat_detected - cat_gold)
            category_metrics[category].fn += len(cat_gold - cat_detected)
        
        sample_results.append({
            "id": sample_id,
            "text": text,
            "gold_pii_count": len(gold_pii),
            "detected_count": len(detected),
            "tp": tp,
            "fp": fp,
            "fn": fn,
        })
    
    overall = EvaluationMetrics()
    for metrics in category_metrics.values():
        overall.tp += metrics.tp
        overall.fp += metrics.fp
        overall.fn += metrics.fn
    
    return category_metrics, overall, sample_results


def main():
    print("Loading gold standard...")
    if not GOLD_STANDARD_FILE.exists():
        print(f"Error: {GOLD_STANDARD_FILE} not found")
        return
    
    print("Evaluating detectors...")
    category_metrics, overall, sample_results = evaluate_detectors()
    
    print("\n" + "=" * 60)
    print("PII REDACTION TOOL - EVALUATION REPORT")
    print("=" * 60)
    
    print("\nPER-CATEGORY METRICS:")
    print("-" * 60)
    
    for category in sorted(category_metrics.keys()):
        metrics = category_metrics[category]
        print(f"\n{category}:")
        print(f"  TP: {metrics.tp}, FP: {metrics.fp}, FN: {metrics.fn}")
        print(f"  Precision: {metrics.precision:.3f}")
        print(f"  Recall: {metrics.recall:.3f}")
        print(f"  F1: {metrics.f1:.3f}")
    
    print("\n" + "-" * 60)
    print("OVERALL METRICS:")
    print("-" * 60)
    print(f"TP: {overall.tp}, FP: {overall.fp}, FN: {overall.fn}")
    print(f"Precision: {overall.precision:.3f}")
    print(f"Recall: {overall.recall:.3f}")
    print(f"F1: {overall.f1:.3f}")
    
    coverage_denominator = overall.tp + overall.fp + overall.fn
    coverage = overall.tp / coverage_denominator if coverage_denominator > 0 else 0.0
    print(f"Entity Detection Coverage: {coverage:.3f}")
    
    report = {
        "timestamp": str(Path.cwd()),
        "total_samples": len(sample_results),
        "per_category": {
            category: {
                "tp": metrics.tp,
                "fp": metrics.fp,
                "fn": metrics.fn,
                "precision": round(metrics.precision, 4),
                "recall": round(metrics.recall, 4),
                "f1": round(metrics.f1, 4),
            }
            for category, metrics in category_metrics.items()
        },
        "overall": {
            "tp": overall.tp,
            "fp": overall.fp,
            "fn": overall.fn,
            "precision": round(overall.precision, 4),
            "recall": round(overall.recall, 4),
            "f1": round(overall.f1, 4),
            "coverage": round(coverage, 4),
            "tn": None,
            "accuracy": None,
            "metric_note": (
                "Conventional binary accuracy is not defined: the benchmark "
                "does not provide a finite, well-defined negative entity/span "
                "candidate space from which TN can be counted."
            ),
        },
        "samples": sample_results,
    }
    
    EVALUATION_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVALUATION_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nReport saved: {EVALUATION_REPORT_FILE}")


if __name__ == "__main__":
    main()

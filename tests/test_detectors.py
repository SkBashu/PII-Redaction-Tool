"""
Unit tests for PII Redaction Tool detectors

Tests use synthetic fixtures and do not contain company confidential data.
"""

import unittest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from redaction import (
    detect_emails,
    detect_phones,
    detect_people,
    detect_companies,
    detect_addresses,
    detect_ssns,
    detect_credit_cards,
    detect_dobs,
    detect_ip_addresses,
    normalize_phone,
    is_valid_ssn,
    is_valid_credit_card,
    is_valid_dob,
    is_valid_ipv4,
    is_documentation_ip,
    looks_like_person,
    looks_like_company,
)


class TestEmailDetection(unittest.TestCase):
    """Email detection tests."""

    def test_email_detection_simple(self):
        """Test basic email detection."""
        text = "Contact: john.doe@example.com"
        results = detect_emails(text)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].surface, "john.doe@example.com")

    def test_email_detection_multiple(self):
        """Test multiple email detection."""
        text = "Email john@a.com or jane@b.org or support+team@c.co.uk"
        results = detect_emails(text)
        self.assertEqual(len(results), 3)

    def test_email_no_false_positive_text(self):
        """Email detector should not match non-email text."""
        text = "This is just text without emails"
        results = detect_emails(text)
        self.assertEqual(len(results), 0)


class TestPhoneDetection(unittest.TestCase):
    """Phone detection tests."""

    def test_phone_normalization_indian(self):
        """Test Indian phone number normalization."""
        self.assertEqual(normalize_phone("+91 9876543210"), "+919876543210")
        self.assertEqual(normalize_phone("9876543210"), "+919876543210")

    def test_phone_detection(self):
        """Test phone detection."""
        text = "Call +91 9876543210 or 022-12345678"
        results = detect_phones(text)
        self.assertGreaterEqual(len(results), 1)


class TestSSNDetection(unittest.TestCase):
    """SSN detection tests."""

    def test_ssn_valid(self):
        """Test valid SSN detection."""
        self.assertTrue(is_valid_ssn("123-45-6789"))
        self.assertTrue(is_valid_ssn("234-56-7890"))

    def test_ssn_invalid(self):
        """Test SSN rejection for invalid patterns."""
        self.assertFalse(is_valid_ssn("000-00-0000"))
        self.assertFalse(is_valid_ssn("666-99-9999"))

    def test_ssn_detection(self):
        """Test SSN detection in text."""
        text = "Employee ID: 123-45-6789"
        results = detect_ssns(text)
        self.assertGreaterEqual(len(results), 1)


class TestCreditCardDetection(unittest.TestCase):
    """Credit card detection tests."""

    def test_credit_card_luhn_valid(self):
        """Test valid credit card Luhn checksum."""
        self.assertTrue(is_valid_credit_card("4532-1234-5678-9010"))

    def test_credit_card_detection(self):
        """Test credit card detection."""
        text = "Payment via 4532-1234-5678-9010"
        results = detect_credit_cards(text)
        self.assertGreaterEqual(len(results), 1)


class TestDOBDetection(unittest.TestCase):
    """Date of Birth detection tests."""

    def test_dob_valid(self):
        """Test valid DOB dates."""
        self.assertTrue(is_valid_dob("15/06/1985"))
        self.assertTrue(is_valid_dob("22-03-1990"))

    def test_dob_invalid(self):
        """Test DOB rejection for future or invalid dates."""
        self.assertFalse(is_valid_dob("15/06/2025"))
        self.assertFalse(is_valid_dob("32/01/1990"))

    def test_dob_detection(self):
        """Test DOB detection with explicit context."""
        text = "Date of Birth: 15/06/1985"
        results = detect_dobs(text)
        self.assertGreaterEqual(len(results), 1)


class TestIPDetection(unittest.TestCase):
    """IP address detection tests."""

    def test_ipv4_validation(self):
        """Test IPv4 validation."""
        self.assertTrue(is_valid_ipv4("203.45.67.89"))
        self.assertTrue(is_valid_ipv4("192.168.1.1"))
        self.assertFalse(is_valid_ipv4("256.1.1.1"))

    def test_ipv4_documentation_ranges(self):
        """Test documentation IP exclusion."""
        self.assertTrue(is_documentation_ip("192.0.2.1"))
        self.assertTrue(is_documentation_ip("10.0.0.1"))
        self.assertTrue(is_documentation_ip("127.0.0.1"))
        self.assertFalse(is_documentation_ip("203.45.67.89"))

    def test_ip_detection(self):
        """Test IP detection."""
        text = "Server at 203.45.67.89 failed"
        results = detect_ip_addresses(text)
        self.assertGreaterEqual(len(results), 1)


class TestPersonDetection(unittest.TestCase):
    """Person name detection tests."""

    def test_person_looks_like(self):
        """Test person name heuristics."""
        self.assertTrue(looks_like_person("Rajesh Sharma"))
        self.assertTrue(looks_like_person("Priya Verma"))
        self.assertFalse(looks_like_person("company secretary"))

    def test_person_detection(self):
        """Test person detection from Contact Person field."""
        text = "Contact Person: Rajesh Sharma"
        results = detect_people(text)
        detected_names = [r.surface for r in results]
        self.assertTrue(any("Rajesh" in name for name in detected_names))

    def test_person_false_positive_rejection(self):
        """Test rejection of false positive person names."""
        text = "Reference Rate of 5.5%"
        results = detect_people(text)
        self.assertEqual(len(results), 0)


class TestCompanyDetection(unittest.TestCase):
    """Company detection tests."""

    def test_company_looks_like(self):
        """Test company name heuristics."""
        self.assertTrue(looks_like_company("Infosys Limited"))
        self.assertTrue(looks_like_company("HDFC Bank"))
        self.assertTrue(looks_like_company("TCS Private Limited"))

    def test_company_detection(self):
        """Test company detection."""
        text = "Managed by Infosys Limited and HDFC Bank"
        results = detect_companies(text)
        companies = [r.surface.casefold() for r in results]
        self.assertTrue(any("infosys" in c for c in companies))


class TestAddressDetection(unittest.TestCase):
    """Address detection tests."""

    def test_address_detection(self):
        """Test address detection with explicit label."""
        text = "Residential Address: 123 Main Street, Mumbai, Maharashtra 400001"
        results = detect_addresses(text)
        self.assertGreaterEqual(len(results), 1)

    def test_address_requires_label(self):
        """Test that bare addresses without labels are not detected."""
        text = "The office is at 123 Street, Delhi"
        results = detect_addresses(text)
        self.assertEqual(len(results), 0)


class TestDeterministicReplacement(unittest.TestCase):
    """Deterministic replacement tests."""

    def test_deterministic_replacement(self):
        """Test that same entity gets same replacement across runs."""
        from redaction import SyntheticGenerator

        seed1 = SyntheticGenerator()
        seed2 = SyntheticGenerator()

        entity_id = "PERSON_abc123def456"
        used1 = set()
        used2 = set()

        name1 = seed1.person_name(entity_id, used1)
        name2 = seed2.person_name(entity_id, used2)

        self.assertEqual(name1, name2)


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def test_complex_snippet(self):
        """Test detection on complex multi-PII snippet."""
        text = (
            "Contact Person: Sarthak Malvadkar, Email: sarthak@company.com, "
            "Phone: +91-99876-54321, Date of Birth: 12/05/1982, "
            "Residential Address: 123 Tech Street, Pune 411001"
        )

        emails = detect_emails(text)
        phones = detect_phones(text)
        people = detect_people(text)
        dobs = detect_dobs(text)
        addresses = detect_addresses(text)

        self.assertGreaterEqual(len(emails), 1)
        self.assertGreaterEqual(len(phones), 1)
        self.assertGreaterEqual(len(people), 1)
        self.assertGreaterEqual(len(dobs), 1)
        self.assertGreaterEqual(len(addresses), 1)

    def test_empty_text(self):
        """Detectors should handle empty text gracefully."""
        text = ""
        self.assertEqual(len(detect_emails(text)), 0)
        self.assertEqual(len(detect_phones(text)), 0)
        self.assertEqual(len(detect_people(text)), 0)
        self.assertEqual(len(detect_companies(text)), 0)

    def test_whitespace_only(self):
        """Detectors should handle whitespace-only text."""
        text = "   \n\t   "
        self.assertEqual(len(detect_people(text)), 0)
        self.assertEqual(len(detect_companies(text)), 0)

    def test_case_insensitivity(self):
        """Tests should handle case variations."""
        text = "DATE OF BIRTH: 15/06/1985"
        results = detect_dobs(text)
        self.assertGreaterEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

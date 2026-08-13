"""
Unit tests for PII Redaction Tool replacement engine and validation.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from redaction import (
    Detection,
    EntityRegistry,
    SyntheticGenerator,
    assign_replacements,
    build_replacement_map,
    validate_replacement,
    extract_document_text,
)
from docx import Document


class TestSyntheticGenerator(unittest.TestCase):
    """Test synthetic value generation across categories."""

    def setUp(self):
        self.generator = SyntheticGenerator()

    def test_deterministic_person_name(self):
        """Same entity ID must yield same synthetic name."""
        entity_id = "PERSON_a1b2c3d4e5f6"
        used_a, used_b = set(), set()
        name1 = self.generator.person_name(entity_id, used_a)
        name2 = self.generator.person_name(entity_id, used_b)
        self.assertEqual(name1, name2)

    def test_company_name_pool_overflow_indexing(self):
        """Company generator must handle >56 unique company entities using indexed fallback."""
        used = set()
        generated = []
        for i in range(100):
            entity_id = f"COMPANY_{i:04d}"
            comp = self.generator.company_name(entity_id, used)
            self.assertNotIn(comp.casefold(), used)
            used.add(comp.casefold())
            generated.append(comp)
        self.assertEqual(len(generated), 100)

    def test_phone_formatting_preservation(self):
        """Phone generator must preserve +91 prefix and formatting structure."""
        original = "+91 98765-43210"
        synth = self.generator.phone(original, 1)
        self.assertTrue(synth.startswith("+91"))
        self.assertEqual(len(synth), len(original))

    def test_ssn_synthetic_format(self):
        """SSN generator must produce safe valid SSN pattern."""
        synth = self.generator.ssn("SSN_12345")
        self.assertRegex(synth, r"^\d{3}-\d{2}-\d{4}$")

    def test_credit_card_luhn_validity(self):
        """Credit card generator must produce Luhn-valid card number."""
        from redaction import is_valid_credit_card
        synth = self.generator.credit_card("CREDIT_CARD_999")
        self.assertTrue(is_valid_credit_card(synth))


class TestEntityRegistryAndMapping(unittest.TestCase):
    """Test EntityRegistry deduplication and replacement mapping."""

    def test_entity_canonicalization(self):
        """Multiple surface forms must map to single canonical entity."""
        registry = EntityRegistry()

        d1 = Detection(category="PHONE", surface="+91 98765-43210", normalized="+919876543210", confidence="HIGH", evidence="")
        d2 = Detection(category="PHONE", surface="9876543210", normalized="+919876543210", confidence="HIGH", evidence="")

        registry.add(d1)
        registry.add(d2)

        self.assertEqual(len(registry.all()), 1)
        entity = registry.all()[0]
        self.assertEqual(len(entity.surfaces), 2)

    def test_replacement_map_building(self):
        """All surfaces must map to assigned synthetic replacement."""
        registry = EntityRegistry()
        d = Detection(category="EMAIL", surface="john.doe@company.com", normalized="john.doe@company.com", confidence="HIGH", evidence="")
        registry.add(d)
        assign_replacements(registry)
        mapping = build_replacement_map(registry)
        self.assertIn("john.doe@company.com", mapping)
        self.assertTrue(mapping["john.doe@company.com"].startswith("contact"))


class TestDocxRedactionAndValidation(unittest.TestCase):
    """Test DOCX document redaction and replacement validation."""

    def test_subentity_replacement_validation(self):
        """Validation must pass when a sub-entity surface is covered by a longer entity replacement."""
        doc = Document()
        doc.add_paragraph("Managed by Elantas Beck India Limited")

        registry = EntityRegistry()
        d_long = Detection(category="COMPANY", surface="Elantas Beck India Limited", normalized="elantas beck india limited", confidence="HIGH", evidence="")
        d_short = Detection(category="COMPANY", surface="Beck India Limited", normalized="beck india limited", confidence="HIGH", evidence="")

        registry.add(d_long)
        registry.add(d_short)
        assign_replacements(registry)

        from redaction import redact_document
        redact_document(doc, registry)

        results = validate_replacement(doc, registry)
        for r in results:
            self.assertFalse(r["original_remaining"])
            self.assertTrue(r["replacement_present"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

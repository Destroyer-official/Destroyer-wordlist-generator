"""
Unit and Integration Test Suite for Destroyer
==============================================
Validates all sub-packages, modules, generators, mathematical models,
streaming pipelines, and CLI entry points.
"""

from __future__ import annotations

import gzip
import json
import math
import os
import shutil
import tempfile
import unittest

from destroyer.config import AppConfig, load_configuration
from destroyer.core.dedup import MemoryBoundedDeduplicator
from destroyer.core.engine import DestroyerEngine
from destroyer.core.entropy import (
    calculate_keyspace_entropy,
    calculate_shannon_entropy,
    estimate_crack_time,
)
from destroyer.core.streamer import StreamWriter
from destroyer.exporters.hashcat import export_hashcat_masks, export_hashcat_rules
from destroyer.exporters.john import export_john_rules
from destroyer.generators.corporate import CorporateGenerator
from destroyer.generators.keyboard import KeyboardWalkGenerator
from destroyer.generators.mangler import ManglerGenerator
from destroyer.generators.markov import MarkovTransitionGenerator
from destroyer.generators.passphrase import PassphraseGenerator
from destroyer.generators.pcfg import PCFGGenerator
from destroyer.models.grammar import PCFG_PRODUCTION_CATALOG
from destroyer.models.profile import TargetProfile, parse_date_components
from destroyer.osint.normalizer import filter_tokens, normalize_token
from destroyer.osint.scraper import HTMLTextExtractor


class TestDestroyerConfig(unittest.TestCase):
    """Test configuration loader and default fallbacks."""

    def test_default_config_loading(self):
        cfg = load_configuration()
        self.assertIsInstance(cfg, AppConfig)
        self.assertIn("2027", cfg.years)
        self.assertIn("Spring", cfg.seasons)
        self.assertIn("Q1", cfg.quarters)
        self.assertIn("October", cfg.months)
        self.assertIn("123456", cfg.walks)
        self.assertEqual(cfg.wcfrom, 8)
        self.assertEqual(cfg.wcto, 64)
        self.assertEqual(cfg.min_passphrase_length, 15)

    def test_custom_config_loading(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".cfg") as tmp:
            tmp.write("[shaping]\nwcfrom=10\nwcto=32\n[years]\nyears=2025,2026,2027\n")
            tmp_path = tmp.name

        try:
            cfg = load_configuration(tmp_path)
            self.assertEqual(cfg.wcfrom, 10)
            self.assertEqual(cfg.wcto, 32)
            self.assertEqual(cfg.years, ["2025", "2026", "2027"])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestTargetProfile(unittest.TestCase):
    """Test target reconnaissance profile model and date parsing."""

    def test_parse_date_components_8_digits(self):
        comp = parse_date_components("14051996")
        self.assertEqual(comp["yyyy"], "1996")
        self.assertEqual(comp["yy"], "96")
        self.assertEqual(comp["dd"], "14")
        self.assertEqual(comp["mm"], "05")
        self.assertEqual(comp["ddmm"], "1405")

    def test_parse_date_components_iso(self):
        comp = parse_date_components("1996-05-14")
        self.assertEqual(comp["yyyy"], "1996")
        self.assertEqual(comp["yy"], "96")

    def test_parse_date_components_year_only(self):
        comp = parse_date_components("1996")
        self.assertEqual(comp["yyyy"], "1996")
        self.assertEqual(comp["yy"], "96")

    def test_profile_serialization(self):
        raw = {
            "name": "Alex",
            "surname": "Mercer",
            "nick": "shadow",
            "handles": ["alexpwns"],
            "email": "alex@corp.internal",
            "birthdate": "14051996",
            "mobile": "+1-987-654-3210",
            "company": "CyberCorp",
            "keywords": ["matrix", "crypto"],
        }
        profile = TargetProfile.from_dict(raw)
        self.assertEqual(profile.name, "alex")
        self.assertEqual(profile.surname, "mercer")
        self.assertEqual(profile.mobile, "19876543210")
        self.assertEqual(profile.birth_components["yyyy"], "1996")

        serialized = profile.to_dict()
        self.assertEqual(serialized["name"], "alex")
        self.assertEqual(serialized["company"], "cybercorp")


class TestEntropyAndMetrics(unittest.TestCase):
    """Test mathematical keyspace and Shannon entropy calculations."""

    def test_keyspace_entropy_pure_lower(self):
        # 8 lowercase letters: 8 * log2(26) ≈ 37.6 bits
        h = calculate_keyspace_entropy("password")
        self.assertAlmostEqual(h, 8 * (math.log2(26)), delta=0.1)

    def test_keyspace_entropy_complex(self):
        # 12 chars mixed: lower + upper + digit + symbol = 26+26+10+33 = 95
        # 12 * log2(95) ≈ 78.8 bits
        h = calculate_keyspace_entropy("P@ssw0rd2027!")
        self.assertGreater(h, 75.0)

    def test_shannon_entropy(self):
        h = calculate_shannon_entropy("aaaa")
        self.assertEqual(h, 0.0)  # Zero uncertainty
        h_diff = calculate_shannon_entropy("abcd")
        self.assertGreater(h_diff, 0.0)

    def test_crack_time_estimates(self):
        self.assertEqual(estimate_crack_time(0.0), "Instant")
        self.assertIn("seconds", estimate_crack_time(40.0))
        self.assertIn("years", estimate_crack_time(90.0))


class TestMemoryBoundedDeduplicator(unittest.TestCase):
    """Test deduplicator capacity bounding and uniqueness checks."""

    def test_uniqueness_and_reset(self):
        dedup = MemoryBoundedDeduplicator(capacity=5)
        self.assertTrue(dedup.is_unique("word1"))
        self.assertFalse(dedup.is_unique("word1"))
        self.assertTrue(dedup.is_unique("word2"))
        self.assertEqual(len(dedup), 2)

        dedup.reset()
        self.assertEqual(len(dedup), 0)

    def test_capacity_bounding(self):
        dedup = MemoryBoundedDeduplicator(capacity=3)
        dedup.is_unique("a")
        dedup.is_unique("b")
        dedup.is_unique("c")
        self.assertEqual(len(dedup), 3)
        # Exceed capacity: cache must clear to maintain bound
        dedup.is_unique("d")
        self.assertLessEqual(len(dedup), 3)


class TestStreamWriter(unittest.TestCase):
    """Test file streaming, length filtering, and transparent gzip output."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_plaintext_streaming(self):
        out_file = os.path.join(self.test_dir, "output.txt")
        writer = StreamWriter(filepath=out_file, min_len=8, max_len=20)

        def mock_gen():
            yield "short"        # 5 chars: filtered out
            yield "validpass1"   # 10 chars: kept
            yield "validpass1"   # Duplicate: filtered out
            yield "toolongpassphrase1234567890"  # 27 chars: filtered out
            yield "anotherpass2" # 12 chars: kept

        stats = writer.write_stream(mock_gen())
        self.assertEqual(stats["total_words"], 2)

        with open(out_file, "r", encoding="utf-8") as fh:
            lines = [l.strip() for l in fh]
        self.assertEqual(lines, ["validpass1", "anotherpass2"])

    def test_gzip_streaming(self):
        out_file = os.path.join(self.test_dir, "output.txt.gz")
        writer = StreamWriter(filepath=out_file, min_len=8, max_len=30)

        def mock_gen():
            yield "compressedpass1"
            yield "compressedpass2"

        stats = writer.write_stream(mock_gen())
        self.assertEqual(stats["total_words"], 2)

        with gzip.open(out_file, "rt", encoding="utf-8") as fh:
            lines = [l.strip() for l in fh]
        self.assertEqual(lines, ["compressedpass1", "compressedpass2"])


class TestGenerators(unittest.TestCase):
    """Test individual combinatorial sub-generators."""

    def setUp(self):
        self.cfg = load_configuration()

    def test_pcfg_generator(self):
        gen = PCFGGenerator(
            primary_tokens=["shadow"],
            date_tokens=["1996"],
            config=self.cfg,
            mode="fast"
        )
        cands = list(gen.generate())
        self.assertGreater(len(cands), 50)
        self.assertTrue(any("Shadow2027!" in c for c in cands))
        self.assertTrue(any("Shadow123!" in c for c in cands))
        self.assertTrue(any("Shadow1996" in c for c in cands))

    def test_passphrase_generator(self):
        gen = PassphraseGenerator(
            token_pool=["shadow", "mercer", "cybercorp"],
            config=self.cfg,
            mode="passphrase",
            nist_mode=True
        )
        cands = list(gen.generate())
        self.assertGreater(len(cands), 20)
        self.assertTrue(any("-" in c for c in cands))
        self.assertTrue(any("Shadow" in c and "Mercer" in c for c in cands))

    def test_corporate_generator(self):
        gen = CorporateGenerator(
            corporate_tokens=["cybercorp"],
            config=self.cfg
        )
        cands = list(gen.generate())
        self.assertGreater(len(cands), 50)
        self.assertTrue(any("Spring2027!" in c for c in cands))
        self.assertTrue(any("Cybercorp2027!" in c for c in cands))
        self.assertTrue(any("October" in c for c in cands))

    def test_mangler_generator(self):
        gen = ManglerGenerator(
            base_tokens=["password"],
            config=self.cfg,
            mode="light"
        )
        cands = list(gen.generate())
        # a -> @, or full light p@$$w0rd
        self.assertTrue(any("p@ssword" in c or "p@$$w0rd" in c for c in cands))

    def test_keyboard_walk_generator(self):
        gen = KeyboardWalkGenerator(
            base_tokens=["alex"],
            config=self.cfg
        )
        cands = list(gen.generate())
        self.assertTrue(any("Alex123456" in c for c in cands))

    def test_markov_generator(self):
        gen = MarkovTransitionGenerator(seed_tokens=["cyber", "security", "shadow"])
        cands = list(gen.generate(max_candidates=10))
        self.assertGreater(len(cands), 0)


class TestOSINTModules(unittest.TestCase):
    """Test token normalizer and HTML extractor."""

    def test_normalizer(self):
        self.assertEqual(normalize_token("  P@ssword!  "), "pssword")
        tokens = ["about", "customkeyword", "the", "devops", "12345"]
        filtered = filter_tokens(tokens)
        self.assertIn("customkeyword", filtered)
        self.assertIn("devops", filtered)
        self.assertNotIn("about", filtered)  # Stop word
        self.assertNotIn("the", filtered)    # Stop word
        self.assertNotIn("12345", filtered)  # Numeric only

    def test_html_text_extractor(self):
        parser = HTMLTextExtractor()
        html = (
            "<html><head><title>Ignore Head</title></head>"
            "<body><h1>Target Corporate Portal</h1>"
            "<p>Production Kubernetes Infrastructure</p>"
            "<script>var secret = 'ignore_script';</script>"
            "<style>.ignore_css {}</style>"
            "</body></html>"
        )
        parser.feed(html)
        self.assertIn("Target", parser.words)
        self.assertIn("Corporate", parser.words)
        self.assertIn("Kubernetes", parser.words)
        self.assertNotIn("ignore_script", parser.words)


class TestExporters(unittest.TestCase):
    """Test Hashcat and John the Ripper export utilities."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_hashcat_rules_export(self):
        out_rule = os.path.join(self.test_dir, "test.rule")
        export_hashcat_rules(out_rule)
        self.assertTrue(os.path.isfile(out_rule))
        with open(out_rule, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("c $2 $0 $2 $7", content)
        self.assertIn("sa@ se3 si1 so0", content)

    def test_hashcat_masks_export(self):
        out_mask = os.path.join(self.test_dir, "test.hcmask")
        export_hashcat_masks(out_mask)
        self.assertTrue(os.path.isfile(out_mask))
        with open(out_mask, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("?u?l?l?l?l2027!", content)

    def test_john_rules_export(self):
        out_rules = os.path.join(self.test_dir, "test.rules")
        export_john_rules(out_rules)
        self.assertTrue(os.path.isfile(out_rules))
        with open(out_rules, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("[List.Rules:Destroyer]", content)


class TestEndToEndEngine(unittest.TestCase):
    """Test full end-to-end execution of DestroyerEngine."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_pipeline_execution(self):
        profile_data = {
            "name": "alex",
            "surname": "mercer",
            "nick": "shadow",
            "company": "cybercorp",
            "birthdate": "14051996",
            "keywords": ["devops", "cloud"],
        }
        profile = TargetProfile.from_dict(profile_data)
        out_file = os.path.join(self.test_dir, "generated_passwords.txt")

        engine = DestroyerEngine(
            profile=profile,
            mode="fast",
            min_len=8,
            max_len=30,
            leet_mode="light",
            include_corporate=True,
            nist_mode=False
        )

        metrics = engine.execute(out_file)
        self.assertGreater(metrics["total_words"], 1000)
        self.assertGreater(metrics["avg_entropy"], 40.0)
        self.assertTrue(os.path.isfile(out_file))

        with open(out_file, "r", encoding="utf-8") as fh:
            lines = [l.strip() for l in fh]
        self.assertIn("Alex2027!", lines)
        self.assertIn("Cybercorp2027!", lines)


if __name__ == "__main__":
    unittest.main()

import unittest

from support import REPOSITORY  # noqa: F401  (puts tools/ on sys.path)
from dreamweave.versions import Constraint, Version, VersionError


class VersionOrdering(unittest.TestCase):
    def test_numbers_compare_as_numbers_not_decimals(self):
        self.assertLess(Version.parse("0.9"), Version.parse("0.82"))
        self.assertLess(Version.parse("1.2.9"), Version.parse("1.2.10"))

    def test_missing_components_are_zero(self):
        self.assertEqual(Version.parse("1.2"), Version.parse("1.2.0"))
        self.assertEqual(hash(Version.parse("1")), hash(Version.parse("1.0.0")))

    def test_prerelease_rules_follow_semver(self):
        ordered = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta", "1.0.0-beta.2", "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0"]
        versions = [Version.parse(text) for text in ordered]
        self.assertEqual(versions, sorted(versions))

    def test_build_metadata_does_not_change_precedence(self):
        self.assertEqual(Version.parse("1.0.0+linux"), Version.parse("1.0.0+windows"))

    def test_rejects_malformed_versions(self):
        for text in ["", "v1.0", "1.0.", "01.2", "1.2.3-01", "1..2", "1.2.3.4.5.6.7", "latest"]:
            with self.subTest(text=text), self.assertRaises(VersionError):
                Version.parse(text)

    def test_development_builds_sort_between_releases(self):
        released = Version.parse("1.2.0")
        development = released.next_development(4)
        self.assertEqual(str(development), "1.2.1-dev.4")
        self.assertLess(released, development)
        self.assertLess(development, Version.parse("1.2.1"))
        self.assertLess(development, released.next_development(5))

    def test_development_after_a_prerelease_stays_below_the_final_release(self):
        beta = Version.parse("2.0.0-beta.1")
        development = beta.next_development(3)
        self.assertLess(beta, development)
        self.assertLess(development, Version.parse("2.0.0-beta.2"))
        self.assertLess(development, Version.parse("2.0.0"))


class Constraints(unittest.TestCase):
    def test_comparators_all_must_hold(self):
        constraint = Constraint.parse(">=0.49, <0.51")
        self.assertTrue(constraint.allows(Version.parse("0.49")))
        self.assertTrue(constraint.allows(Version.parse("0.50.3")))
        self.assertFalse(constraint.allows(Version.parse("0.51")))
        self.assertFalse(constraint.allows(Version.parse("0.48.9")))

    def test_star_allows_anything(self):
        self.assertTrue(Constraint.parse("*").allows(Version.parse("0.0.1-dev.1")))

    def test_every_operator(self):
        version = Version.parse("1.5")
        expectations = {"=1.5": True, "!=1.5": False, ">1.4": True, ">=1.5": True, "<1.5": False, "<=1.5.0": True}
        for text, expected in expectations.items():
            with self.subTest(text=text):
                self.assertEqual(Constraint.parse(text).allows(version), expected)

    def test_rejects_ambiguous_grammar_with_a_hint(self):
        hints = {"^1.2": "not supported", "~1.2": "not supported", "1.2": "exactly that version", ">=1 || <3": "AND-only", "": "empty", "2+": "not a comparator"}
        for text, hint in hints.items():
            with self.subTest(text=text), self.assertRaisesRegex(VersionError, hint):
                Constraint.parse(text)


if __name__ == "__main__":
    unittest.main()

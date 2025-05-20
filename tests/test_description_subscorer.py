import unittest

from api_scoring_app.infra.subscorers.subscorer_description import DescriptionSubscorer
from api_scoring_app.core.subscorers import IssueSeverity
from api_scoring_app.core.parser import ParsedSpecification, ParsedDescription
from api_scoring_app.core.config import Config

class TestDescriptionSubscorer(unittest.TestCase):
    """Test suite for DescriptionSubscorer."""

    def setUp(self):
        self.max_points = 20
        self.subscorer = DescriptionSubscorer(points=self.max_points)
        self.subscorer_name = Config.DESCRIPTION_SUBSCORER_NAME

    def test_no_issues(self):
        """Test scoring with no issues."""

        parsed_spec = ParsedSpecification()
        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertEqual(report.subscorer, self.subscorer_name)
        self.assertEqual(report.points, self.max_points)
        self.assertEqual(len(report.issues), 0)

    def test_missing_descriptions(self):
        """Test scoring with missing descriptions."""

        missing_descriptions = [
            ["a", "b", "c"],
            ["ka", "be", "ce"]
        ]

        parsed_spec = ParsedSpecification()
        parsed_spec.descriptions = ParsedDescription(
            missing_descriptions=missing_descriptions
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]

        self.assertTrue(report.points < self.max_points)
        self.assertEqual(len(report.issues), len(missing_descriptions))

        issues = report.issues

        missing_description_count = 0
        for issue in issues:
            self.assertTrue(issue.severity == IssueSeverity.LOW)
            for path in missing_descriptions:
                path_as_string = " -> ".join(path)
                if path_as_string in issue.path:
                    missing_description_count += 1

        self.assertEqual(missing_description_count, len(missing_descriptions))

    def test_short_descriptions(self):
        """Test scoring with short descriptions."""

        short_descriptions = [
            ["a", "b", "c"],
            ["va", "be", "ce"]
        ]

        parsed_spec = ParsedSpecification()
        parsed_spec.descriptions = ParsedDescription(
            short_descriptions=short_descriptions
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertTrue(report.points < self.max_points)
        self.assertEqual(len(report.issues), len(short_descriptions))

        issues = report.issues
        short_description_count = 0
        for issue in issues:
            self.assertTrue(issue.severity == IssueSeverity.LOW)
            for path in short_descriptions:
                path_as_string = " -> ".join(path)
                if path_as_string in issue.path:
                    short_description_count += 1
                    break
            self.assertIn(str(Config.DESCRIPTION_MIN_DESCRIPTION_LENGTH), issue.suggestion)

        self.assertEqual(short_description_count, len(short_descriptions))

    def test_multiple_issues(self):
        """Test scoring with both missing and short descriptions."""

        missing_descriptions = [
            ["a", "mista", "zozin"]
        ]

        short_descriptions = [
            ["ka", "ge", "be"]
        ]

        parsed_spec = ParsedSpecification()
        parsed_spec.descriptions = ParsedDescription(
            missing_descriptions=missing_descriptions,
            short_descriptions=short_descriptions
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]

        self.assertTrue(report.points < self.max_points)
        self.assertEqual(len(report.issues), 2)

        issues = report.issues
        missing_count = 0
        short_count = 0
        for issue in issues:
            self.assertTrue(issue.severity == IssueSeverity.LOW)

            if "Missing" in issue.message:
                for path in missing_descriptions:
                    path_as_string = " -> ".join(path)
                    if path_as_string in issue.path:
                        missing_count += 1

            if "too short" in issue.message:
                for path in short_descriptions:
                    path_as_string = " -> ".join(path)
                    if path_as_string in issue.path:
                        short_count += 1

        self.assertEqual(missing_count, len(missing_descriptions))
        self.assertEqual(short_count, len(short_descriptions))

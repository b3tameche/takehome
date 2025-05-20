import unittest

from api_scoring_app.infra.subscorers.subscorer_schema import SchemaSubscorer
from api_scoring_app.core.subscorers import IssueSeverity
from api_scoring_app.core.parser import ParsedSpecification, ParsedSchema
from api_scoring_app.core.config import Config

class TestSchemaSubscorer(unittest.TestCase):
    """Test suite for SchemaSubscorer."""

    def setUp(self):
        self.max_points = 20
        self.subscorer = SchemaSubscorer(points=self.max_points)
        self.subscorer_name = Config.SCHEMA_SUBSCORER_NAME

    def test_no_issues(self):
        """Test scoring with no issues."""

        parsed_spec = ParsedSpecification()
        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertEqual(report.subscorer, self.subscorer_name)
        self.assertEqual(report.points, self.max_points)
        self.assertEqual(len(report.issues), 0)

    def test_free_form_schemas(self):
        """Test scoring with free-form schemas."""

        free_form_schemas = [
            ["a", "b"],
            ["a", "b", "c"]
        ]

        parsed_spec = ParsedSpecification()
        parsed_spec.schemas = ParsedSchema(
            free_form_schemas=free_form_schemas
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]

        self.assertTrue(report.points < self.max_points)
        self.assertEqual(len(report.issues), len(free_form_schemas))

        issues = report.issues

        free_form_schema_count = 0
        for issue in issues:
            self.assertTrue(issue.severity == IssueSeverity.MEDIUM)
            for path in free_form_schemas:
                path_as_string = " -> ".join(path)
                if path_as_string in issue.path:
                    free_form_schema_count += 1
                    break

        self.assertEqual(free_form_schema_count, len(free_form_schemas))

    def test_missing_schemas(self):
        """Test scoring with missing schemas."""

        missing_schemas = [
            ["a", "b", "c"]
        ]

        parsed_spec = ParsedSpecification()
        parsed_spec.schemas = ParsedSchema(
            missing_schemas=missing_schemas
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertTrue(report.points < self.max_points)
        self.assertEqual(len(report.issues), len(missing_schemas))

        issues = report.issues
        missing_schema_count = 0
        for issue in issues:
            self.assertTrue(issue.severity == IssueSeverity.MEDIUM)
            for path in missing_schemas:
                path_as_string = " -> ".join(path)
                if path_as_string in issue.path:
                    missing_schema_count += 1

        self.assertEqual(missing_schema_count, len(missing_schemas))

    def test_multiple_issues(self):
        """Test scoring with both free-form and missing schemas."""
        
        free_form_schemas = [
            ["a", "b", "c"]
        ]

        missing_schemas = [
            ["x", "y", "z"]
        ]

        parsed_spec = ParsedSpecification()
        parsed_spec.schemas = ParsedSchema(
            free_form_schemas=free_form_schemas,
            missing_schemas=missing_schemas
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]

        self.assertTrue(report.points < self.max_points)
        self.assertEqual(len(report.issues), 2)

        issues = report.issues
        free_form_count = 0
        missing_count = 0
        for issue in issues:
            for path in free_form_schemas:
                path_as_string = " -> ".join(path)
                if path_as_string in issue.path:
                    free_form_count += 1
                    break

            for path in missing_schemas:
                path_as_string = " -> ".join(path)
                if path_as_string in issue.path:
                    missing_count += 1
                    break

        self.assertEqual(free_form_count, 1)
        self.assertEqual(missing_count, 1)

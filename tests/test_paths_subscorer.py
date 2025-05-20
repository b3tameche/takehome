import unittest

from api_scoring_app.infra.subscorers import PathsSubscorer
from api_scoring_app.core.subscorers import IssueSeverity
from api_scoring_app.core.parser import ParsedSpecification, ParsedPaths
from api_scoring_app.core import Config
from api_scoring_app.core.subscorers import Issue

class TestPathsSubscorer(unittest.TestCase):
    """Test suite for PathsSubscorer."""

    def setUp(self):
        self.max_points = 15
        self.subscorer = PathsSubscorer(points=self.max_points)
        self.subscorer_name = Config.PATHS_SUBSCORER_NAME


    def test_no_issues(self):
        """Test scoring with no issues."""

        parsed_spec = ParsedSpecification()
        parsed_spec.paths = ParsedPaths(
            path_to_operations={
                "/a": ["get", "post"],
                "/a/{x}": ["get", "post", "put"]
            }
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertEqual(report.subscorer, self.subscorer_name)
        self.assertEqual(report.points, self.max_points)
        self.assertEqual(len(report.issues), 0)


    def test_crud_violations(self):
        """Test scoring with CRUD violations."""

        path_to_operations = {
            "/create": ["get"],
            "/list": ["post"],
            "/update": ["delete"],
            "/delete": ["put"]
        }

        parsed_spec = ParsedSpecification()
        parsed_spec.paths = ParsedPaths(
            path_to_operations=path_to_operations
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertTrue(report.points < self.max_points)

        # CRUD violation issues
        crud_issues: list[Issue] = []
        for path, _ in path_to_operations.items():
            crud_issues.extend([issue for issue in report.issues if "crud" in issue.message.lower() and path in issue.path])

        self.assertEqual(len(crud_issues), len(path_to_operations))

        for issue in crud_issues:
            self.assertEqual(issue.severity, IssueSeverity.LOW)
            self.assertIn("paths ->", issue.path)
            self.assertIn("GET", issue.suggestion)
            self.assertIn("POST", issue.suggestion)
            self.assertIn("PUT/PATCH", issue.suggestion)
            self.assertIn("DELETE", issue.suggestion)


    def test_overlapping_paths(self):
        """Test scoring with overlapping paths."""

        # not comprehensive but enough I guess
        path_to_operations = {
            "/a/b": ["get", "post"],
            "/a/{x}": ["get", "post", "put"]
        }

        parsed_spec = ParsedSpecification()
        parsed_spec.paths = ParsedPaths(
            path_to_operations=path_to_operations
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertTrue(report.points < self.max_points)

        overlapping_issues: list[Issue] = [issue for issue in report.issues if "overlapping" in issue.message.lower()]
        paths = list(path_to_operations.keys())
        
        for issue in overlapping_issues:
            self.assertEqual(issue.severity, IssueSeverity.HIGH)
            self.assertIn(paths[0], issue.message)
            self.assertIn(paths[1], issue.message)


    def test_inconsistent_naming(self):
        """Test scoring for inconsistently named paths."""

        path_to_operations = {
            "/a-b": ["get"],
            "/c_d": ["get"]
        }

        parsed_spec = ParsedSpecification()
        parsed_spec.paths = ParsedPaths(
            path_to_operations=path_to_operations
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertTrue(report.points < self.max_points)

        naming_issues = [issue for issue in report.issues if "inconsistent" in issue.message.lower()]
        self.assertEqual(len(naming_issues), 1)

        for issue in naming_issues:
            self.assertEqual(issue.severity, IssueSeverity.MEDIUM)
            self.assertIn("/a-b", issue.message)
            self.assertIn("/c_d", issue.message)
            self.assertIn("kebab", issue.suggestion)
            self.assertNotIn("snake", issue.suggestion)

    def test_multiple_issues(self):
        """Test scoring with multiple types of issues."""

        parsed_spec = ParsedSpecification()
        parsed_spec.paths = ParsedPaths(
            path_to_operations={
                "/create/{y}": ["get"],
                "/create/{z}": ["get"],
                "/a-b": ["get"],
                "/c_d": ["get"]
            }
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertTrue(report.points < self.max_points)

        overlapping_count = len([issue for issue in report.issues if "overlapping" in issue.message.lower()])
        naming_count = len([issue for issue in report.issues if "inconsistent" in issue.message.lower()])
        crud_count = len([issue for issue in report.issues if "crud" in issue.message.lower()])

        self.assertEqual(overlapping_count, 1)
        self.assertEqual(naming_count, 1)
        self.assertEqual(crud_count, 2)

        self.assertEqual(len(report.issues), overlapping_count + naming_count + crud_count)

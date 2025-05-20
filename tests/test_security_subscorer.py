import unittest

from api_scoring_app.infra.subscorers import SecuritySubscorer
from api_scoring_app.core.subscorers import IssueSeverity
from api_scoring_app.core.parser import ParsedSpecification, ParsedSecurity
from api_scoring_app.core import Config
from api_scoring_app.core.parser import WrappedSecurityRequirement
from openapi_pydantic import SecurityScheme, OAuthFlows, OAuthFlow

class TestSecuritySubscorer(unittest.TestCase):
    """Test suite for SecuritySubscorer."""

    def setUp(self):
        self.max_points = 10
        self.subscorer = SecuritySubscorer(points=self.max_points)
        self.subscorer_name = Config.SECURITY_SUBSCORER_NAME


    def test_no_issues(self):
        """Test scoring with no issues."""

        path = ["components", "securitySchemes", "basic"]

        scheme = SecurityScheme(
            type="http",
            scheme="basic"
        )

        basic_req = WrappedSecurityRequirement("basic", path)

        parsed_spec = ParsedSpecification()
        parsed_spec.security = ParsedSecurity(
            defined_schemes=[basic_req],
            referenced_schemes=[basic_req],
            operation_referenced_schemes=[],
            schemes=[
                (path, scheme)
            ]
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertEqual(report.subscorer, self.subscorer_name)
        self.assertEqual(report.points, self.max_points)
        self.assertEqual(len(report.issues), 0)


    def test_no_security_schemes(self):
        """Test scoring with no security schemes defined."""

        # security schemes are not defined
        
        parsed_spec = ParsedSpecification()

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertTrue(report.points < self.max_points)
        self.assertEqual(len(report.issues), 1)

        issue = report.issues[0]
        self.assertEqual(issue.severity, IssueSeverity.CRITICAL)
        self.assertIn("security schemes are not defined", issue.message.lower())


    def test_missing_oauth2_fields(self):
        """
        Test scoring with security scheme missing required fields.

        This one detects "missing OAuth scopes."
        """

        # security schemes are defined, but have missing fields

        path = ["components", "securitySchemes", "oauth2"]

        scheme = SecurityScheme(
            type="oauth2",
            flows=OAuthFlows(
                implicit=OAuthFlow(
                    authorizationUrl="url",
                    # missing scopes
                )
            )
        )

        oauth2_req = WrappedSecurityRequirement("oauth2", path)

        parsed_spec = ParsedSpecification()
        parsed_spec.security = ParsedSecurity(
            defined_schemes=[oauth2_req],
            referenced_schemes=[oauth2_req],
            operation_referenced_schemes=[],
            schemes=[
                (path, scheme)
            ]
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertTrue(report.points < self.max_points)

        zeroed_issues = [issue for issue in report.issues if issue.severity == IssueSeverity.ZERO]
        self.assertGreater(len(zeroed_issues), 0)

        for issue in zeroed_issues:
            self.assertIn("oauth2", str(issue.message).lower())


    def test_unreferenced_security_schemes(self):
        """Test scoring with unreferenced security schemes."""

        # security schemes are correctly defined, but not referenced

        path = ["components", "securitySchemes", "basic"]

        scheme = SecurityScheme(
            type="http",
            scheme="basic",
        )

        basic_req = WrappedSecurityRequirement("basic", path)

        parsed_spec = ParsedSpecification()
        parsed_spec.security = ParsedSecurity(
            defined_schemes=[basic_req],
            referenced_schemes=[], # not referenced
            operation_referenced_schemes=[],
            schemes=[
                (path, scheme)
            ]
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertTrue(report.points < self.max_points)
        self.assertEqual(len(report.issues), 1)

        issue = report.issues[0]
        self.assertEqual(issue.severity, IssueSeverity.HIGH)
        self.assertIn("not referenced", issue.message.lower())
        self.assertIn("basic", issue.message.lower())


    def test_undefined_security_schemes(self):
        """Test scoring with undefined but referenced security schemes."""

        # security schemes are referenced, but not defined

        path_defined = ["components", "securitySchemes", "defined"]
        path_referenced = ["security", "referenced"]

        defined_req = WrappedSecurityRequirement("defined", path_defined)
        referenced_req = WrappedSecurityRequirement("referenced", path_referenced)

        parsed_spec = ParsedSpecification()
        parsed_spec.security = ParsedSecurity(
            defined_schemes=[defined_req],
            referenced_schemes=[referenced_req, defined_req], # referenced, but not in defined_schemes
            operation_referenced_schemes=[],
            schemes=[]
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertTrue(report.points < self.max_points)
        self.assertEqual(len(report.issues), 1)

        issue = report.issues[0]
        self.assertEqual(issue.severity, IssueSeverity.MEDIUM)
        self.assertIn("not defined", issue.message)
        self.assertIn("but not defined", issue.message)


    def test_multiple_issues(self):
        """Test scoring with multiple types of security issues."""

        path_oauth2 = ["components", "securitySchemes", "oauth2"]
        path_basic = ["security", "basic"]

        oauth2_scheme = SecurityScheme(
            type="oauth2",
            flows=OAuthFlows(
                implicit=OAuthFlow(
                    authorizationUrl="url",
                    # 1. missing scopes
                )
            )
        )

        oauth2_req = WrappedSecurityRequirement("oauth2", path_oauth2)
        basic_req = WrappedSecurityRequirement("basic", path_basic)

        parsed_spec = ParsedSpecification()
        parsed_spec.security = ParsedSecurity(
            defined_schemes=[oauth2_req], # 2. defined, but not referenced
            referenced_schemes=[basic_req], # 3. referenced, but not defined
            operation_referenced_schemes=[],
            schemes=[
                (path_oauth2, oauth2_scheme)
            ]
        )

        reports = self.subscorer.score_spec(parsed_spec)

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertTrue(report.points < self.max_points)
        self.assertEqual(len(report.issues), 3)

        missing_fields_count = len([issue for issue in report.issues if "missing" in str(issue.message).lower()])
        undefined_count = len([issue for issue in report.issues if "but not defined" in issue.message])
        unreferenced_count = len([issue for issue in report.issues if "but not referenced" in issue.message])

        self.assertEqual(missing_fields_count, 1)
        self.assertEqual(undefined_count, 1)
        self.assertEqual(unreferenced_count, 1)

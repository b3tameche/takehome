import os
import unittest

from api_scoring_app.core.config import Config
from api_scoring_app.runner.ApiSpecProcessor import APISpecificationProcessor
from api_scoring_app.infra.subscorers import (
    SchemaSubscorer, 
    DescriptionSubscorer, 
    PathsSubscorer, 
    ResponseCodesSubscorer, 
    ExamplesSubscorer, 
    SecuritySubscorer, 
    MiscSubscorer
)

class TestIntegration(unittest.TestCase):
    """Integration test for specification with known issues."""

    def setUp(self):
        self.processor = APISpecificationProcessor()

        self.processor.scoring_engine.add_subscorer(SchemaSubscorer(points=10))
        self.processor.scoring_engine.add_subscorer(DescriptionSubscorer(points=10))
        self.processor.scoring_engine.add_subscorer(PathsSubscorer(points=10))
        self.processor.scoring_engine.add_subscorer(ResponseCodesSubscorer(points=10))
        self.processor.scoring_engine.add_subscorer(ExamplesSubscorer(points=10))
        self.processor.scoring_engine.add_subscorer(SecuritySubscorer(points=10))
        self.processor.scoring_engine.add_subscorer(MiscSubscorer(points=10))

        self.known_spec_path = os.path.join(os.path.dirname(__file__), "specs/test_known_issues.yaml")
        self.simplest_spec_path = os.path.join(os.path.dirname(__file__), "specs/spec_simplest.yaml")


    def test_known_issues_spec_scoring(self):
        """Test scoring of the spec with known issues."""
        
        reports = self.processor.process(self.known_spec_path)

        # all subscorers responded
        self.assertEqual(len(reports), 7)

        # total score
        total_score = sum(report.points for report in reports)
        total_max = sum(report.max_points for report in reports)
        self.assertTrue(total_score < total_max)

        # specific issues in reports
        schema_report = [report for report in reports if report.subscorer == Config.SCHEMA_SUBSCORER_NAME][0]
        desc_report = [report for report in reports if report.subscorer == Config.DESCRIPTION_SUBSCORER_NAME][0]
        paths_report = [report for report in reports if report.subscorer == Config.PATHS_SUBSCORER_NAME][0]
        response_report = [report for report in reports if report.subscorer == Config.RESPONSE_CODES_SUBSCORER_NAME][0]
        examples_report = [report for report in reports if report.subscorer == Config.EXAMPLES_SUBSCORER_NAME][0]
        security_report = [report for report in reports if report.subscorer == Config.SECURITY_SUBSCORER_NAME][0]
        misc_report = [report for report in reports if report.subscorer == Config.MISC_SUBSCORER_NAME][0]

        # SCHEMA SUBSCORER
        # should have exactly 2 issues
        self.assertEqual(len(schema_report.issues), 2)

        # one free-form schema
        self.assertEqual(len([issue for issue in schema_report.issues if "free-form" in issue.message.lower()]), 1)

        # one missing schema
        self.assertEqual(len([issue for issue in schema_report.issues if "missing" in issue.message.lower()]), 1)



        # DESCRIPTION SUBSCORER
        # should have exactly 2 issues
        self.assertEqual(len(desc_report.issues), 2)

        # one missing description
        self.assertEqual(len([issue for issue in desc_report.issues if "missing" in issue.message.lower()]), 1)
        
        # one too short description
        self.assertEqual(len([issue for issue in desc_report.issues if "too short" in issue.message.lower()]), 1)



        # PATHS SUBSCORER
        # should have exactly 1 issue
        self.assertEqual(len(paths_report.issues), 1)

        # has overlapping paths
        self.assertEqual(len([issue for issue in paths_report.issues if "overlapping" in issue.message.lower()]), 1)

        

        # RESPONSE CODES SUBSCORER
        # should have exactly 2 issues
        self.assertEqual(len(response_report.issues), 2)

        # one missing response code
        self.assertEqual(len([issue for issue in response_report.issues if "missing" in issue.message.lower()]), 1)

        # one empty content
        self.assertEqual(len([issue for issue in response_report.issues if "no content" in issue.message.lower()]), 1)
        


        # EXAMPLES SUBSCORER
        # should have exactly 1 issue
        self.assertEqual(len(examples_report.issues), 1)

        # missing response example
        self.assertEqual(len([issue for issue in examples_report.issues if "missing response example" in issue.message.lower()]), 1)



        # SECURITY SUBSCORER
        # should have exactly 1 issue
        self.assertEqual(len(security_report.issues), 1)

        # missing security scheme definitions
        self.assertEqual(len([issue for issue in security_report.issues if "security schemes are not defined" == issue.message.lower()]), 1)



        # MISC SUBSCORER
        # should have exactly 2 issues
        self.assertEqual(len(misc_report.issues), 2)

        # one referenced, but not defined tag
        self.assertEqual(len([issue for issue in misc_report.issues if "not consistently referenced" in issue.message.lower()]), 1)

        # one unversioned paths
        self.assertEqual(len([issue for issue in misc_report.issues if "paths are not consistently versioned" == issue.message.lower()]), 1)


import json

from typing import List, Dict, Protocol

from api_scoring_app.core.subscorers import ScoringReport, IssueSeverity


class IReportGenerator(Protocol):
    def generate_report(self, reports: List[ScoringReport]) -> str:
        pass


class ReportUtils:
    @staticmethod
    def get_total_score(reports: List[ScoringReport]) -> float:
        return round(sum(report.points for report in reports), 1)
    
    def get_max_possible_score(reports: List[ScoringReport]) -> float:
        return round(sum(report.max_points for report in reports), 1)

    @staticmethod
    def get_severity_counts(reports: List[ScoringReport]) -> Dict[str, int]:
        severity_counts = {
            IssueSeverity.LOW.name: 0,
            IssueSeverity.MEDIUM.name: 0, 
            IssueSeverity.HIGH.name: 0,
            IssueSeverity.CRITICAL.name: 0,
            IssueSeverity.ZERO.name: 0
        }

        for report in reports:
            for issue in report.issues:
                severity_name = issue.severity.name
                severity_counts[severity_name] += 1

        return severity_counts
    
    @staticmethod
    def get_overall_grade(reports: List[ScoringReport]) -> str:
        total_score = ReportUtils.get_total_score(reports)
        if total_score >= 90:
            return "A"
        elif total_score >= 80:
            return "B"
        elif total_score >= 70:
            return "C"
        elif total_score >= 60:
            return "D"
        elif total_score >= 50:
            return "E"
        else:
            return "F"


class JsonReportGenerator:
    def generate_report(self, reports: List[ScoringReport]) -> str:

        try:
            total_score = ReportUtils.get_total_score(reports)
            overall_grade = ReportUtils.get_overall_grade(reports)
            severity_counts = ReportUtils.get_severity_counts(reports)
            max_possible_score = ReportUtils.get_max_possible_score(reports)

            report_data = {
                "total_score": total_score,
                "max_total_Score": max_possible_score,
                "overall_grade": overall_grade,
                "severity_counts": severity_counts,
                "reports": [{
                    "subscorer": report.subscorer,
                    "score": round(report.points, 1),
                    "max_score": round(report.max_points, 1),
                    "issues": [
                        {
                            "message": issue.message,
                            "severity": issue.severity.name,
                            "path": issue.path if issue.path else "N/A",
                            "suggestion": issue.suggestion if issue.suggestion else "N/A"
                        }
                        for issue in report.issues
                    ]
                } for report in reports]
            }
                
            return json.dumps(report_data, indent=2)
        except json.JSONDecodeError as e:
            print(e)
            return "Error generating report"




class ReportGeneratorFactory:
    """Factory for creating spec exporters."""

    @staticmethod
    def generate(format: str = "json") -> IReportGenerator:
        if format == "json":
            return JsonReportGenerator()
        # elif format == "md":
        #     return MarkdownReportGenerator()
        else:
            raise ValueError(f"Unsupported output format: {format}")

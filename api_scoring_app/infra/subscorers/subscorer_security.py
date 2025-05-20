from dataclasses import dataclass, field

from openapi_pydantic import SecurityScheme, OAuthFlows

from api_scoring_app.core import Config
from api_scoring_app.core.types import MissingFieldError
from api_scoring_app.core.parser import WrappedSecurityRequirement
from api_scoring_app.core.subscorers import ScoringReport, Issue, IssueSeverity, ParsedSpecification, BaseScorer

@dataclass
class SecuritySubscorer(BaseScorer):
    """
    Security subscorer for OpenAPI specification.
    """
    points: float
    
    _security_scheme_errors: list[MissingFieldError] = field(init=False, default_factory=list)
    _unused_security_schemes: list[WrappedSecurityRequirement] = field(init=False, default_factory=list)
    _undefined_security_schemes: list[WrappedSecurityRequirement] = field(init=False, default_factory=list)

    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        scoring_report = ScoringReport(Config.SECURITY_SUBSCORER_NAME, self.points)

        # self._recursive_security_schema_search(spec)
        self._populate_security_info(parsed_specification)

        # security schemes are not defined
        if not parsed_specification.security.defined_schemes:
            scoring_report.add_issue(
                Issue(
                    severity=IssueSeverity.CRITICAL,
                    message="Security schemes are not defined",
                    suggestion="Define at least one security scheme"
                )
            )

        # security schemes are defined, but have missing fields
        elif self._security_scheme_errors:
            issues = []
            for error in self._security_scheme_errors:
                path_as_str = " -> ".join(error.path)
                issues.append(Issue(
                    severity=IssueSeverity.ZERO,
                    message=str(error),
                    path=path_as_str,
                    suggestion="Add missing fields"
                ))
            scoring_report.bulk_add_issues(
                issues=issues,
                severity=IssueSeverity.CRITICAL
            )

        # security schemes are correctly defined, but not referenced
        issues = []
        for unused in self._unused_security_schemes:
            path_as_str = " -> ".join(unused.path)
            issues.append(Issue(
                severity=IssueSeverity.HIGH,
                message=f"Security scheme '{unused.name}' is defined, but not referenced",
                path=path_as_str,
                suggestion="Reference the defined security schemes"
            ))
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.MEDIUM
        )

        # security schemes are referenced, but not defined
        issues = []
        for undefined in self._undefined_security_schemes:
            path_as_str = " -> ".join(undefined.path)
            issues.append(Issue(
                severity=IssueSeverity.MEDIUM,
                message=f"Security scheme '{undefined.name}' is referenced, but not defined",
                path=path_as_str,
                suggestion="Define the referenced security schemes"
            ))
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.HIGH
        )

        return [scoring_report]
    
    def _populate_security_info(self, parsed_specification: ParsedSpecification) -> None:
        for path, scheme in parsed_specification.security.schemes:
            validation_errors = self._validate_security_scheme(scheme, path)
            if validation_errors:
                self._security_scheme_errors.extend(validation_errors)

        self._unused_security_schemes = [scheme for scheme in parsed_specification.security.defined_schemes if scheme not in parsed_specification.security.referenced_schemes]
        
        undefined_from_referenced = [scheme for scheme in parsed_specification.security.referenced_schemes if scheme not in parsed_specification.security.defined_schemes]
        undefined_from_operation_referenced = [scheme for scheme in parsed_specification.security.operation_referenced_schemes if scheme not in parsed_specification.security.defined_schemes]
        self._undefined_security_schemes = undefined_from_referenced + undefined_from_operation_referenced


    def _validate_security_scheme(self, scheme: SecurityScheme, path: list[str]) -> list[MissingFieldError]:
        """
        Validate a security scheme based on its type and required fields.
        """
        scheme_type = scheme.type

        missing_field_errors: list[MissingFieldError] = []

        # based on scheme type
        if scheme_type == "apiKey":
            missing_fields = []
            if not scheme.name:
                missing_fields.append("name")
            if not scheme.security_scheme_in:
                missing_fields.append("in")
            
            if missing_fields:
                missing_field_errors.append(MissingFieldError(
                    path=path,
                    parent="apiKey",
                    missing_fields=missing_fields
                ))

        elif scheme_type == "http":
            missing_fields = []
            if not scheme.scheme:
                missing_fields.append("scheme")
            
            if missing_fields:
                missing_field_errors.append(MissingFieldError(
                    path=path,
                    parent="http",
                    missing_fields=missing_fields
                ))

        elif scheme_type == "oauth2":
            if not scheme.flows:
                missing_field_errors.append(MissingFieldError(
                    path=path,
                    parent="oauth2",
                    missing_fields=["flows"]
                ))
                return missing_field_errors

            # validate flows
            flows: OAuthFlows = scheme.flows

            # for implicit flow
            if flows.implicit:
                missing_fields = []
                if not flows.implicit.authorizationUrl:
                    missing_fields.append("authorizationUrl")
                
                if not flows.implicit.scopes:
                    missing_fields.append("scopes")

                if missing_fields:
                    missing_field_errors.append(MissingFieldError(
                        path=path + ["flows", "implicit"],
                        parent="oauth2",
                        missing_fields=missing_fields
                    ))

            # for password flow
            if flows.password:
                missing_fields = []
                if not flows.password.tokenUrl:
                    missing_fields.append("tokenUrl")
                
                if not flows.password.scopes:
                    missing_fields.append("scopes")
                
                if missing_fields:
                    missing_field_errors.append(MissingFieldError(
                        path=path + ["flows", "password"],
                        parent="oauth2",
                        missing_fields=missing_fields
                    ))

            # for clientCredentials flow
            if flows.clientCredentials:
                missing_fields = []
                if not flows.clientCredentials.tokenUrl:
                    missing_fields.append("tokenUrl")
                if not flows.clientCredentials.scopes:
                    missing_fields.append("scopes")
                
                if missing_fields:
                    missing_field_errors.append(MissingFieldError(
                        path=path + ["flows", "clientCredentials"],
                        parent="oauth2",
                        missing_fields=missing_fields
                    ))

            # for authorizationCode flow
            if flows.authorizationCode:
                missing_fields = []
                if not flows.authorizationCode.authorizationUrl:
                    missing_fields.append("authorizationUrl")
                if not flows.authorizationCode.tokenUrl:
                    missing_fields.append("tokenUrl")
                if not flows.authorizationCode.scopes:
                    missing_fields.append("scopes")
                
                if missing_fields:
                    missing_field_errors.append(MissingFieldError(
                        path=path + ["flows", "authorizationCode"],
                        parent="oauth2",
                        missing_fields=missing_fields
                    ))

            # at least one flow should be defined
            if not (flows.implicit or flows.password or flows.clientCredentials or flows.authorizationCode):
                missing_field_errors.append(MissingFieldError(
                    path=path,
                    parent="oauth2",
                    missing_fields=["implicit", "password", "clientCredentials", "authorizationCode"]
                ))

        elif scheme_type == "openIdConnect":
            if not scheme.openIdConnectUrl:
                missing_field_errors.append(MissingFieldError(
                    path=path + ["openIdConnectUrl"],
                    parent="openIdConnect",
                    missing_fields=["openIdConnectUrl"]
                ))

        return missing_field_errors

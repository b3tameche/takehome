from dataclasses import dataclass, field
from typing import Any

from openapi_pydantic import OpenAPI, SecurityScheme, OAuthFlows, SecurityRequirement
from pydantic import BaseModel

from api_scoring_app.core import IScorer
from api_scoring_app.core.types import ScoringReport, Issue, IssueSeverity, WrappedSecurityRequirement, MissingFieldError

@dataclass
class SecuritySubscorer:
    """
    Security subscorer for OpenAPI specification.
    """

    subscorers: list[IScorer] = field(default_factory=list) 

    _defined_schemes: list[WrappedSecurityRequirement] = field(init=False, default_factory=list)
    _referenced_schemes: list[WrappedSecurityRequirement] = field(init=False, default_factory=list)
    _operation_referenced_schemes: list[WrappedSecurityRequirement] = field(init=False, default_factory=list)

    _security_scheme_errors: list[MissingFieldError] = field(init=False, default_factory=list)
    _unused_security_schemes: list[WrappedSecurityRequirement] = field(init=False, default_factory=list)
    _undefined_security_schemes: list[WrappedSecurityRequirement] = field(init=False, default_factory=list)

    def score_spec(self, spec: OpenAPI) -> ScoringReport:
        scoring_report = ScoringReport()

        self._recursive_security_schema_search(spec)
        self._populate_security_info()

        # security schemes are not defined
        if not self._defined_schemes:
            scoring_report.add_issue(
                Issue(
                    severity=IssueSeverity.ZERO,
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
                severity=IssueSeverity.ZERO
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
            severity=IssueSeverity.HIGH
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
            severity=IssueSeverity.MEDIUM
        )

        return scoring_report
    
    def _populate_security_info(self) -> None:
        self._unused_security_schemes = [scheme for scheme in self._defined_schemes if scheme not in self._referenced_schemes]
        
        undefined_from_referenced = [scheme for scheme in self._referenced_schemes if scheme not in self._defined_schemes]
        undefined_from_operation_referenced = [scheme for scheme in self._operation_referenced_schemes if scheme not in self._defined_schemes]
        self._undefined_security_schemes = undefined_from_referenced + undefined_from_operation_referenced
    
    def _recursive_security_schema_search(self, obj: Any, path: list[str] = []) -> None:
        if isinstance(obj, SecurityScheme):
            scheme_name = path[-1]
            self._defined_schemes.append(WrappedSecurityRequirement(scheme_name, path))

            validation_errors = self._validate_security_scheme(obj, path)
            if validation_errors:
                self._security_scheme_errors.extend(validation_errors)
        elif len(path) > 0 and obj is not None:
            if path[0] == 'security':
                referenced_schemes: list[SecurityRequirement] = obj

                for scheme in referenced_schemes:
                    scheme_name = list(scheme.keys())[0]
                    scheme_path = path + [scheme_name]
                    self._referenced_schemes.append(WrappedSecurityRequirement(scheme_name, scheme_path))

                return # stop recursion here, no need to go deeper
            elif path[-1] == 'security': # it comes from operation object
                
                referenced_schemes: list[SecurityRequirement] = obj

                for scheme in referenced_schemes:
                    scheme_name = list(scheme.keys())[0]
                    scheme_path = path + [scheme_name]
                    self._operation_referenced_schemes.append(WrappedSecurityRequirement(scheme_name, scheme_path))
                return # stop recursion here, no need to go deeper

        # recursion
        if isinstance(obj, dict): # in depth
            for key, value in obj.items():
                self._recursive_security_schema_search(value, path + [key])

        elif isinstance(obj, (list, tuple)): # in width
            for i, item in enumerate(obj):
                self._recursive_security_schema_search(item, path + [str(i)])

        elif isinstance(obj, BaseModel):
            for field_name, field_value in obj.__dict__.items():
                if not field_name.startswith('_'): # skip private fields
                    self._recursive_security_schema_search(field_value, path + [field_name])

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

    def add_subscorer(self, subscorer: IScorer) -> None:
        self.subscorers.append(subscorer)
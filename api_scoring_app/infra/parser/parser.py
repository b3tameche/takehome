from typing import Any, List
from openapi_pydantic import OpenAPI, PathItem, RequestBody, Response, SecurityRequirement, Server, Tag, MediaType, Schema, SecurityScheme
from pydantic import BaseModel
from dataclasses import dataclass, field
from api_scoring_app.core.config import Config
from api_scoring_app.core.parser import WrappedTag, WrappedSecurityRequirement, ParsedSpecification

@dataclass
class Parser:

    config: Config = field(default_factory=Config)
    parsed_specification: ParsedSpecification = field(init=False, default_factory=ParsedSpecification)

    def parse(self, obj: OpenAPI) -> ParsedSpecification:
        self._recursive_parser(obj)

        return self.parsed_specification
    
    def _recursive_parser(self, obj: Any, path: list[str] = []) -> dict:
        self._populate_description(obj, path)
        self._populate_examples(obj, path)
        self._populate_misc(obj, path)
        self._populate_response_codes(obj, path)
        self._populate_schemas(obj, path)
        
        if self._populate_security(obj, path):
            return

        # recursion
        if isinstance(obj, dict): # in depth
            for key, value in obj.items():
                self._recursive_parser(value, path + [key])

        elif isinstance(obj, (list, tuple)): # in width
            for i, item in enumerate(obj):
                self._recursive_parser(item, path + [str(i)])

        elif isinstance(obj, BaseModel):
            for field_name, field_value in obj.__dict__.items():
                if not field_name.startswith('_'): # skip private fields
                    self._recursive_parser(field_value, path + [field_name])
    

    def _populate_description(self, obj: Any, path: list[str] = []):
        if isinstance(obj, self.config.DESCRIPTION_TYPES_TO_CHECK):
            if hasattr(obj, "description"):
                if obj.description is None:
                    self.parsed_specification.descriptions.missing_descriptions.append(path)
                elif not (len(obj.description) >= self.config.DESCRIPTION_MIN_DESCRIPTION_LENGTH):
                    self.parsed_specification.descriptions.short_descriptions.append(path)
    

    def _populate_examples(self, obj: Any, path: list[str] = []):
        if len(path) > 2 and path[0] == 'paths':
            for method in self.config.EXAMPLES_MAJOR_METHODS: # examples should be defined for major methods
                if path[2] != method:
                    continue

                if (isinstance(obj, RequestBody)):
                    self.parsed_specification.examples.request_bodies.append((path, obj))
                elif (isinstance(obj, Response)):
                    self.parsed_specification.examples.responses.append((path, obj))
    

    def _populate_misc(self, obj: Any, path: list[str] = []):
        if isinstance(obj, Tag):
            self.parsed_specification.misc.tags_defined.append(WrappedTag(obj.name, path))
        elif isinstance(obj, Server):
            self.parsed_specification.misc.servers_defined.append(obj)
        elif len(path) > 0 and path[-1] == 'paths' and obj is not None:
            self.parsed_specification.misc.paths_defined.append(list(obj.keys())[0].strip('/'))
        elif len(path) > 2 and path[-1] == 'tags' and obj is not None:
            op = path[-2]
            if self._is_operation(op): # only if it's in an operation object
                for tag in obj:
                    self.parsed_specification.misc.tags_from_operations.append(WrappedTag(tag, path))


    def _populate_paths(self, obj: Any, path: list[str] = []):
        if isinstance(obj, PathItem):
            operations = self._get_operations(obj)
            self.parsed_specification.paths.path_to_operations[path[-1]] = operations


    def _populate_response_codes(self, obj: Any, path: list[str] = []):
        if len(path) > 0 and path[-1] in self.config.OPERATIONS:
            if obj is not None and obj.responses is None:
                self.parsed_specification.response_codes.missing_responses.append(path)

        if len(path) > 0 and path[0] == 'paths' and obj is not None: # response should come from path item
            if isinstance(obj, Response):
                # print(path)
                self.parsed_specification.response_codes.responses.append((path, obj))


    def _populate_schemas(self, obj: Any, path: list[str] = []):
        # check free-form schemas
        if isinstance(obj, Schema):
            if self._is_free_form_schema(obj):
                self.parsed_specification.schemas.free_form_schemas.append(path)

        # check media types with missing schemas, should cover endpoints
        elif isinstance(obj, MediaType):
            if obj.media_type_schema is None:   
                self.parsed_specification.schemas.missing_schemas.append(path)


    def _populate_security(self, obj: Any, path: list[str] = []) -> bool:
        if isinstance(obj, SecurityScheme):
            scheme_name = path[-1]
            self.parsed_specification.security.defined_schemes.append(WrappedSecurityRequirement(scheme_name, path))
            self.parsed_specification.security.schemes.append((path, obj))
        elif len(path) > 0 and obj is not None:
            if path[0] == 'security':
                referenced_schemes: list[SecurityRequirement] = obj

                for scheme in referenced_schemes:
                    scheme_name = list(scheme.keys())[0]
                    scheme_path = path + [scheme_name]
                    self.parsed_specification.security.referenced_schemes.append(WrappedSecurityRequirement(scheme_name, scheme_path))

                return True # stop recursion here, no need to go deeper
            elif path[-1] == 'security': # it comes from operation object
                
                referenced_schemes: list[SecurityRequirement] = obj

                for scheme in referenced_schemes:
                    scheme_name = list(scheme.keys())[0]
                    scheme_path = path + [scheme_name]
                    self.parsed_specification.security.operation_referenced_schemes.append(WrappedSecurityRequirement(scheme_name, scheme_path))
                return True # stop recursion here, no need to go deeper

        return False
    
    def _is_operation(self, keyword: str) -> bool:
        return keyword in self.config.OPERATIONS

    def _get_operations(self, path_item: PathItem) -> List[str]:
        return [op for op in path_item.model_fields_set if op in self.config.OPERATIONS]


    def _is_free_form_schema(self, schema: Schema) -> bool:
        condition = (schema.type == "object" and schema.additionalProperties is True) or \
            (schema.type == "object" and schema.additionalProperties is None)
        
        condition = condition and schema.properties is None

        return condition
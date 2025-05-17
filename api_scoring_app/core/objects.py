"""
Module with all the OpenAPI v3.1 objects.

TODO: Schema object is missing, 'Any' is used instead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Any, TypeAlias

@dataclass
class PathItem:
    ref: Optional[str]
    summary: Optional[str]
    description: Optional[str]
    get: Optional[Operation]
    put: Optional[Operation]
    post: Optional[Operation]
    delete: Optional[Operation]
    options: Optional[Operation]
    head: Optional[Operation]
    patch: Optional[Operation]
    trace: Optional[Operation]
    servers: Optional[List[Server]]
    parameters: Optional[List[Union[Parameter, Reference]]]

@dataclass
class License:
    name: str
    identifier: Optional[str]
    url: Optional[str]

@dataclass
class Contact:
    name: Optional[str]
    url: Optional[str]
    email: Optional[str]

@dataclass
class Info:
    title: str
    summary: Optional[str]
    description: Optional[str]
    termsOfService: Optional[str]
    contact: Optional[Contact]
    license: Optional[License]
    version: str

@dataclass
class Discriminator:
    propertyName: str
    mapping: Optional[Dict[str, str]]

@dataclass
class Xml:
    name: Optional[str]
    namespace: Optional[str]
    prefix: Optional[str]
    attribute: Optional[bool]
    wrapped: Optional[bool]

@dataclass
class Example:
    summary: Optional[str]
    description: Optional[str]
    value: Optional[Any]
    externalValue: Optional[str]

@dataclass
class Reference:
    ref: str
    summary: Optional[str]
    description: Optional[str]

@dataclass
class Encoding:
    contentType: Optional[str]
    headers: Optional[Dict[str, Union[Header, Reference]]]
    style: Optional[str]
    explode: Optional[bool]
    allowReserved: Optional[bool]

@dataclass
class MediaType:
    schema: Optional[Any]
    example: Optional[Example]
    examples: Optional[Dict[str, Union[Example, Reference]]]
    encoding: Optional[Dict[str, Encoding]]

@dataclass
class Header:
    description: Optional[str]
    required: Optional[bool]
    deprecated: Optional[bool]
    allowEmptyValue: Optional[bool]
    style: Optional[str]
    explode: Optional[bool]
    allowReserved: Optional[bool]
    schema: Optional[Any]
    example: Optional[Any]
    examples: Optional[Dict[str, Union[Example, Reference]]]
    content: Optional[Dict[str, MediaType]]

@dataclass
class Parameter:
    name: str
    in_: str
    description: Optional[str]
    required: Optional[bool]
    deprecated: Optional[bool]
    allowEmptyValue: Optional[bool]
    style: Optional[str]
    explode: Optional[bool]
    allowReserved: Optional[bool]
    schema: Optional[Any]
    example: Optional[Optional[Any]]
    examples: Optional[Optional[Dict[str, Union[Example, Reference]]]]
    content: Optional[Optional[Dict[str, MediaType]]]

@dataclass
class RequestBody:
    description: Optional[str]
    content: Dict[str, MediaType]
    required: Optional[bool]

@dataclass
class Link:
    operationRef: Optional[str]
    operationId: Optional[str]
    parameters: Optional[Dict[str, Any]]
    requestBody: Optional[Any]
    description: Optional[str]
    server: Optional[Server]

@dataclass
class Response:
    description: str
    headers: Optional[Dict[str, Union[Header, Reference]]]
    content: Optional[Dict[str, MediaType]]
    links: Optional[Dict[str, Union[Link, Reference]]]

Callback: TypeAlias = Dict[str, Union[PathItem, Reference]]
SecurityRequirement: TypeAlias = Dict[str, List[str]]

@dataclass
class Operation:
    tags: Optional[List[str]]
    summary: Optional[str]
    description: Optional[str]
    # externalDocs
    operationId: Optional[str]
    parameters: Optional[List[Union[Parameter, Reference]]]
    requestBody: Optional[Union[RequestBody, Reference]]
    responses: Optional[List[Union[Response, Reference]]]
    callbacks: Optional[Dict[str, Union[Callback, Reference]]]
    deprecated: Optional[bool]
    security: Optional[List[SecurityRequirement]]
    servers: Optional[List[Server]]

@dataclass
class ServerVariable:
    enum: Optional[List[str]]
    default: str
    description: Optional[str]

@dataclass
class Server:
    url: str
    description: Optional[str]
    variables: Optional[Dict[str, ServerVariable]]

@dataclass
class OAuthFlow:
    authorizationUrl: str
    tokenUrl: str
    refreshUrl: Optional[str]
    scopes: Dict[str, str]

@dataclass
class OAuthFlows:
    implicit: Optional[OAuthFlow]
    password: Optional[OAuthFlow]
    clientCredentials: Optional[OAuthFlow]
    authorizationCode: Optional[OAuthFlow]

@dataclass
class SecurityScheme:
    type: str
    description: Optional[str]
    name: str
    in_: str
    scheme: str
    bearerFormat: Optional[str]
    flows: OAuthFlows
    openIdConnectUrl: str

@dataclass
class Components:
    schemas: Optional[Dict[str, Any]]
    responses: Optional[Dict[str, Union[Response, Reference]]]
    parameters: Optional[Dict[str, Union[Parameter, Reference]]]
    examples: Optional[Dict[str, Union[Example, Reference]]]
    requestBodies: Optional[Dict[str, Union[RequestBody, Reference]]]
    headers: Optional[Dict[str, Union[Header, Reference]]]
    securitySchemes: Optional[Dict[str, Union[SecurityScheme, Reference]]]
    links: Optional[Dict[str, Union[Link, Reference]]]
    callbacks: Optional[Dict[str, Union[Callback, Reference]]]
    pathItems: Optional[Dict[str, Union[PathItem, Reference]]]

Paths: TypeAlias = Dict[str, PathItem]

@dataclass
class ExternalDocumentation:
    description: Optional[str]
    url: str

@dataclass
class Tag:
    name: str
    description: Optional[str]
    externalDocs: Optional[ExternalDocumentation]

@dataclass
class Root:
    openapi: str
    info: Info
    # jsonSchemaDialect
    servers: Optional[List[Server]]
    paths: Optional[Paths]
    webhooks: Optional[Dict[str, Union[PathItem, Reference]]]
    components: Optional[Components]
    security: Optional[List[SecurityRequirement]]
    tags: Optional[List[Tag]]
    externalDocs: Optional[ExternalDocumentation]

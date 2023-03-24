# coding: utf-8

"""
    DJ server

    A DataJunction metrics layer  # noqa: E501

    The version of the OpenAPI document: 0.0.post1.dev1+g9dc3258
    Generated by: https://openapi-generator.tech
"""

from datetime import date, datetime  # noqa: F401
import decimal  # noqa: F401
import functools  # noqa: F401
import io  # noqa: F401
import re  # noqa: F401
import typing  # noqa: F401
import typing_extensions  # noqa: F401
import uuid  # noqa: F401

import frozendict  # noqa: F401

from djopenapi import schemas  # noqa: F401


class Column(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    A column.

Columns can be physical (associated with ``Table`` objects) or abstract (associated
with ``Node`` objects).
    """


    class MetaOapg:
        required = {
            "name",
            "type",
        }
        
        class properties:
            name = schemas.StrSchema
            type = schemas.StrSchema
            id = schemas.IntSchema
            dimension_id = schemas.IntSchema
            dimension_column = schemas.StrSchema
            __annotations__ = {
                "name": name,
                "type": type,
                "id": id,
                "dimension_id": dimension_id,
                "dimension_column": dimension_column,
            }
    
    name: MetaOapg.properties.name
    type: MetaOapg.properties.type
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["name"]) -> MetaOapg.properties.name: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["type"]) -> MetaOapg.properties.type: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["id"]) -> MetaOapg.properties.id: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["dimension_id"]) -> MetaOapg.properties.dimension_id: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["dimension_column"]) -> MetaOapg.properties.dimension_column: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["name", "type", "id", "dimension_id", "dimension_column", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["name"]) -> MetaOapg.properties.name: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["type"]) -> MetaOapg.properties.type: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["id"]) -> typing.Union[MetaOapg.properties.id, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["dimension_id"]) -> typing.Union[MetaOapg.properties.dimension_id, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["dimension_column"]) -> typing.Union[MetaOapg.properties.dimension_column, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["name", "type", "id", "dimension_id", "dimension_column", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        name: typing.Union[MetaOapg.properties.name, str, ],
        type: typing.Union[MetaOapg.properties.type, str, ],
        id: typing.Union[MetaOapg.properties.id, decimal.Decimal, int, schemas.Unset] = schemas.unset,
        dimension_id: typing.Union[MetaOapg.properties.dimension_id, decimal.Decimal, int, schemas.Unset] = schemas.unset,
        dimension_column: typing.Union[MetaOapg.properties.dimension_column, str, schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'Column':
        return super().__new__(
            cls,
            *_args,
            name=name,
            type=type,
            id=id,
            dimension_id=dimension_id,
            dimension_column=dimension_column,
            _configuration=_configuration,
            **kwargs,
        )
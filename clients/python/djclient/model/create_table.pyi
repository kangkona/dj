# coding: utf-8

"""
    DJ server

    A DataJunction metrics layer  # noqa: E501

    The version of the OpenAPI document: 0.0.post1.dev1+ge24d408
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

from djclient import schemas  # noqa: F401


class CreateTable(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    Create table input
    """


    class MetaOapg:
        required = {
            "catalog_name",
            "database_name",
            "columns",
            "table",
        }
        
        class properties:
            table = schemas.StrSchema
            database_name = schemas.StrSchema
            catalog_name = schemas.StrSchema
            
            
            class columns(
                schemas.ListSchema
            ):
            
            
                class MetaOapg:
                    
                    @staticmethod
                    def items() -> typing.Type['CreateColumn']:
                        return CreateColumn
            
                def __new__(
                    cls,
                    _arg: typing.Union[typing.Tuple['CreateColumn'], typing.List['CreateColumn']],
                    _configuration: typing.Optional[schemas.Configuration] = None,
                ) -> 'columns':
                    return super().__new__(
                        cls,
                        _arg,
                        _configuration=_configuration,
                    )
            
                def __getitem__(self, i: int) -> 'CreateColumn':
                    return super().__getitem__(i)
            schema = schemas.StrSchema
            cost = schemas.NumberSchema
            __annotations__ = {
                "table": table,
                "database_name": database_name,
                "catalog_name": catalog_name,
                "columns": columns,
                "schema": schema,
                "cost": cost,
            }
    
    catalog_name: MetaOapg.properties.catalog_name
    database_name: MetaOapg.properties.database_name
    columns: MetaOapg.properties.columns
    table: MetaOapg.properties.table
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["table"]) -> MetaOapg.properties.table: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["database_name"]) -> MetaOapg.properties.database_name: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["catalog_name"]) -> MetaOapg.properties.catalog_name: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["columns"]) -> MetaOapg.properties.columns: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["schema"]) -> MetaOapg.properties.schema: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["cost"]) -> MetaOapg.properties.cost: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["table", "database_name", "catalog_name", "columns", "schema", "cost", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["table"]) -> MetaOapg.properties.table: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["database_name"]) -> MetaOapg.properties.database_name: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["catalog_name"]) -> MetaOapg.properties.catalog_name: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["columns"]) -> MetaOapg.properties.columns: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["schema"]) -> typing.Union[MetaOapg.properties.schema, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["cost"]) -> typing.Union[MetaOapg.properties.cost, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["table", "database_name", "catalog_name", "columns", "schema", "cost", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        catalog_name: typing.Union[MetaOapg.properties.catalog_name, str, ],
        database_name: typing.Union[MetaOapg.properties.database_name, str, ],
        columns: typing.Union[MetaOapg.properties.columns, list, tuple, ],
        table: typing.Union[MetaOapg.properties.table, str, ],
        schema: typing.Union[MetaOapg.properties.schema, str, schemas.Unset] = schemas.unset,
        cost: typing.Union[MetaOapg.properties.cost, decimal.Decimal, int, float, schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'CreateTable':
        return super().__new__(
            cls,
            *_args,
            catalog_name=catalog_name,
            database_name=database_name,
            columns=columns,
            table=table,
            schema=schema,
            cost=cost,
            _configuration=_configuration,
            **kwargs,
        )

from djclient.model.create_column import CreateColumn

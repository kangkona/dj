from typing import List

import strawberry
from fastapi import Depends
from strawberry.fastapi import GraphQLRouter

from dj.api.graphql.database import Database, get_databases
from dj.api.graphql.metric import (
    Metric,
    TranslatedSQL,
    read_metric,
    read_metrics,
    read_metrics_data,
    read_metrics_sql,
)
from dj.api.graphql.node import Node, get_nodes
from dj.api.graphql.query import QueryWithResults, submit_query
from dj.utils import get_session, get_settings


async def get_context(session=Depends(get_session), settings=Depends(get_settings)):
    return {"session": session, "settings": settings}


@strawberry.type
class Query:
    get_databases: List[Database] = strawberry.field(resolver=get_databases)
    get_nodes: List[Node] = strawberry.field(resolver=get_nodes)
    read_metrics: List[Metric] = strawberry.field(resolver=read_metrics)
    read_metric: Metric = strawberry.field(resolver=read_metric)
    read_metrics_data: QueryWithResults = strawberry.field(resolver=read_metrics_data)
    read_metrics_sql: TranslatedSQL = strawberry.field(resolver=read_metrics_sql)


@strawberry.type
class Mutation:
    submit_query: QueryWithResults = strawberry.mutation(resolver=submit_query)


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema, context_getter=get_context)
"""
Cube materialization jobs
"""
from typing import Dict

from dj.materialization.jobs.materialization_job import MaterializationJob
from dj.models.engine import Dialect
from dj.models.node import DruidCubeConfig, MaterializationConfig
from dj.service_clients import QueryServiceClient

DRUID_AGG_MAPPING = {
    ("bigint", "sum"): "longSum",
    ("double", "sum"): "doubleSum",
    ("float", "sum"): "floatSum",
    ("double", "min"): "doubleMin",
    ("double", "max"): "doubleMax",
    ("float", "min"): "floatMin",
    ("float", "max"): "floatMax",
    ("bigint", "min"): "longMin",
    ("bigint", "max"): "longMax",
    ("bigint", "count"): "longSum",
    ("double", "count"): "longSum",
    ("float", "count"): "longSum",
}


class DefaultCubeMaterialization(
    MaterializationJob,
):  # pylint: disable=too-few-public-methods
    """
    Dummy job that is not meant to be executed but contains all the
    settings needed for to materialize a generic cube.
    """

    def schedule(
        self,
        materialization: MaterializationConfig,
        query_service_client: QueryServiceClient,
    ):
        """
        Since this is a settings-only dummy job, we do nothing in this stage.
        """
        return


class DruidCubeMaterializationJob(MaterializationJob):
    """
    Druid materialization for a cube node.
    """

    dialect = Dialect.DRUID

    def build_druid_spec(self, cube_config: DruidCubeConfig, node_name: str) -> Dict:
        """
        Builds the Druid ingestion spec from a materialization config.
        """
        druid_datasource_name = (
            cube_config.prefix  # type: ignore
            + node_name.replace(".", "_DOT_")  # type: ignore
            + cube_config.suffix  # type: ignore
        )
        _metrics_spec = [
            {
                "fieldName": measure["name"],
                "name": measure["name"],
                "type": DRUID_AGG_MAPPING[
                    (measure["type"].lower(), measure["agg"].lower())
                ],
            }
            for measure_group in cube_config.measures.values()  # type: ignore
            for measure in measure_group
        ]
        metrics_spec = [
            dict(tup) for tup in {tuple(spec.items()) for spec in _metrics_spec}
        ]
        druid_spec = {
            "dataSchema": {
                "dataSource": druid_datasource_name,
                "parser": {
                    "parseSpec": {
                        "format": cube_config.druid.parse_spec_format or "parquet",  # type: ignore
                        "dimensionsSpec": {"dimensions": cube_config.dimensions},
                        "timestampSpec": {
                            "column": cube_config.druid.timestamp_column,  # type: ignore
                            "format": (
                                cube_config.druid.timestamp_format  # type: ignore
                                or "yyyyMMdd"
                            ),
                        },
                    },
                },
                "metricsSpec": metrics_spec,
                "granularitySpec": {
                    "type": "uniform",
                    "segmentGranularity": cube_config.druid.granularity,  # type: ignore
                    "intervals": cube_config.druid.intervals,  # type: ignore
                },
            },
        }
        return druid_spec

    def schedule(
        self,
        materialization: MaterializationConfig,
        query_service_client: QueryServiceClient,
    ):
        """
        Use the query service to kick off the materialization setup.
        """
        cube_config = DruidCubeConfig.parse_obj(materialization.config)
        druid_spec = self.build_druid_spec(
            cube_config,
            materialization.node_revision.name,
        )
        query_service_client.materialize_cube(
            node_name=materialization.node_revision.name,
            node_type=materialization.node_revision.type,
            schedule=materialization.schedule,
            query=cube_config.query,
            spark_conf=cube_config.spark.__root__,
            druid_spec=druid_spec,
        )
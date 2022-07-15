"""FastVector App - Utilities"""
import os
import json
from fastapi import FastAPI
from pygeofilter.backends.sql import to_sql_where
from pygeofilter.parsers.ecql import parse

import config

async def get_tables_metadata(request) -> list:
    """
    Method used to get tables metadata.
    """
    tables_metadata = []

    url = str(request.base_url)

    for database in config.DATABASES.items():

        pool = request.app.state.databases[f'{database[0]}_pool']

        async with pool.acquire() as con:
            tables_query = """
            SELECT schemaname, tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname not in ('pg_catalog','information_schema', 'topology')
            AND tablename != 'spatial_ref_sys'; 
            """
            tables = await con.fetch(tables_query)
            for table in tables:
                tables_metadata.append(
                    {
                        "id" : f"{database[0]}.{table['schemaname']}.{table['tablename']}",
                        "title" : table['tablename'],
                        "description" : table['tablename'],
                        "keywords": [table['tablename']],
                        "links":[
                            {
                                "type": "application/json",
                                "rel": "self",
                                "title": "This document as JSON",
                                "href": f"{url}api/v1/collections/{database[0]}.{table['schemaname']}.{table['tablename']}"
                            }
                        ],
                        "extent": {
                            "spatial": {
                                "bbox": await get_table_bounds(
                                    database=database[0],
                                    scheme=table['schemaname'],
                                    table=table['tablename'],
                                    app=request.app
                                ),
                                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                            }
                        },
                        "itemType": "feature"
                    }
                )

    return tables_metadata

async def get_table_columns(database: str, scheme: str, table: str, app: FastAPI) -> list:
    """
    Method used to retrieve columns for a given table.
    """

    pool = app.state.databases[f'{database}_pool']

    async with pool.acquire() as con:
        column_query = f"""
        SELECT
            jsonb_agg(
                jsonb_build_object(
                    'name', attname,
                    'type', format_type(atttypid, null),
                    'description', col_description(attrelid, attnum)
                )
            )
        FROM pg_attribute
        WHERE attnum>0
        AND attrelid=format('%I.%I', '{scheme}', '{table}')::regclass
        """
        columns = await con.fetchval(column_query)

        return json.loads(columns)

async def get_table_geojson(database: str, scheme: str, table: str, app: FastAPI) -> list:
    """
    Method used to retrieve the table geojson.

    """

    pool = app.state.databases[f'{database}_pool']

    async with pool.acquire() as con:
        query = f"""
        SELECT
        json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(ST_AsGeoJSON(t.*)::json)
        )
        FROM (
            SELECT *
            FROM {scheme}.{table}
        ) AS t;
        """
        geojson = await con.fetchrow(query)
        
        return json.loads(geojson['json_build_object'])

async def get_table_bounds(database: str, scheme: str, table: str, app: FastAPI) -> list:
    """
    Method used to retrieve the bounds for a given table.
    """

    pool = app.state.databases[f'{database}_pool']

    async with pool.acquire() as con:
        query = f"""
        SELECT ARRAY[
            ST_XMin(ST_Union(geom)),
            ST_YMin(ST_Union(geom)),
            ST_XMax(ST_Union(geom)),
            ST_YMax(ST_Union(geom))
        ]
        FROM {scheme}.{table}
        """
        # extent = await con.fetchval(query)

        extent = [
            -180,
            -90,
            180,
            90
        ]

        return extent

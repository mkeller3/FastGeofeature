from fastapi import Request, APIRouter
from pygeofilter.backends.sql import to_sql_where
from pygeofilter.parsers.ecql import parse

import utilities

router = APIRouter()

@router.get("/", tags=["Collections"])
async def tables(request: Request):
    """
    Method used to return a list of tables available to query.

    """

    db_tables = await utilities.get_tables_metadata(request)

    return db_tables

@router.get("/{database}.{scheme}.{table}", tags=["Collections"])
async def tables(database: str, scheme: str, table: str, request: Request):
    """
    Method used to return information about a collection.

    """

    url = str(request.base_url)

    return {
        "id": f"{database}.{scheme}.{table}",
        "title": f"{database}.{scheme}.{table}",
        "description": f"{database}.{scheme}.{table}",
        "keywords": [f"{database}.{scheme}.{table}"],
        "links": [
            {
                "type": "application/json",
                "rel": "self",
                "title": "Items as GeoJSON",
                "href": f"{url}api/v1/collections/{database}.{scheme}.{table}/items"
            }
        ],
        "extent": {
            "spatial": {
                "bbox": await utilities.get_table_bounds(
                    database=database,
                    scheme=scheme,
                    table=table,
                    app=request.app
                ),
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            }
        },
        "itemType": "feature"
    }

@router.get("/{database}.{scheme}.{table}/items", tags=["Collections"])
async def tables(database: str, scheme: str, table: str, request: Request,
    bbox: str, limit: int=200000, offset: int=0, properties: str="*",
    sortby :str="gid", filter :str=None):
    """
    Method used to return geojson from a collection.

    """

    blacklist_query_parameters = ["bbox","limit","offset","properties","sortby","filter"]

    new_query_parameters = []

    for query in request.query_params:
        if query not in blacklist_query_parameters:
            new_query_parameters.append(query)

    column_where_parameters = ""

    if new_query_parameters != []:
        pool = request.app.state.databases[f'{database}_pool']

        async with pool.acquire() as con:


            sql_field_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table}'
            AND column_name != 'geom';
            """

            db_fields = await con.fetch(sql_field_query)

            for field in db_fields:
                if field['column_name'] in new_query_parameters:
                    if len(column_where_parameters) != 0:
                        column_where_parameters += " AND "
                    column_where_parameters += f" {field['column_name']} = '{request.query_params[field['column_name']]}' "

    if filter is not None:
        pool = request.app.state.databases[f'{database}_pool']

        async with pool.acquire() as con:

            sql_field_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table}'
            AND column_name != 'geom';
            """

            field_mapping = {}

            db_fields = await con.fetch(sql_field_query)

            for field in db_fields:
                field_mapping[field['column_name']] = field['column_name']

            ast = parse(filter)
            filter = to_sql_where(ast, field_mapping)
    
    if filter is not None:
        filter += f" AND {column_where_parameters}"
    else:
        filter = column_where_parameters
    
    results = await utilities.get_table_geojson(
        database=database,
        scheme=scheme,
        table=table,
        limit=limit,
        offset=offset,
        properties=properties,
        sort_by=sortby,
        bbox=bbox,
        filter=filter,
        app=request.app
    )

    return results

@router.get("/{database}.{scheme}.{table}/items/{id}", tags=["Collections"])
async def tables(database: str, scheme: str, table: str, id:str, request: Request, properties: str="*",):
    """
    Method used to return geojson for one item of a collection.

    """

    results = await utilities.get_table_geojson(
        database=database,
        scheme=scheme,
        table=table,
        where_parameter=f"gid = '{id}'",
        properties=properties,
        app=request.app
    )

    return results

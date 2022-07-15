from fastapi import Request, APIRouter

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
async def tables(database: str, scheme: str, table: str, request: Request):
    """
    Method used to return information about a collection.
    """

    results = await utilities.get_table_geojson(
        database=database,
        scheme=scheme,
        table=table,
        app=request.app
    )

    return results
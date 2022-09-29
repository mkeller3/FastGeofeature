
"""FastGeofeature App"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from db import close_db_connection, connect_to_db
from routers import collections


DESCRIPTION = """
A lightweight python api to serve an OGC Features API.
"""

app = FastAPI(
    title="FastGeofeature",
    description=DESCRIPTION,
    version="0.0.1",
    contact={
        "name": "Michael Keller",
        "email": "michaelkeller03@gmail.com",
    },
    license_info={
        "name": "The MIT License (MIT)",
        "url": "https://mit-license.org/",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    collections.router,
    prefix="/api/v1/collections",
    tags=["Collections"],
)

Instrumentator().instrument(app).expose(app)


# Register Start/Stop application event handler to setup/stop the database connection
@app.on_event("startup")
async def startup_event():
    """Application startup: register the database connection and create table list."""
    await connect_to_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: de-register the database connection."""
    await close_db_connection(app)

@app.get("/api/v1/", tags=["Land Page"])
async def landing_page(request: Request):
    """
    Method to show landing page.
    """

    url = str(request.base_url)

    return {
        "links": [
            {
                "rel": "self",
                "type": "application/json",
                "title": "This document as JSON",
                "href": f"{url}api/v1/"
            },
            {
                "rel": "conformance",
                "type": "application/json",
                "title": "Conformance",
                "href": f"{url}api/v1/conformance"
            },
            {
                "rel": "data",
                "type": "application/json",
                "title": "Collections",
                "href": f"{url}api/v1/collections"
            },
            {
                "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0",
                "title": "The OpenAPI definition as JSON",
                "href": f"{url}openapi.json"
            }
        ],
        "title": "OGC Feature API",
        "description": "An example api"
    }

@app.get("/api/v1/conformance", tags=["Conformance"])
async def conformance(request: Request):
    """
    Method to show conformance
    """

    url = str(request.base_url)

    return {
        "conformsTo": [
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"
        ]
    }

@app.get("/api/v1/health_check", tags=["Health"])
async def health():
    """
    Method used to verify server is healthy.
    """

    return {"status": "UP"}

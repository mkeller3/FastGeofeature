# FastGeofeature

FastGeofeature is a geospatial api to serve features from a mulititude of [PostGIS](https://github.com/postgis/postgis) enabled databases. FastGeofeature is written in [Python](https://www.python.org/) using the [FastAPI](https://fastapi.tiangolo.com/) web framework. 

---

**Source Code**: <a href="https://github.com/mkeller3/FastGeofeature" target="_blank">https://github.com/mkeller3/FastGeofeature</a>

---

## Requirements

FastGeofeature requires PostGIS >= 2.4.0.

## Configuration

In order for the api to work you will need to edit the `config.py` file with your database connections.

Example
```python
DATABASES = {
    "data": {
        "host": "localhost", # Hostname of the server
        "database": "data", # Name of the database
        "username": "postgres", # Name of the user, ideally only SELECT rights
        "password": "postgres", # Password of the user
        "port": 5432, # Port number for PostgreSQL
    }
}
```

## Usage

### Running Locally

To run the app locally `uvicorn main:app --reload`

### Production
Build Dockerfile into a docker image to deploy to the cloud.

## API

| Method | URL                                                                              | Description                                             |
| ------ | -------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `GET`  | `/api/v1/collections/collections.json`                                           | [Collections](#collections)               |
| `GET`  | `/api/v1/collections/{name}.json`                                                | [Feature Collection](#feature-collection)         |
| `GET`  | `/api/v1/collections/{name}/items.json`                                          | [Features](#features)    |
| `GET`  | `/api/v1/collections/{name}/items/{id}.json`                                     | [Feature](#feature) |
| `GET`  | `/api/v1/health_check`                                                           | Server health check: returns `200 OK`            |



## Collections

## Feature Collection

## Features

## Feature

# NYU DevOps Project - Products Service

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Overview

The Products service is a RESTful microservice for an eCommerce application. It manages the items a customer can buy, and supports Create, Read, Update, Delete, and List (CRUD + L) operations. All responses, including errors, are returned as JSON.

## Setup

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Visual Studio Code](https://code.visualstudio.com/) with the **Dev Containers** extension

### Running the service locally
1. Clone the repository:
```bash
   git clone https://github.com/CSCI-GA-2820-FA26-003/products.git
   cd products
   code .
```
2. When VS Code opens, click **Reopen in Container**. This starts the app and a PostgreSQL database.
3. Create the database tables:
```bash
   flask db-create
```
4. Start the service:
```bash
   honcho start
```
5. Open http://localhost:8080 in your browser.

## Running Tests

Run the linter (PEP8 checks):
```bash
make lint
```

Run the unit tests with coverage (minimum 95%):
```bash
make test
```

## API Endpoints

| Method | URL | Description | Success Code | Error Codes |
|--------|-----|-------------|--------------|-------------|
| GET | `/` | Returns service name, version, and list URL | 200 OK | — |
| POST | `/products` | Creates a new product | 201 Created | 400 Bad Request, 415 Unsupported Media Type |
| GET | `/products` | Lists all products | 200 OK | — |
| GET | `/products/{id}` | Reads a single product | 200 OK | 404 Not Found |
| PUT | `/products/{id}` | Updates an existing product | 200 OK | 400 Bad Request, 404 Not Found, 415 Unsupported Media Type |
| DELETE | `/products/{id}` | Deletes a product | 204 No Content | 404 Not Found |

### Example: Create a product
Request:
```bash
curl -X POST http://localhost:8080/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Blue Shirt", "description": "Cotton t-shirt", "category": "Clothing", "price": "19.99", "stock": 10}'
```
Response (`201 Created`, with a `Location` header pointing to the new product):
```json
{
  "id": 1,
  "name": "Blue Shirt",
  "description": "Cotton t-shirt",
  "category": "Clothing",
  "price": "19.99",
  "stock": 10,
  "image_url": null,
  "created_at": "2026-10-19T12:00:00",
  "updated_at": "2026-10-19T12:00:00"
}
```

## Product Model

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | Integer | Auto | Assigned by the database |
| name | String (63) | Yes | Cannot be empty |
| description | String (256) | No | |
| category | String (63) | No | |
| price | Decimal (Numeric) | No | Stored as Numeric, not Float; cannot be negative |
| stock | Integer | No | Cannot be negative |
| image_url | String (512) | No | |
| created_at | DateTime | Auto | Set when the product is created |
| updated_at | DateTime | Auto | Updated on every change |

## Project Structure

```text
service/                - service Python package
├── __init__.py         - package initializer
├── config.py           - configuration parameters
├── models.py           - Product model
├── routes.py           - REST API routes
└── common/             - common code (error handlers, logging, status codes)

tests/                  - test cases package
├── factories.py        - factory for generating fake products
├── test_models.py      - test suite for the Product model
└── test_routes.py      - test suite for the REST API routes
```

## License

Copyright (c) 2016, 2026 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
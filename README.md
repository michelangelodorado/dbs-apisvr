# dbs-apisvr

A lightweight Database Access Authorization API server built with Flask. It validates whether a user has permission to perform database operations for a given department, checking user identity, access type, and returning the allowed time window and target systems.

## How It Works

Authorization policies are defined in `db.json`. Each entry specifies:

- **DEPNO** - Department number
- **allowed_users** - Users authorized for that department
- **allowed_types** - Permitted access levels (`L1_RO`, `L2_RW`, `L3_FULL`)
- **time_range** - Valid access window (ISO 8601 start/end)
- **allowed_systems** - Target systems (IP and port) the user may access

When a request hits the `/check` endpoint, the server validates the user and access type against the department's policy and returns the associated time range and allowed systems on success.

## Quick Start

### Local

```bash
pip install -r requirements.txt
python app.py
```

The server starts on `http://localhost:8080`.

### Docker

```bash
docker build -t dbs-apisvr .
docker run -p 8080:8080 dbs-apisvr
```

## API

### `GET /check`

Validates a user's authorization for a department.

**Query Parameters**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `DEPNO`   | Yes      | Department number |
| `TYPE`    | Yes      | Access type (`L1_RO`, `L2_RW`, `L3_FULL`) |
| `USER`    | Yes      | Username |

**Example**

```bash
curl "http://localhost:8080/check?DEPNO=644687&TYPE=L1_RO&USER=nw.mike_d"
```

**Success Response** `200`

```json
{
  "status": "valid",
  "DEPNO": "644687",
  "TYPE": "L1_RO",
  "USER": "nw.mike_d",
  "time_range": {
    "start": "2026-03-20T06:00:00Z",
    "end": "2026-03-22T06:00:00Z"
  },
  "allowed_systems": [
    { "ip": "10.1.10.5", "port": 80 },
    { "ip": "10.1.10.8", "port": 80 },
    { "ip": "10.1.10.9", "port": 80 }
  ]
}
```

**Invalid Response** `200`

```json
{ "status": "not-valid", "reason": "DEPNO not found" }
{ "status": "not-valid", "reason": "user not authorized" }
{ "status": "not-valid", "reason": "type not permitted" }
```

**Error Response** `400`

Returned when one or more required parameters are missing.

```json
{ "status": "error", "message": "Missing required parameters: DEPNO, TYPE, USER" }
```

### `GET /health`

Health check endpoint.

```bash
curl http://localhost:8080/health
```

```json
{ "status": "healthy" }
```

## Access Types

| Type | Description |
|------|-------------|
| `L1_RO` | Read-only access |
| `L2_RW` | Read-write access |
| `L3_FULL` | Full access |

## Configuration

Authorization policies are stored in `db.json`. Add, remove, or modify entries to control access. Each entry follows this structure:

```json
{
  "DEPNO": "644687",
  "allowed_users": ["nw.jeffrey_d", "nw.james_d", "nw.mike_d"],
  "allowed_types": ["L1_RO", "L2_RW"],
  "time_range": {
    "start": "2026-03-20T06:00:00Z",
    "end": "2026-03-22T06:00:00Z"
  },
  "allowed_systems": [
    { "ip": "10.1.10.5", "port": 80 },
    { "ip": "10.1.10.8", "port": 80 }
  ]
}
```

> **Note:** `db.json` is loaded once at startup. Restart the server after making changes.

## Project Structure

```
dbs-apisvr/
├── app.py              # Flask application
├── db.json             # Authorization policy database
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container image definition
└── README.md
```

## Tech Stack

- **Python 3.12**
- **Flask 3.1.0**
- **Gunicorn 23.0.0** (production WSGI server)
- **Docker** (python:3.12-slim base image)

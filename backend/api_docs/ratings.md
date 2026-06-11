# Ratings

## Purpose

Allow patients to rate completed care requests and allow patients, nurses, and authorized admins to view ratings within their role boundary.

## Endpoint URL

`/api/ratings/`

## HTTP Method

`GET`, `POST`

## Authentication

JWT bearer token required.

## Permissions

- `GET`: patient sees own submitted ratings, nurse sees ratings received, authorized admin sees all.
- `POST`: patient only.

## Request Schema

`GET` has no request body.

`POST`:

```json
{
  "care_request_id": 42,
  "rating": 5,
  "comment": "Professional and punctual"
}
```

## Response Schema

```json
[
  {
    "id": 1,
    "patient_id": 3,
    "nurse_id": 8,
    "nurse_name": "Jane Wanjiku",
    "care_request_id": 42,
    "rating": 5,
    "comment": "Professional and punctual",
    "created_at": "2026-06-11T10:00:00Z",
    "updated_at": "2026-06-11T10:00:00Z"
  }
]
```

## Error Responses

- `400` when the request is incomplete, already rated, or the rating is outside 1-5.
- `401` when the JWT is missing or invalid.
- `403` when a non-patient attempts to create a rating or a patient rates another patient's request.

## Business Rules

- Only completed requests can be rated.
- A care request can have only one active rating.
- Rating creation updates the nurse average rating and reputation score.
- Rating creation emits an audit log.

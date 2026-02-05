# API Specification

Base URL: `/api/v1`

All list endpoints support pagination with:
- `page` (default 1)
- `per_page` (default 10, max 100)

## Health
`GET /health`

Response:
```
{ "status": "ok" }
```

## Perkara
`GET /perkara`

`GET /perkara/{id}`

Example list response:
```
{
  "page": 1,
  "per_page": 10,
  "total": 25,
  "pages": 3,
  "items": [
    {
      "id": 1,
      "no_perkara": "10/Pdt.G/2025/PA.IKN",
      "nama_suami": "Nama Suami",
      "nama_istri": "Nama Istri",
      "status": "Terdaftar",
      "tanggal_sidang": "2025-12-04"
    }
  ]
}
```

## Pegawai
`GET /pegawai`

Returns:
- `id`, `username`, `role`, `nama_lengkap`, `nip`, `pas_foto`, `pdf_sk_pns`

## Laporan Tamu
`GET /laporan`

## Berita
`GET /berita`

## Galeri
`GET /galeri`

## Diskusi Internal
`GET /diskusi`

## Data Integrity & Concepts
- **Soft Delete**: Deleting resources (Perkara, Users, etc.) does not permanently remove them from the database. Instead, the `is_deleted` flag is set to `1`.
- **UUIDs**: All resource IDs are UUID strings, not integers.

## API Documentation (Swagger)
The system provides two interactive API documentation interfaces:

### 1. Core Application API
Interact with the main application endpoints (Public, Dashboard, Admin).
- **UI**: `/docs` (Recommended)
- **JSON Spec**: `/spec`

### 2. Dedicated Rest-API Blueprint
For the specific `api` blueprint endpoints.
- **UI**: `/docs/swagger-ui`
- **JSON Spec**: `/docs/openapi.json`

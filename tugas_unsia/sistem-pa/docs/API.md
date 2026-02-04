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

## Swagger UI
Open Swagger UI at:
- `/docs/swagger-ui`

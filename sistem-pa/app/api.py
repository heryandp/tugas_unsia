import math

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields

from .db import get_db


class PaginationArgsSchema(Schema):
    page = fields.Int(load_default=1, metadata={"description": "Page number (1-based)."})
    per_page = fields.Int(load_default=10, metadata={"description": "Items per page."})


class PerkaraSchema(Schema):
    id = fields.Int()
    no_perkara = fields.Str()
    nama_suami = fields.Str()
    nama_istri = fields.Str()
    keluhan = fields.Str(allow_none=True)
    tanggal_daftar = fields.Str(allow_none=True)
    nama_staff = fields.Str(allow_none=True)
    file_suami = fields.Str(allow_none=True)
    file_istri = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    biaya_daftar = fields.Str(allow_none=True)
    hasil_mediasi = fields.Str(allow_none=True)
    detail_mediasi = fields.Str(allow_none=True)
    nama_mediator = fields.Str(allow_none=True)
    tanggal_sidang = fields.Str(allow_none=True)
    no_akta_cerai = fields.Str(allow_none=True)


class PegawaiSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    role = fields.Str()
    nama_lengkap = fields.Str()
    nip = fields.Str()
    pas_foto = fields.Str(allow_none=True)
    pdf_sk_pns = fields.Str(allow_none=True)


class LaporanSchema(Schema):
    id = fields.Int()
    nama_tamu = fields.Str()
    no_hp = fields.Str()
    isi_pesan = fields.Str()
    tanggal = fields.Str()
    status = fields.Str(allow_none=True)
    balasan = fields.Str(allow_none=True)


class BeritaSchema(Schema):
    id = fields.Int()
    judul = fields.Str()
    isi = fields.Str()
    gambar = fields.Str(allow_none=True)
    tanggal = fields.Str()


class GaleriSchema(Schema):
    id = fields.Int()
    judul_foto = fields.Str()
    file_foto = fields.Str()
    tanggal = fields.Str()


class DiskusiSchema(Schema):
    id = fields.Int()
    pengirim = fields.Str()
    role_pengirim = fields.Str()
    pesan = fields.Str()
    tanggal = fields.Str()


class PageSchema(Schema):
    page = fields.Int()
    per_page = fields.Int()
    total = fields.Int()
    pages = fields.Int()


class PerkaraPageSchema(PageSchema):
    items = fields.List(fields.Nested(PerkaraSchema))


class PegawaiPageSchema(PageSchema):
    items = fields.List(fields.Nested(PegawaiSchema))


class LaporanPageSchema(PageSchema):
    items = fields.List(fields.Nested(LaporanSchema))


class BeritaPageSchema(PageSchema):
    items = fields.List(fields.Nested(BeritaSchema))


class GaleriPageSchema(PageSchema):
    items = fields.List(fields.Nested(GaleriSchema))


class DiskusiPageSchema(PageSchema):
    items = fields.List(fields.Nested(DiskusiSchema))


def _paginate(query_count_sql, query_items_sql, page, per_page, params=()):
    page = max(page, 1)
    per_page = max(min(per_page, 100), 1)
    conn = get_db()
    total = conn.execute(query_count_sql, params).fetchone()[0]
    pages = max(math.ceil(total / per_page), 1) if total else 1
    page = min(page, pages)
    offset = (page - 1) * per_page
    items = conn.execute(query_items_sql, (*params, per_page, offset)).fetchall()
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
        "items": items,
    }


def register_api(api):
    blp = Blueprint("api", "api", url_prefix="/api/v1", description="API for PA IKN system.")

    @blp.route("/health")
    class Health(MethodView):
        @blp.response(200, Schema.from_dict({"status": fields.Str()})())
        def get(self):
            return {"status": "ok"}

    @blp.route("/perkara")
    class PerkaraList(MethodView):
        @blp.arguments(PaginationArgsSchema, location="query")
        @blp.response(200, PerkaraPageSchema)
        def get(self, args):
            return _paginate(
                "SELECT COUNT(*) FROM perkara",
                "SELECT * FROM perkara ORDER BY id DESC LIMIT ? OFFSET ?",
                args["page"],
                args["per_page"],
            )

    @blp.route("/perkara/<int:perkara_id>")
    class PerkaraDetail(MethodView):
        @blp.response(200, PerkaraSchema)
        def get(self, perkara_id):
            conn = get_db()
            row = conn.execute("SELECT * FROM perkara WHERE id=?", (perkara_id,)).fetchone()
            if not row:
                abort(404, message="Perkara not found.")
            return row

    @blp.route("/pegawai")
    class PegawaiList(MethodView):
        @blp.arguments(PaginationArgsSchema, location="query")
        @blp.response(200, PegawaiPageSchema)
        def get(self, args):
            return _paginate(
                "SELECT COUNT(*) FROM users",
                "SELECT id, username, role, nama_lengkap, nip, pas_foto, pdf_sk_pns FROM users ORDER BY id DESC LIMIT ? OFFSET ?",
                args["page"],
                args["per_page"],
            )

    @blp.route("/laporan")
    class LaporanList(MethodView):
        @blp.arguments(PaginationArgsSchema, location="query")
        @blp.response(200, LaporanPageSchema)
        def get(self, args):
            return _paginate(
                "SELECT COUNT(*) FROM laporan_tamu",
                "SELECT * FROM laporan_tamu ORDER BY id DESC LIMIT ? OFFSET ?",
                args["page"],
                args["per_page"],
            )

    @blp.route("/berita")
    class BeritaList(MethodView):
        @blp.arguments(PaginationArgsSchema, location="query")
        @blp.response(200, BeritaPageSchema)
        def get(self, args):
            return _paginate(
                "SELECT COUNT(*) FROM berita",
                "SELECT * FROM berita ORDER BY id DESC LIMIT ? OFFSET ?",
                args["page"],
                args["per_page"],
            )

    @blp.route("/galeri")
    class GaleriList(MethodView):
        @blp.arguments(PaginationArgsSchema, location="query")
        @blp.response(200, GaleriPageSchema)
        def get(self, args):
            return _paginate(
                "SELECT COUNT(*) FROM galeri",
                "SELECT * FROM galeri ORDER BY id DESC LIMIT ? OFFSET ?",
                args["page"],
                args["per_page"],
            )

    @blp.route("/diskusi")
    class DiskusiList(MethodView):
        @blp.arguments(PaginationArgsSchema, location="query")
        @blp.response(200, DiskusiPageSchema)
        def get(self, args):
            return _paginate(
                "SELECT COUNT(*) FROM diskusi",
                "SELECT * FROM diskusi ORDER BY id DESC LIMIT ? OFFSET ?",
                args["page"],
                args["per_page"],
            )

    api.register_blueprint(blp)

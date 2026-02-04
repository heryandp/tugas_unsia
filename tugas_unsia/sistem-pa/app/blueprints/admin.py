import os
from datetime import datetime

import json

from flask import Blueprint, current_app, flash, make_response, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from ..db import get_db
from ..utils import allowed_file, max_upload_bytes, sanitize_text, validate_upload


bp = Blueprint("admin", __name__)


def _hx_error(message, status=400):
    resp = make_response("", status)
    resp.headers["HX-Trigger"] = json.dumps({"toast": {"level": "error", "message": message}})
    return resp


def _error_redirect(message, endpoint):
    if request.headers.get("HX-Request"):
        return _hx_error(message)
    flash(message, "error")
    return redirect(url_for(endpoint))


@bp.route("/cms_update", methods=["POST"])
def cms_update():
    if session.get("role") != "admin_it":
        return "HANYA ADMIN IT"
    conn = get_db()

    if "sambutan_ketua" in request.form:
        conn.execute(
            "UPDATE pengaturan SET nilai=? WHERE kunci='sambutan_ketua'",
            (request.form["sambutan_ketua"],),
        )
        conn.execute(
            "UPDATE pengaturan SET nilai=? WHERE kunci='no_telp'",
            (request.form["no_telp"],),
        )
        conn.execute(
            "UPDATE pengaturan SET nilai=? WHERE kunci='email_kantor'",
            (request.form["email_kantor"],),
        )

    def save_img(file_obj, key_name):
        if file_obj and file_obj.filename != "":
            if allowed_file(file_obj.filename):
                try:
                    ok, msg = validate_upload(file_obj, max_upload_bytes(file_obj))
                    if not ok:
                        raise ValueError(msg)
                    fname = secure_filename(f"{key_name}_{file_obj.filename}")
                    upload_dir = current_app.config["UPLOAD_FOLDER"]
                    if not os.path.exists(upload_dir):
                        os.makedirs(upload_dir)
                    file_path = os.path.join(upload_dir, fname)
                    file_obj.save(file_path)
                    conn.execute(
                        "UPDATE pengaturan SET nilai=? WHERE kunci=?",
                        (f"/uploads/{fname}", key_name),
                    )
                    return True
                except PermissionError:
                    return False
            return False
        return None

    try:
        save_img(request.files.get("bg_landing"), "bg_landing")
        save_img(request.files.get("bg_login"), "bg_login")
        save_img(request.files.get("bg_dashboard"), "bg_dashboard")
        save_img(request.files.get("bg_verify_pin"), "bg_verify_pin")
        save_img(request.files.get("foto_ketua"), "foto_ketua")
        save_img(request.files.get("logo_web"), "logo_web")
        save_img(request.files.get("logo_pa_ikn"), "logo_pa_ikn")
        save_img(request.files.get("barcode_ttd"), "barcode_ttd")
        for i in range(1, 6):
            save_img(request.files.get(f"kegiatan_{i}"), f"kegiatan_{i}")
        conn.commit()
        flash("Pengaturan berhasil diperbarui.", "success")
    except Exception as e:
        conn.rollback()
        flash("Gagal menyimpan pengaturan.", "error")
        return f"<h1>Error Upload</h1><p>{e}</p><p><a href='/dashboard/admin'>Kembali</a></p>", 500
    if request.headers.get("HX-Request"):
        resp = make_response("", 204)
        resp.headers["HX-Trigger"] = json.dumps(
            {"toast": {"level": "success", "message": "Pengaturan berhasil diperbarui."}}
        )
        return resp
    return redirect(url_for("dashboard.admin"))


@bp.route("/tambah_user", methods=["POST"])
def tambah_user():
    if session.get("role") not in ["admin_it", "sekretaris", "kassubag"]:
        return "Akses Ditolak"
    u = sanitize_text(request.form.get("username", ""), 50)
    p = sanitize_text(request.form.get("password", ""), 64)
    r = sanitize_text(request.form.get("role", ""), 20)
    n = sanitize_text(request.form.get("nama", ""), 80)
    nip = sanitize_text(request.form.get("nip", ""), 20)
    pin = sanitize_text(request.form.get("pin_6digit", ""), 6)
    if not u or not p or not r or not n or not nip or not pin:
        return _error_redirect("Mohon lengkapi semua field.", "dashboard.admin")
    if r not in ["staff", "hakim", "panitera", "sekretaris", "kassubag", "ketua", "wakil_ketua", "admin_it"]:
        return _error_redirect("Role tidak valid.", "dashboard.admin")
    if len(u) < 3 or len(u) > 50:
        return _error_redirect("Username 3-50 karakter.", "dashboard.admin")
    if len(p) < 4 or len(p) > 64:
        return _error_redirect("Password 4-64 karakter.", "dashboard.admin")
    if not nip.isdigit() or len(nip) < 5:
        return _error_redirect("NIP harus angka minimal 5 digit.", "dashboard.admin")
    if not pin.isdigit() or len(pin) != 6:
        return _error_redirect("PIN harus 6 digit angka.", "dashboard.admin")
    foto = request.files.get("pas_foto")
    foto_name = ""
    if foto and allowed_file(foto.filename):
        ok, msg = validate_upload(foto, max_upload_bytes(foto))
        if not ok:
            return _error_redirect(msg, "dashboard.admin")
        foto_name = secure_filename(f"pegawai_{nip}_{foto.filename}")
        foto.save(os.path.join(current_app.config["UPLOAD_FOLDER"], foto_name))
    pdf_sk = request.files.get("pdf_sk_pns")
    pdf_name = ""
    if pdf_sk and allowed_file(pdf_sk.filename):
        ok, msg = validate_upload(pdf_sk, max_upload_bytes(pdf_sk))
        if not ok:
            return _error_redirect(msg, "dashboard.admin")
        pdf_name = secure_filename(f"SK_{nip}_{pdf_sk.filename}")
        pdf_sk.save(os.path.join(current_app.config["UPLOAD_FOLDER"], pdf_name))
    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE username=?", (u,)).fetchone()
    if existing:
        return _error_redirect("Username sudah digunakan.", "dashboard.admin")
    conn.execute(
        "INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
        (u, p, r, n, nip, foto_name, pin, pdf_name),
    )
    conn.commit()
    flash("Pegawai baru berhasil ditambahkan.", "success")
    if request.headers.get("HX-Request"):
        resp = make_response("", 204)
        resp.headers["HX-Trigger"] = json.dumps(
            {"toast": {"level": "success", "message": "Pegawai baru berhasil ditambahkan."}}
        )
        return resp
    return redirect(url_for("dashboard.admin"))


@bp.route("/tambah_berita", methods=["POST"])
def tambah_berita():
    if session.get("role") != "admin_it":
        return "Akses Ditolak"
    judul = sanitize_text(request.form.get("judul", ""), 120)
    isi = sanitize_text(request.form.get("isi", ""), 2000)
    if not judul or not isi:
        return _error_redirect("Judul dan isi berita wajib.", "dashboard.admin")
    if len(judul) < 5 or len(judul) > 120:
        return _error_redirect("Judul 5-120 karakter.", "dashboard.admin")
    if len(isi) < 10:
        return _error_redirect("Isi berita minimal 10 karakter.", "dashboard.admin")
    tgl = datetime.now().strftime("%Y-%m-%d")
    gambar = request.files.get("gambar")
    gambar_name = "https://via.placeholder.com/150"
    if gambar and allowed_file(gambar.filename):
        ok, msg = validate_upload(gambar, max_upload_bytes(gambar))
        if not ok:
            return _error_redirect(msg, "dashboard.admin")
        gambar_name = secure_filename(f"berita_{gambar.filename}")
        gambar.save(os.path.join(current_app.config["UPLOAD_FOLDER"], gambar_name))
        gambar_name = f"/uploads/{gambar_name}"
    conn = get_db()
    cur = conn.execute("INSERT INTO berita VALUES (NULL, ?, ?, ?, ?)", (judul, isi, gambar_name, tgl))
    conn.commit()
    flash("Berita berhasil diposting.", "success")
    if request.headers.get("HX-Request"):
        b = conn.execute("SELECT * FROM berita WHERE id=?", (cur.lastrowid,)).fetchone()
        resp = make_response(render_template("partials/berita_row.html", b=b))
        resp.headers["HX-Trigger"] = json.dumps(
            {"toast": {"level": "success", "message": "Berita berhasil diposting."}}
        )
        return resp
    return redirect(url_for("dashboard.admin"))


@bp.route("/tambah_galeri", methods=["POST"])
def tambah_galeri():
    if session.get("role") != "admin_it":
        return "Akses Ditolak"
    judul = sanitize_text(request.form.get("judul_foto", ""), 120)
    if not judul:
        return _error_redirect("Judul foto wajib.", "dashboard.admin")
    if len(judul) < 3 or len(judul) > 120:
        return _error_redirect("Judul foto 3-120 karakter.", "dashboard.admin")
    tgl = datetime.now().strftime("%Y-%m-%d")
    foto = request.files.get("file_foto")
    foto_name = "https://via.placeholder.com/400x300"
    if foto and allowed_file(foto.filename):
        ok, msg = validate_upload(foto, max_upload_bytes(foto))
        if not ok:
            return _error_redirect(msg, "dashboard.admin")
        foto_name = secure_filename(f"galeri_{foto.filename}")
        foto.save(os.path.join(current_app.config["UPLOAD_FOLDER"], foto_name))
        foto_name = f"/uploads/{foto_name}"
    conn = get_db()
    cur = conn.execute("INSERT INTO galeri VALUES (NULL, ?, ?, ?)", (judul, foto_name, tgl))
    conn.commit()
    flash("Foto galeri berhasil diunggah.", "success")
    if request.headers.get("HX-Request"):
        g = conn.execute("SELECT * FROM galeri WHERE id=?", (cur.lastrowid,)).fetchone()
        resp = make_response(render_template("partials/galeri_row.html", g=g))
        resp.headers["HX-Trigger"] = json.dumps(
            {"toast": {"level": "success", "message": "Foto galeri berhasil diunggah."}}
        )
        return resp
    return redirect(url_for("dashboard.admin"))

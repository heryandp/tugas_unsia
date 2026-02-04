import math
import os
import random
from datetime import datetime

import json

from flask import Blueprint, current_app, flash, make_response, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from ..db import get_db
from ..utils import allowed_file, max_upload_bytes, sanitize_text, validate_upload


bp = Blueprint("dashboard", __name__)


def _guard_dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    if "pin_required" in session:
        return redirect(url_for("auth.verify_pin"))
    return None


def _dashboard_context(perkara=None):
    conn = get_db()
    if perkara is None:
        perkara = conn.execute("SELECT * FROM perkara").fetchall()
    pegawai = conn.execute("SELECT * FROM users").fetchall()
    chat = conn.execute("SELECT * FROM diskusi ORDER BY id DESC LIMIT 50").fetchall()
    laporan = conn.execute("SELECT * FROM laporan_tamu ORDER BY id DESC").fetchall()
    berita = conn.execute("SELECT * FROM berita ORDER BY id DESC").fetchall()
    galeri = conn.execute("SELECT * FROM galeri ORDER BY id DESC").fetchall()
    rows = conn.execute("SELECT * FROM pengaturan").fetchall()
    p = {row["kunci"]: row["nilai"] for row in rows}
    return {
        "role": session["role"],
        "nama_user": session["nama"],
        "perkara": perkara,
        "pegawai": pegawai,
        "chat": chat,
        "laporan": laporan,
        "berita": berita,
        "galeri": galeri,
        "p": p,
        "tgl_skrg": datetime.now().strftime("%Y-%m-%d"),
    }


def _redirect_back(default_endpoint):
    return redirect(request.referrer or url_for(default_endpoint))


def _hx_error(message, status=400):
    resp = make_response("", status)
    resp.headers["HX-Trigger"] = json.dumps({"toast": {"level": "error", "message": message}})
    return resp


def _next_no_perkara(year):
    conn = get_db()
    like = f"%/Pdt.G/{year}/PA.IKN"
    rows = conn.execute(
        "SELECT no_perkara FROM perkara WHERE no_perkara LIKE ? ORDER BY id DESC",
        (like,),
    ).fetchall()
    max_seq = 0
    for row in rows:
        try:
            seq = int(str(row["no_perkara"]).split("/")[0])
            if seq > max_seq:
                max_seq = seq
        except (ValueError, IndexError, TypeError):
            continue
    return f"{max_seq + 1}/Pdt.G/{year}/PA.IKN"


@bp.route("/dashboard")
def dashboard():
    guard = _guard_dashboard()
    if guard:
        return guard
    page = request.args.get("page")
    if page:
        legacy = {
            "input_perkara": "dashboard.input_perkara",
            "data_akta": "dashboard.data_akta",
            "ruang_hakim": "dashboard.ruang_hakim",
            "diskusi": "dashboard.diskusi",
            "laporan": "dashboard.laporan",
            "admin": "dashboard.admin",
            "data_pegawai": "dashboard.data_pegawai",
        }
        endpoint = legacy.get(page)
        if endpoint:
            return redirect(url_for(endpoint))
    return redirect(url_for("dashboard.input_perkara"))


@bp.route("/dashboard/input-perkara")
def input_perkara():
    guard = _guard_dashboard()
    if guard:
        return guard
    conn = get_db()
    perkara_latest = conn.execute("SELECT * FROM perkara ORDER BY id DESC LIMIT 5").fetchall()
    ctx = _dashboard_context(perkara=perkara_latest)
    year_now = datetime.now().year
    ctx["no_perkara_auto"] = _next_no_perkara(year_now)
    ctx["active_page"] = "input_perkara"
    return render_template("dashboard_input.html", **ctx)


@bp.route("/dashboard/data-akta")
def data_akta():
    guard = _guard_dashboard()
    if guard:
        return guard
    page = max(int(request.args.get("page", 1)), 1)
    per_page = max(int(request.args.get("per_page", 10)), 1)
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM perkara").fetchone()[0]
    pages = max(math.ceil(total / per_page), 1) if total else 1
    page = min(page, pages)
    offset = (page - 1) * per_page
    perkara_page = conn.execute(
        "SELECT * FROM perkara ORDER BY id DESC LIMIT ? OFFSET ?",
        (per_page, offset),
    ).fetchall()
    ctx = _dashboard_context(perkara=perkara_page)
    ctx["active_page"] = "data_akta"
    ctx["perkara_total"] = total
    ctx["perkara_page"] = page
    ctx["perkara_pages"] = pages
    ctx["perkara_per_page"] = per_page
    ctx["perkara_has_prev"] = page > 1
    ctx["perkara_has_next"] = page < pages
    ctx["perkara_prev"] = page - 1
    ctx["perkara_next"] = page + 1
    return render_template("dashboard_data.html", **ctx)


@bp.route("/dashboard/ruang-hakim")
def ruang_hakim():
    guard = _guard_dashboard()
    if guard:
        return guard
    ctx = _dashboard_context()
    ctx["active_page"] = "ruang_hakim"
    return render_template("dashboard_hakim.html", **ctx)


@bp.route("/dashboard/diskusi")
def diskusi():
    guard = _guard_dashboard()
    if guard:
        return guard
    ctx = _dashboard_context()
    ctx["active_page"] = "diskusi"
    return render_template("dashboard_chat.html", **ctx)


@bp.route("/dashboard/laporan")
def laporan():
    guard = _guard_dashboard()
    if guard:
        return guard
    ctx = _dashboard_context()
    ctx["active_page"] = "laporan"
    return render_template("dashboard_laporan.html", **ctx)


@bp.route("/dashboard/admin")
def admin():
    guard = _guard_dashboard()
    if guard:
        return guard
    ctx = _dashboard_context()
    ctx["active_page"] = "admin"
    return render_template("dashboard_admin.html", **ctx)


@bp.route("/dashboard/data-pegawai")
def data_pegawai():
    guard = _guard_dashboard()
    if guard:
        return guard
    ctx = _dashboard_context()
    ctx["active_page"] = "data_pegawai"
    return render_template("dashboard_pegawai.html", **ctx)


@bp.route("/tambah_perkara", methods=["POST"])
def tambah_perkara():
    if session.get("role") not in ["staff", "admin_it"]:
        return "Akses Ditolak"
    no = sanitize_text(request.form.get("no_perkara", ""), 50)
    if not no:
        no = _next_no_perkara(datetime.now().year)
    suami = sanitize_text(request.form.get("nama_suami", ""), 80)
    istri = sanitize_text(request.form.get("nama_istri", ""), 80)
    keluhan = sanitize_text(request.form.get("keluhan", ""), 500)
    tgl = sanitize_text(request.form.get("tanggal_daftar", ""), 20)
    staff = sanitize_text(request.form.get("nama_staff", ""), 80)
    biaya = sanitize_text(request.form.get("biaya_daftar", ""), 20)
    tanggal_sidang = sanitize_text(request.form.get("tanggal_sidang", ""), 20)
    if not suami or not istri or not tgl or not staff or not tanggal_sidang:
        msg = "Mohon lengkapi field wajib."
        if request.headers.get("HX-Request"):
            return _hx_error(msg)
        flash(msg, "error")
        return redirect(url_for("dashboard.input_perkara"))
    if len(suami) < 3 or len(istri) < 3:
        msg = "Nama suami/istri minimal 3 karakter."
        if request.headers.get("HX-Request"):
            return _hx_error(msg)
        flash(msg, "error")
        return redirect(url_for("dashboard.input_perkara"))
    if keluhan and len(keluhan) < 5:
        msg = "Keluhan minimal 5 karakter."
        if request.headers.get("HX-Request"):
            return _hx_error(msg)
        flash(msg, "error")
        return redirect(url_for("dashboard.input_perkara"))
    if biaya and (not biaya.isdigit() or int(biaya) < 0):
        msg = "Biaya harus angka >= 0."
        if request.headers.get("HX-Request"):
            return _hx_error(msg)
        flash(msg, "error")
        return redirect(url_for("dashboard.input_perkara"))
    fs, fi = request.files.get("file_suami"), request.files.get("file_istri")
    ns, ni = "", ""
    try:
        if fs and allowed_file(fs.filename):
            ok, msg = validate_upload(fs, max_upload_bytes(fs))
            if not ok:
                return _hx_error(msg) if request.headers.get("HX-Request") else redirect(url_for("dashboard.input_perkara"))
            ns = secure_filename(no + "_S_" + fs.filename)
            fs.save(os.path.join(current_app.config["UPLOAD_FOLDER"], ns))
        if fi and allowed_file(fi.filename):
            ok, msg = validate_upload(fi, max_upload_bytes(fi))
            if not ok:
                return _hx_error(msg) if request.headers.get("HX-Request") else redirect(url_for("dashboard.input_perkara"))
            ni = secure_filename(no + "_I_" + fi.filename)
            fi.save(os.path.join(current_app.config["UPLOAD_FOLDER"], ni))
    except Exception as e:
        current_app.logger.error(f"Error upload file: {e}")
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO perkara
        (no_perkara, nama_suami, nama_istri, keluhan, tanggal_daftar, nama_staff,
        file_suami, file_istri, status, biaya_daftar, hasil_mediasi, tanggal_sidang)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (no, suami, istri, keluhan, tgl, staff, ns, ni, "Terdaftar (Menunggu Mediasi)", biaya, "Belum Dimediasi", tanggal_sidang),
    )
    conn.commit()
    flash("Perkara berhasil ditambahkan.", "success")
    if request.headers.get("HX-Request"):
        r = conn.execute("SELECT * FROM perkara WHERE id=?", (cur.lastrowid,)).fetchone()
        resp = make_response(render_template("partials/perkara_row.html", r=r, role=session["role"]))
        resp.headers["HX-Trigger"] = json.dumps(
            {"toast": {"level": "success", "message": "Perkara berhasil ditambahkan."}}
        )
        return resp
    return _redirect_back("dashboard.input_perkara")


@bp.route("/update_hakim", methods=["POST"])
def update_hakim():
    if session.get("role") not in ["hakim", "admin_it", "ketua", "wakil_ketua"]:
        return "Akses Ditolak"
    id_p = sanitize_text(request.form.get("id_perkara", ""), 20)
    hasil = sanitize_text(request.form.get("hasil_mediasi", ""), 50)
    detail = sanitize_text(request.form.get("detail_mediasi", ""), 500)
    if not id_p or not hasil:
        msg = "Field wajib belum lengkap."
        if request.headers.get("HX-Request"):
            return _hx_error(msg)
        flash(msg, "error")
        return _redirect_back("dashboard.ruang_hakim")
    mediator = session["nama"]
    status_baru = "Lanjut Sidang" if hasil == "Gagal" else "Berhasil Rujuk"
    if hasil == "Gagal":
        status_baru = "Putusan Cerai Sah"
    conn = get_db()
    conn.execute(
        "UPDATE perkara SET hasil_mediasi=?, detail_mediasi=?, nama_mediator=?, status=? WHERE id=?",
        (hasil, detail, mediator, status_baru, id_p),
    )
    conn.commit()
    if request.headers.get("HX-Request"):
        r = conn.execute("SELECT * FROM perkara WHERE id=?", (id_p,)).fetchone()
        resp = make_response(render_template("partials/hakim_card.html", r=r))
        resp.headers["HX-Trigger"] = json.dumps(
            {"toast": {"level": "success", "message": "Putusan berhasil diperbarui."}}
        )
        return resp
    flash("Putusan berhasil diperbarui.", "success")
    return _redirect_back("dashboard.ruang_hakim")


@bp.route("/update_panitera", methods=["POST"])
def update_panitera():
    if session.get("role") not in ["panitera", "admin_it"]:
        return "Akses Ditolak"
    id_p = sanitize_text(request.form.get("id_perkara", ""), 20)
    if not id_p:
        msg = "ID perkara tidak valid."
        if request.headers.get("HX-Request"):
            return _hx_error(msg)
        flash(msg, "error")
        return _redirect_back("dashboard.data_akta")
    no_akta = f"AC-{random.randint(1000,9999)}/PA-IKN/{datetime.now().year}"
    conn = get_db()
    conn.execute("UPDATE perkara SET no_akta_cerai=? WHERE id=?", (no_akta, id_p))
    conn.commit()
    if request.headers.get("HX-Request"):
        r = conn.execute("SELECT * FROM perkara WHERE id=?", (id_p,)).fetchone()
        resp = make_response(render_template("partials/perkara_row.html", r=r, role=session["role"]))
        resp.headers["HX-Trigger"] = json.dumps(
            {"toast": {"level": "success", "message": "Akta cerai berhasil diterbitkan."}}
        )
        return resp
    flash("Akta cerai berhasil diterbitkan.", "success")
    return _redirect_back("dashboard.data_akta")


@bp.route("/kirim_chat", methods=["POST"])
def kirim_chat():
    pesan = sanitize_text(request.form.get("pesan", ""), 500)
    if not pesan:
        msg = "Pesan tidak boleh kosong."
        if request.headers.get("HX-Request"):
            return _hx_error(msg)
        flash(msg, "error")
        return _redirect_back("dashboard.diskusi")
    if len(pesan) > 500:
        msg = "Pesan terlalu panjang (maks 500)."
        if request.headers.get("HX-Request"):
            return _hx_error(msg)
        flash(msg, "error")
        return _redirect_back("dashboard.diskusi")
    tgl = datetime.now().strftime("%d-%m-%Y %H:%M")
    conn = get_db()
    conn.execute(
        "INSERT INTO diskusi (pengirim, role_pengirim, pesan, tanggal) VALUES (?, ?, ?, ?)",
        (session["nama"], session["role"], pesan, tgl),
    )
    conn.commit()
    flash("Pesan terkirim.", "success")
    if request.headers.get("HX-Request"):
        resp = make_response("", 204)
        resp.headers["HX-Trigger"] = json.dumps(
            {"toast": {"level": "success", "message": "Pesan terkirim."}}
        )
        return resp
    return _redirect_back("dashboard.diskusi")


@bp.route("/balas_saran", methods=["POST"])
def balas_saran():
    if session.get("role") not in ["kassubag", "admin_it", "sekretaris"]:
        return "Akses Ditolak"
    id_laporan = sanitize_text(request.form.get("id_laporan", ""), 20)
    balasan = sanitize_text(request.form.get("balasan", ""), 500)
    if not id_laporan or not balasan:
        msg = "Balasan wajib diisi."
        if request.headers.get("HX-Request"):
            return _hx_error(msg)
        flash(msg, "error")
        return _redirect_back("dashboard.laporan")
    if len(balasan) < 3 or len(balasan) > 500:
        msg = "Balasan 3-500 karakter."
        if request.headers.get("HX-Request"):
            return _hx_error(msg)
        flash(msg, "error")
        return _redirect_back("dashboard.laporan")
    conn = get_db()
    conn.execute("UPDATE laporan_tamu SET balasan=?, status='Dibalas' WHERE id=?", (balasan, id_laporan))
    conn.commit()
    flash("Balasan berhasil dikirim.", "success")
    if request.headers.get("HX-Request"):
        l = conn.execute("SELECT * FROM laporan_tamu WHERE id=?", (id_laporan,)).fetchone()
        resp = make_response(render_template("partials/laporan_card.html", l=l, role=session["role"]))
        resp.headers["HX-Trigger"] = json.dumps(
            {"toast": {"level": "success", "message": "Balasan berhasil dikirim."}}
        )
        return resp
    return _redirect_back("dashboard.laporan")


@bp.route("/hapus_data/<tipe>/<id>")
def hapus_data(tipe, id):
    if session.get("role") != "admin_it":
        return "Akses Ditolak"
    conn = get_db()
    allowed = {
        "perkara": "perkara",
        "pegawai": "users",
        "chat": "diskusi",
        "laporan": "laporan_tamu",
        "berita": "berita",
        "galeri": "galeri",
    }
    if tipe not in allowed:
        return "Tipe tidak valid", 400
    conn.execute(f"DELETE FROM {allowed[tipe]} WHERE id=?", (id,))
    conn.commit()
    flash("Data berhasil dihapus.", "success")
    if request.headers.get("HX-Request"):
        resp = make_response("", 204)
        resp.headers["HX-Trigger"] = json.dumps(
            {"toast": {"level": "success", "message": "Data berhasil dihapus."}}
        )
        return resp
    return _redirect_back("dashboard.admin")


@bp.route("/edit_pegawai/<id>", methods=["GET", "POST"])
def edit_pegawai(id):
    if session.get("role") not in ["admin_it", "sekretaris", "kassubag"]:
        return "Akses Ditolak"
    conn = get_db()
    if request.method == "POST":
        nama = sanitize_text(request.form.get("nama", ""), 80)
        role = sanitize_text(request.form.get("role", ""), 20)
        nip = sanitize_text(request.form.get("nip", ""), 20)
        pin = sanitize_text(request.form.get("pin_6digit", ""), 6)
        if not nama or not role or not nip or not pin:
            msg = "Mohon lengkapi semua field."
            if request.headers.get("HX-Request"):
                return _hx_error(msg)
            flash(msg, "error")
            return redirect(url_for("dashboard.data_pegawai"))
        if role not in ["staff", "hakim", "panitera", "sekretaris", "kassubag", "ketua", "wakil_ketua", "admin_it"]:
            msg = "Role tidak valid."
            if request.headers.get("HX-Request"):
                return _hx_error(msg)
            flash(msg, "error")
            return redirect(url_for("dashboard.data_pegawai"))
        if not nip.isdigit() or len(nip) < 5:
            msg = "NIP harus angka minimal 5 digit."
            if request.headers.get("HX-Request"):
                return _hx_error(msg)
            flash(msg, "error")
            return redirect(url_for("dashboard.data_pegawai"))
        if not pin.isdigit() or len(pin) != 6:
            msg = "PIN harus 6 digit angka."
            if request.headers.get("HX-Request"):
                return _hx_error(msg)
            flash(msg, "error")
            return redirect(url_for("dashboard.data_pegawai"))
        conn.execute(
            "UPDATE users SET nama_lengkap=?, role=?, nip=?, pin_6digit=? WHERE id=?",
            (nama, role, nip, pin, id),
        )
        foto = request.files.get("pas_foto")
        if foto and allowed_file(foto.filename):
            ok, msg = validate_upload(foto, max_upload_bytes(foto))
            if not ok:
                return _hx_error(msg) if request.headers.get("HX-Request") else redirect(url_for("dashboard.data_pegawai"))
            foto_name = secure_filename(f"pegawai_{nip}_{foto.filename}")
            foto.save(os.path.join(current_app.config["UPLOAD_FOLDER"], foto_name))
            conn.execute("UPDATE users SET pas_foto=? WHERE id=?", (foto_name, id))
        pdf_sk = request.files.get("pdf_sk_pns")
        if pdf_sk and allowed_file(pdf_sk.filename):
            ok, msg = validate_upload(pdf_sk, max_upload_bytes(pdf_sk))
            if not ok:
                return _hx_error(msg) if request.headers.get("HX-Request") else redirect(url_for("dashboard.data_pegawai"))
            pdf_name = secure_filename(f"SK_{nip}_{pdf_sk.filename}")
            pdf_sk.save(os.path.join(current_app.config["UPLOAD_FOLDER"], pdf_name))
            conn.execute("UPDATE users SET pdf_sk_pns=? WHERE id=?", (pdf_name, id))
        conn.commit()
        flash("Data pegawai berhasil diperbarui.", "success")
        if request.headers.get("HX-Request"):
            resp = make_response("", 204)
            resp.headers["HX-Trigger"] = json.dumps(
                {"toast": {"level": "success", "message": "Data pegawai berhasil diperbarui."}}
            )
            return resp
        return redirect(url_for("dashboard.data_pegawai"))
    pegawai = conn.execute("SELECT * FROM users WHERE id=?", (id,)).fetchone()
    return render_template("edit_pegawai.html", pegawai=pegawai)

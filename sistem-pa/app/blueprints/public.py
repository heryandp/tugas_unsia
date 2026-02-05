from datetime import datetime

import uuid
from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..db import get_db
from ..utils import sanitize_text


bp = Blueprint("public", __name__)


@bp.route("/")
def landing_page():
    """
    Halaman Landing Page Public
    ---
    tags:
      - Public
    responses:
      200:
        description: Halaman utama menampilkan berita dan galeri
    """
    conn = get_db()
    rows = conn.execute("SELECT * FROM pengaturan").fetchall()
    p = {row["kunci"]: row["nilai"] for row in rows}
    berita = conn.execute("SELECT * FROM berita WHERE is_deleted=0 ORDER BY RANDOM() LIMIT 3").fetchall()
    galeri = conn.execute("SELECT * FROM galeri WHERE is_deleted=0 ORDER BY id DESC LIMIT 5").fetchall()
    return render_template("landing.html", p=p, berita=berita, galeri=galeri)


@bp.route("/profil_pegawai")
def profil_pegawai():
    conn = get_db()
    rows = conn.execute("SELECT * FROM pengaturan").fetchall()
    p = {row["kunci"]: row["nilai"] for row in rows}
    pegawai = conn.execute(
        "SELECT nama_lengkap, role, nip, pas_foto FROM users WHERE is_deleted=0 ORDER BY role"
    ).fetchall()
    return render_template("profil_publik.html", p=p, pegawai=pegawai)


@bp.route("/jadwal_sidang")
def jadwal_sidang():
    conn = get_db()
    rows = conn.execute("SELECT * FROM pengaturan").fetchall()
    p = {row["kunci"]: row["nilai"] for row in rows}
    jadwal = conn.execute(
        "SELECT * FROM perkara WHERE tanggal_sidang IS NOT NULL AND tanggal_sidang != '' AND is_deleted=0 ORDER BY tanggal_sidang"
    ).fetchall()
    return render_template("jadwal_publik.html", p=p, jadwal=jadwal)


@bp.route("/sejarah")
def sejarah():
    conn = get_db()
    rows = conn.execute("SELECT * FROM pengaturan").fetchall()
    p = {row["kunci"]: row["nilai"] for row in rows}
    return render_template("sejarah.html", p=p)


@bp.route("/visi-misi")
def visi_misi():
    conn = get_db()
    rows = conn.execute("SELECT * FROM pengaturan").fetchall()
    p = {row["kunci"]: row["nilai"] for row in rows}
    return render_template("visi_misi.html", p=p)


@bp.route("/kirim_laporan_tamu", methods=["POST"])
def kirim_laporan_tamu():
    """
    Kirim Laporan Tamu
    ---
    tags:
      - Public
    parameters:
      - name: nama
        in: formData
        type: string
        required: true
        description: Nama Pelapor
      - name: hp
        in: formData
        type: string
        required: true
        description: Nomor HP
      - name: pesan
        in: formData
        type: string
        required: true
        description: Isi Laporan
    responses:
      302:
        description: Redirect kembali ke landing page dengan flash message
    """
    nama = sanitize_text(request.form.get("nama", ""), 80)
    hp = sanitize_text(request.form.get("hp", ""), 20)
    pesan = sanitize_text(request.form.get("pesan", ""), 500)
    if not nama or not hp or not pesan:
        flash("Mohon lengkapi semua field.", "error")
        return redirect(url_for("public.landing_page"))
    if len(nama) < 3 or len(nama) > 80:
        flash("Nama harus 3-80 karakter.", "error")
        return redirect(url_for("public.landing_page"))
    if not hp.isdigit() or len(hp) < 8 or len(hp) > 15:
        flash("No. HP harus 8-15 digit angka.", "error")
        return redirect(url_for("public.landing_page"))
    if len(pesan) < 5 or len(pesan) > 500:
        flash("Pesan harus 5-500 karakter.", "error")
        return redirect(url_for("public.landing_page"))
    tgl = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    conn.execute(
        "INSERT INTO laporan_tamu (id, nama_tamu, no_hp, isi_pesan, tanggal, status, is_deleted, deleted_at, created_at, created_by, updated_at, updated_by) VALUES (?, ?, ?, ?, ?, ?, 0, NULL, ?, ?, NULL, NULL)",
        (str(uuid.uuid4()), nama, hp, pesan, tgl, "Menunggu Balasan", tgl, nama),
    )
    conn.commit()
    flash("Laporan berhasil dikirim. Terima kasih.", "success")
    return redirect(url_for("public.landing_page"))

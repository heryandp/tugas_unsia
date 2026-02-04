import random
import string
import time

from flask import Blueprint, redirect, render_template, request, session, url_for

from ..db import get_db


bp = Blueprint("auth", __name__)
_RATE_LIMIT = {}


def _rate_limited(key, limit=10, window_seconds=300):
    now = time.time()
    window_start = now - window_seconds
    entries = [t for t in _RATE_LIMIT.get(key, []) if t >= window_start]
    if len(entries) >= limit:
        _RATE_LIMIT[key] = entries
        return True
    entries.append(now)
    _RATE_LIMIT[key] = entries
    return False


def generate_captcha():
    tipe = random.choice(["tambah", "kurang", "kali", "bagi", "text"])

    if tipe == "tambah":
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        res = a + b
        return f"Berapa hasil {a} + {b} ?", str(res), "tambah"
    if tipe == "kurang":
        a = random.randint(10, 30)
        b = random.randint(1, 9)
        res = a - b
        return f"Berapa hasil {a} - {b} ?", str(res), "kurang"
    if tipe == "kali":
        a = random.randint(2, 10)
        b = random.randint(2, 10)
        res = a * b
        return f"Berapa hasil {a} × {b} ?", str(res), "kali"
    if tipe == "bagi":
        b = random.randint(2, 10)
        res = random.randint(2, 10)
        a = b * res
        return f"Berapa hasil {a} ÷ {b} ?", str(res), "bagi"
    chars = string.ascii_uppercase + string.digits
    code = "".join(random.choice(chars) for _ in range(5))
    return f"Ketik kode ini: {code}", code, "text"


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    user = None
    if "captcha_q" not in session or request.args.get("new") == "1" or request.method == "GET":
        q, a, tipe = generate_captcha()
        session["captcha_q"] = q
        session["captcha_a"] = a
        session["captcha_type"] = tipe

    conn = get_db()
    res = conn.execute("SELECT nilai FROM pengaturan WHERE kunci='logo_web'").fetchone()
    logo = res["nilai"] if res else ""
    bg = conn.execute("SELECT nilai FROM pengaturan WHERE kunci='bg_login'").fetchone()
    bg = bg["nilai"] if bg else ""

    if request.method == "POST":
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
        if _rate_limited(f"login:{ip}", limit=10, window_seconds=300):
            error = "Terlalu banyak percobaan. Coba lagi beberapa menit."
            return render_template(
                "login.html",
                error=error,
                question=session.get("captcha_q"),
                logo=logo,
                bg=bg,
                captcha_type=session.get("captcha_type", "tambah"),
            )
        user_in = sanitize_text(request.form.get("username", ""), 50)
        pass_in = sanitize_text(request.form.get("password", ""), 64)
        capt_in = sanitize_text(request.form.get("captcha", ""), 10)
        if not user_in or not pass_in or not capt_in:
            error = "Mohon lengkapi semua field login."
        elif len(user_in) > 50 or len(pass_in) > 64:
            error = "Username atau password terlalu panjang."
        elif capt_in.upper() != session["captcha_a"].upper():
            error = "Captcha Salah! Hitung/Ketik dengan benar."
        else:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password= ?",
                (user_in, pass_in),
            ).fetchone()
            if user:
                session["user_id"] = user["id"]
                session["role"] = user["role"]
                session["nama"] = user["nama_lengkap"]
                session["pin_required"] = user["pin_6digit"]
                session.pop("captcha_q", None)
                return redirect(url_for("auth.verify_pin"))
            error = "Username atau Password Salah"
        q, a, tipe = generate_captcha()
        session["captcha_q"] = q
        session["captcha_a"] = a
        session["captcha_type"] = tipe

    return render_template(
        "login.html",
        error=error,
        question=session.get("captcha_q"),
        logo=logo,
        bg=bg,
        captcha_type=session.get("captcha_type", "tambah"),
    )


@bp.route("/verify_pin", methods=["GET", "POST"])
def verify_pin():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    error = None
    conn = get_db()
    res = conn.execute("SELECT nilai FROM pengaturan WHERE kunci='logo_web'").fetchone()
    logo = res["nilai"] if res else ""
    bg = conn.execute("SELECT nilai FROM pengaturan WHERE kunci='bg_verify_pin'").fetchone()
    bg_verify = bg["nilai"] if bg else ""
    if request.method == "POST":
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
        if _rate_limited(f"pin:{ip}", limit=10, window_seconds=300):
            error = "Terlalu banyak percobaan. Coba lagi beberapa menit."
            return render_template("verify_pin.html", error=error, logo=logo, bg=bg_verify)
        pin_input = sanitize_text(request.form.get("pin", ""), 6)
        if not pin_input:
            error = "PIN wajib diisi."
        elif not pin_input.isdigit() or len(pin_input) != 6:
            error = "PIN harus 6 digit angka."
        elif pin_input == session.get("pin_required"):
            session.pop("pin_required", None)
            return redirect(url_for("dashboard.dashboard"))
        else:
            error = "PIN Salah! Coba lagi."
    return render_template("verify_pin.html", error=error, logo=logo, bg=bg_verify)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("public.landing_page"))
from ..utils import sanitize_text

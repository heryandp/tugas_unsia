import json
from datetime import datetime

from flask import render_template, session

from . import sock
from .db import get_db


_clients = set()


@sock.route("/chatroom")
def chatroom(ws):
    _clients.add(ws)
    try:
        while True:
            message = ws.receive()
            if message is None:
                break
            try:
                payload = json.loads(message)
            except Exception:
                payload = {}
            text = (payload.get("chat_message") or payload.get("message") or "").strip()
            if not text:
                continue
            nama = session.get("nama", "Anonim")
            role = session.get("role", "guest")
            tgl = datetime.now().strftime("%d-%m-%Y %H:%M")

            conn = get_db()
            conn.execute(
                "INSERT INTO diskusi (pengirim, role_pengirim, pesan, tanggal) VALUES (?, ?, ?, ?)",
                (nama, role, text, tgl),
            )
            conn.commit()

            html = render_template(
                "partials/chat_message.html",
                c={"pengirim": nama, "role_pengirim": role, "pesan": text, "tanggal": tgl},
            )

            dead = []
            for client in _clients:
                try:
                    client.send(html)
                except Exception:
                    dead.append(client)
            for d in dead:
                _clients.discard(d)
    finally:
        _clients.discard(ws)

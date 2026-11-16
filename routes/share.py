from datetime import datetime, timezone
from io import BytesIO
import os
import uuid
from urllib.parse import quote

from flask import (
    Blueprint,
    Response,
    current_app,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from crypto import (
    CryptoKeyError,
    decrypt_data,
    decrypt_file,
    decrypt_key_rsa,
    encrypt_data,
    encrypt_file,
    encrypt_key_rsa,
    generate_rsa_keys,
    generate_symmetric_key,
    unwrap_key,
    wrap_key,
)
from models import AccessRequest, PrivateDocument, StrokeRecord, User, db

share_bp = Blueprint("share", __name__, url_prefix="/share")


def _upload_dir() -> str:
    path = os.path.join(current_app.instance_path, "uploads")
    os.makedirs(path, exist_ok=True)
    return path


def _current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None


@share_bp.route("/", strict_slashes=False, methods=["GET"])
def share_dashboard():
    user = _current_user()
    if not user:
        return redirect("/login")

    other_users = (
        db.session.query(User)
        .filter(User.id != user.id)
        .order_by(User.username.asc())
        .all()
    )
    incoming = (
        db.session.query(AccessRequest)
        .filter_by(owner_id=user.id)
        .order_by(AccessRequest.created_at.desc())
        .all()
    )
    outgoing = (
        db.session.query(AccessRequest)
        .filter_by(requester_id=user.id)
        .order_by(AccessRequest.created_at.desc())
        .all()
    )

    outbox_keys = session.get("outbox_keys", {})
    wa_links = {
        req_id: f"https://wa.me/?text={quote('Encrypted Key Stroke App: ' + enc_key)}"
        for req_id, enc_key in outbox_keys.items()
    }
    mailto_links = {
        req_id: f"mailto:?subject={quote('Encrypted Key Stroke App')}&body={quote(enc_key)}"
        for req_id, enc_key in outbox_keys.items()
    }

    return render_template(
        "share.html",
        active_tab="access",
        user=user,
        other_users=other_users,
        incoming=incoming,
        outgoing=outgoing,
        outbox_keys=outbox_keys,
        wa_links=wa_links,
        mailto_links=mailto_links,
        msg=session.pop("share_msg", None),
        err=session.pop("share_err", None),
    )


@share_bp.route("/documents", methods=["GET"])
def share_documents():
    user = _current_user()
    if not user:
        return redirect("/login")

    my_docs = (
        db.session.query(PrivateDocument)
        .filter_by(user_id=user.id)
        .order_by(PrivateDocument.created_at.desc())
        .all()
    )
    return render_template(
        "share_documents.html",
        active_tab="documents",
        user=user,
        my_docs=my_docs,
        msg=session.pop("share_msg", None),
        err=session.pop("share_err", None),
    )


@share_bp.route("/keys", methods=["GET"])
def share_keys():
    user = _current_user()
    if not user:
        return redirect("/login")

    return render_template(
        "share_keys.html",
        active_tab="keys",
        user=user,
        has_pending_pem=bool(session.get("pending_pem")),
        msg=session.pop("share_msg", None),
        err=session.pop("share_err", None),
    )


@share_bp.route("/keys/generate", methods=["POST"])
def generate_keys():
    user = _current_user()
    if not user:
        return redirect("/login")

    public_key, private_key = generate_rsa_keys()
    user.public_key = public_key
    db.session.commit()

    session["pending_pem"] = private_key
    session["share_msg"] = "Pasangan kunci RSA berhasil dibuat. Segera unduh file .pem Anda."
    return redirect(url_for("share.share_keys"))


@share_bp.route("/keys/download", methods=["GET"])
def download_pem():
    user = _current_user()
    if not user:
        return redirect("/login")

    pem_data = session.pop("pending_pem", None)
    if not pem_data:
        session["share_err"] = "Tidak ada file .pem baru untuk diunduh. Generate ulang jika kunci hilang."
        return redirect(url_for("share.share_keys"))

    filename = f"{secure_filename(user.username)}_private.pem"
    return Response(
        pem_data,
        mimetype="application/x-pem-file",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@share_bp.route("/documents/upload", methods=["POST"])
def upload_document():
    user = _current_user()
    if not user:
        return redirect("/login")

    uploaded = request.files.get("document")
    if not uploaded or not uploaded.filename:
        session["share_err"] = "Pilih file gambar atau dokumen terlebih dahulu."
        return redirect(url_for("share.share_documents"))

    raw_bytes = uploaded.read()
    if not raw_bytes or len(raw_bytes) > 5 * 1024 * 1024:
        session["share_err"] = "Ukuran file harus antara 1 byte hingga 5 MB."
        return redirect(url_for("share.share_documents"))

    doc_key = generate_symmetric_key()
    enc_filename = f"doc_{user.id}_{uuid.uuid4().hex}.enc"
    with open(os.path.join(_upload_dir(), enc_filename), "wb") as f:
        f.write(encrypt_file(raw_bytes, doc_key))

    doc = PrivateDocument(
        user_id=user.id,
        filename=secure_filename(uploaded.filename) or "document",
        mime_type=uploaded.mimetype or "application/octet-stream",
        encrypted_filepath=enc_filename,
        wrapped_key=wrap_key(doc_key),
    )
    db.session.add(doc)
    db.session.commit()

    session["share_msg"] = f"File '{doc.filename}' berhasil dienkripsi dan disimpan."
    return redirect(url_for("share.share_documents"))


@share_bp.route("/documents/<int:doc_id>", methods=["GET"])
def view_own_document(doc_id):
    user = _current_user()
    if not user:
        return redirect("/login")

    doc = db.session.get(PrivateDocument, doc_id)
    if not doc or doc.user_id != user.id:
        return "Dokumen tidak ditemukan", 404

    file_path = os.path.join(_upload_dir(), doc.encrypted_filepath)
    if not os.path.exists(file_path):
        return "File terenkripsi tidak ditemukan", 404

    with open(file_path, "rb") as f:
        raw_bytes = decrypt_file(f.read(), unwrap_key(doc.wrapped_key))

    return send_file(
        BytesIO(raw_bytes),
        mimetype=doc.mime_type,
        as_attachment=request.args.get("download") == "1",
        download_name=doc.filename,
    )


@share_bp.route("/documents/<int:doc_id>/delete", methods=["POST"])
def delete_own_document(doc_id):
    user = _current_user()
    if not user:
        return redirect("/login")

    doc = db.session.get(PrivateDocument, doc_id)
    if doc and doc.user_id == user.id:
        file_path = os.path.join(_upload_dir(), doc.encrypted_filepath)
        if os.path.exists(file_path):
            os.remove(file_path)
        db.session.delete(doc)
        db.session.commit()
        session["share_msg"] = f"File '{doc.filename}' dihapus."

    return redirect(url_for("share.share_documents"))


@share_bp.route("/request", methods=["POST"])
def create_request():
    user = _current_user()
    if not user:
        return redirect("/login")

    if not user.public_key:
        session["share_err"] = "Buat pasangan kunci RSA (.pem) terlebih dahulu sebelum meminta akses."
        return redirect(url_for("share.share_keys"))

    owner_id = request.form.get("owner_id", type=int)
    owner = db.session.get(User, owner_id) if owner_id else None
    if not owner or owner.id == user.id:
        session["share_err"] = "Pengguna tujuan tidak valid."
        return redirect(url_for("share.share_dashboard"))

    existing = (
        db.session.query(AccessRequest)
        .filter_by(requester_id=user.id, owner_id=owner.id, status="PENDING")
        .first()
    )
    if existing:
        session["share_err"] = f"Permintaan ke {owner.username} masih menunggu persetujuan."
        return redirect(url_for("share.share_dashboard"))

    db.session.add(AccessRequest(requester_id=user.id, owner_id=owner.id, status="PENDING"))
    db.session.commit()

    session["share_msg"] = f"Permintaan akses dikirim ke {owner.username}."
    return redirect(url_for("share.share_dashboard"))


@share_bp.route("/approve/<int:req_id>", methods=["POST"])
def approve_request(req_id):
    user = _current_user()
    if not user:
        return redirect("/login")

    req = db.session.get(AccessRequest, req_id)
    if not req or req.owner_id != user.id or req.status != "PENDING":
        session["share_err"] = "Permintaan tidak ditemukan atau sudah diproses."
        return redirect(url_for("share.share_dashboard"))

    if not req.requester or not req.requester.public_key:
        session["share_err"] = "Peminta akses belum memiliki RSA public key."
        return redirect(url_for("share.share_dashboard"))

    k_share = generate_symmetric_key()

    # Kumpulkan data rekam medis pemilik untuk dienkripsi dengan K_share
    records_data = []
    owner_records = db.session.query(StrokeRecord).filter_by(user_id=user.id).all()
    for rec in owner_records:
        try:
            payload = decrypt_data(rec.encrypted_payload)
        except Exception:
            payload = {"name": "Tidak dapat didekripsi"}
        payload["risk_score"] = round(rec.risk_score * 100, 1)
        payload["created_at"] = rec.created_at.strftime("%Y-%m-%d %H:%M") if rec.created_at else "-"
        records_data.append(payload)

    # Salin dan enkripsi ulang gambar/dokumen pemilik dengan K_share
    shared_docs = []
    owner_docs = db.session.query(PrivateDocument).filter_by(user_id=user.id).all()
    for doc in owner_docs:
        src_path = os.path.join(_upload_dir(), doc.encrypted_filepath)
        if not os.path.exists(src_path):
            continue
        with open(src_path, "rb") as f:
            plain_bytes = decrypt_file(f.read(), unwrap_key(doc.wrapped_key))

        shared_name = f"shared_{req.id}_{doc.id}.enc"
        with open(os.path.join(_upload_dir(), shared_name), "wb") as f:
            f.write(encrypt_file(plain_bytes, k_share))

        shared_docs.append({
            "filename": doc.filename,
            "mime_type": doc.mime_type,
            "enc_path": shared_name,
        })

    req.shared_payload = encrypt_data({"records": records_data, "documents": shared_docs}, key=k_share)
    req.wrapped_sym_key = wrap_key(k_share)
    req.status = "APPROVED"
    req.approved_at = datetime.now(timezone.utc)
    db.session.commit()

    # Enkripsi K_share dengan RSA public key peminta untuk dikirim via WA/Email
    outbox = session.get("outbox_keys", {})
    outbox[str(req.id)] = encrypt_key_rsa(k_share, req.requester.public_key)
    session["outbox_keys"] = outbox

    session["share_msg"] = f"Akses untuk {req.requester.username} disetujui. Salin dan kirim ciphertext kunci lewat WA atau Email."
    return redirect(url_for("share.share_dashboard"))


@share_bp.route("/revoke/<int:req_id>", methods=["POST"])
def revoke_request(req_id):
    user = _current_user()
    if not user:
        return redirect("/login")

    req = db.session.get(AccessRequest, req_id)
    if req and req.owner_id == user.id:
        for fname in os.listdir(_upload_dir()):
            if fname.startswith(f"shared_{req.id}_"):
                os.remove(os.path.join(_upload_dir(), fname))
        req.status = "REVOKED"
        req.wrapped_sym_key = None
        req.shared_payload = None
        db.session.commit()

        outbox = session.get("outbox_keys", {})
        outbox.pop(str(req.id), None)
        session["outbox_keys"] = outbox
        session["share_msg"] = "Akses berhasil dicabut."

    return redirect(url_for("share.share_dashboard"))


@share_bp.route("/unlock/<int:req_id>", methods=["GET", "POST"])
def unlock_shared_data(req_id):
    user = _current_user()
    if not user:
        return redirect("/login")

    req = db.session.get(AccessRequest, req_id)
    if not req or req.requester_id != user.id or req.status != "APPROVED":
        session["share_err"] = "Akses tidak tersedia atau belum disetujui."
        return redirect(url_for("share.share_dashboard"))

    error = None
    bundle = None

    if request.method == "POST":
        enc_key = request.form.get("encrypted_key", "").strip()
        pem_file = request.files.get("private_key_file")
        pem_text = request.form.get("private_key_text", "").strip()

        if pem_file and pem_file.filename:
            pem_text = pem_file.read().decode("utf-8", errors="ignore").strip()

        if not enc_key or not pem_text:
            error = "Masukkan ciphertext kunci dari WA/Email dan file atau teks Private Key (.pem)."
        else:
            try:
                sym_key = decrypt_key_rsa(enc_key, pem_text)
                bundle = decrypt_data(req.shared_payload, key=sym_key)
                share_keys = session.get("share_keys", {})
                share_keys[str(req.id)] = sym_key
                session["share_keys"] = share_keys
            except (CryptoKeyError, Exception):
                error = "Dekripsi gagal. Pastikan ciphertext kunci dan file .pem sesuai."

    return render_template(
        "share_view.html",
        active_tab="access",
        req=req,
        bundle=bundle,
        error=error,
    )


@share_bp.route("/file/<int:req_id>/<int:idx>", methods=["GET"])
def serve_shared_file(req_id, idx):
    user = _current_user()
    if not user:
        return redirect("/login")

    req = db.session.get(AccessRequest, req_id)
    if not req or req.requester_id != user.id or req.status != "APPROVED":
        return "Akses ditolak", 403

    sym_key = session.get("share_keys", {}).get(str(req_id))
    if not sym_key:
        return "Kunci belum dibuka", 403

    bundle = decrypt_data(req.shared_payload, key=sym_key)
    docs = bundle.get("documents", [])
    if idx < 0 or idx >= len(docs):
        return "File tidak ditemukan", 404

    doc_info = docs[idx]
    file_path = os.path.join(_upload_dir(), doc_info["enc_path"])
    if not os.path.exists(file_path):
        return "File terenkripsi tidak ditemukan", 404

    with open(file_path, "rb") as f:
        raw_bytes = decrypt_file(f.read(), sym_key)

    return send_file(
        BytesIO(raw_bytes),
        mimetype=doc_info["mime_type"],
        as_attachment=request.args.get("download") == "1",
        download_name=doc_info["filename"],
    )

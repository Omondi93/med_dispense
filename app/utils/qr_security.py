import hmac
import hashlib
import os
import base64
import uuid


# -------------------------
# 🔐 KEY MANAGEMENT
# -------------------------

def _get_secret_key(secret_key=None):
    if secret_key is None:
        secret_key = os.environ.get("QR_SECRET_KEY")

    if not secret_key:
        raise ValueError("QR_SECRET_KEY is not set. This is a security risk.")

    if isinstance(secret_key, str):
        secret_key = secret_key.encode("utf-8")

    return secret_key


# -------------------------
# 🧠 DATA NORMALIZATION
# -------------------------

def _normalize_data(batch_id, medicine_id, manufacture_date, expiry_date, serial=None):
    base = f"{int(batch_id)}|{int(medicine_id)}|{manufacture_date}|{expiry_date}"

    if serial:
        return f"{base}|{serial}"

    return base


# -------------------------
# 🔐 SIGNATURE
# -------------------------

def generate_signature(batch_id, medicine_id, manufacture_date, expiry_date, serial=None, secret_key=None):
    key = _get_secret_key(secret_key)

    data_string = _normalize_data(
        batch_id,
        medicine_id,
        manufacture_date,
        expiry_date,
        serial
    )

    signature = hmac.new(
        key,
        data_string.encode("utf-8"),
        hashlib.sha256
    ).digest()

    # ✅ strip '=' padding
    return base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")


def verify_signature(batch_id, medicine_id, manufacture_date, expiry_date, signature, serial=None, secret_key=None):
    # ✅ restore padding before comparison
    padded_signature = signature + "=" * (-len(signature) % 4)

    expected = generate_signature(
        batch_id,
        medicine_id,
        manufacture_date,
        expiry_date,
        serial,
        secret_key
    )

    return hmac.compare_digest(expected, padded_signature)


# -------------------------
# 🔳 SINGLE QR
# -------------------------

def generate_qr_payload(batch_id, medicine_id, manufacture_date, expiry_date, secret_key=None):
    signature = generate_signature(
        batch_id,
        medicine_id,
        manufacture_date,
        expiry_date,
        secret_key=secret_key
    )

    return f"{batch_id}|{medicine_id}|{manufacture_date}|{expiry_date}|{signature}"


# -------------------------
# 🏭 BULK QR
# -------------------------

def generate_qr_payload_with_serial(batch_id, medicine_id, manufacture_date, expiry_date, secret_key=None):
    serial = str(uuid.uuid4())

    signature = generate_signature(
        batch_id,
        medicine_id,
        manufacture_date,
        expiry_date,
        serial=serial,
        secret_key=secret_key
    )

    payload = f"{batch_id}|{medicine_id}|{manufacture_date}|{expiry_date}|{serial}|{signature}"

    return payload, serial, signature


# -------------------------
# 📦 PARSER
# -------------------------

def parse_qr_payload(payload):
    try:
        parts = payload.split("|")

        if len(parts) == 5:
            return {
                "batch_id": int(parts[0]),
                "medicine_id": int(parts[1]),
                "manufacture_date": parts[2],
                "expiry_date": parts[3],
                "serial": None,
                "signature": parts[4],
            }

        elif len(parts) == 6:
            return {
                "batch_id": int(parts[0]),
                "medicine_id": int(parts[1]),
                "manufacture_date": parts[2],
                "expiry_date": parts[3],
                "serial": parts[4],
                "signature": parts[5],
            }

        return None

    except Exception:
        return None
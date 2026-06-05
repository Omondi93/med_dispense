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
        raise ValueError(
            "QR_SECRET_KEY is not set. This is a security risk."
        )

    if isinstance(secret_key, str):
        secret_key = secret_key.encode("utf-8")

    return secret_key


# -------------------------
# 🧠 DATA NORMALIZATION
# -------------------------

def _normalize_data(
    batch_id,
    medicine_id,
    manufacture_date,
    expiry_date,
    serial=None
):
    base = (
        f"{int(batch_id)}|"
        f"{int(medicine_id)}|"
        f"{manufacture_date}|"
        f"{expiry_date}"
    )

    if serial:
        return f"{base}|{serial}"

    return base


# -------------------------
# 🔐 SIGNATURE GENERATION
# -------------------------

def generate_signature(
    batch_id,
    medicine_id,
    manufacture_date,
    expiry_date,
    serial=None,
    secret_key=None
):
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

    return base64.urlsafe_b64encode(
        signature
    ).decode("utf-8").rstrip("=")


# -------------------------
# ✅ SIGNATURE VERIFICATION
# -------------------------

def verify_signature(
    batch_id,
    medicine_id,
    manufacture_date,
    expiry_date,
    signature,
    serial=None,
    secret_key=None
):
    expected = generate_signature(
        batch_id,
        medicine_id,
        manufacture_date,
        expiry_date,
        serial,
        secret_key
    )

    return hmac.compare_digest(
        expected,
        signature
    )


# -------------------------
# 🔳 SINGLE QR PAYLOAD
# -------------------------

def generate_qr_payload(
    batch_id,
    medicine_id,
    manufacture_date,
    expiry_date,
    secret_key=None
):
    signature = generate_signature(
        batch_id,
        medicine_id,
        manufacture_date,
        expiry_date,
        secret_key=secret_key
    )

    return (
        f"{batch_id}|"
        f"{medicine_id}|"
        f"{manufacture_date}|"
        f"{expiry_date}|"
        f"{signature}"
    )


# -------------------------
# 🏭 BULK QR PAYLOAD
# -------------------------

def generate_qr_payload_with_serial(
    batch_id,
    medicine_id,
    manufacture_date,
    expiry_date,
    secret_key=None
):
    serial = str(uuid.uuid4())

    signature = generate_signature(
        batch_id,
        medicine_id,
        manufacture_date,
        expiry_date,
        serial=serial,
        secret_key=secret_key
    )

    payload = (
        f"{batch_id}|"
        f"{medicine_id}|"
        f"{manufacture_date}|"
        f"{expiry_date}|"
        f"{serial}|"
        f"{signature}"
    )

    return payload, serial, signature


# -------------------------
# 📦 PAYLOAD PARSER
# -------------------------

def parse_qr_payload(payload):
    try:
        parts = payload.split("|")

        # Single QR
        if len(parts) == 5:

            return {
                "batch_id": int(parts[0]),
                "medicine_id": int(parts[1]),
                "manufacture_date": parts[2],
                "expiry_date": parts[3],
                "serial": None,
                "signature": parts[4]
            }

        # Bulk QR
        elif len(parts) == 6:

            return {
                "batch_id": int(parts[0]),
                "medicine_id": int(parts[1]),
                "manufacture_date": parts[2],
                "expiry_date": parts[3],
                "serial": parts[4],
                "signature": parts[5]
            }

        raise ValueError("Invalid QR payload format")

    except Exception:
        return None
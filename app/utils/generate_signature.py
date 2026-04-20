import base64
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding


_KEY_PATH = Path(__file__).parent / "private_key.pem"


def _load_private_key(pem_path: Path | str | None = None):
    """Load an RSA private key from a PEM file."""
    path = Path(pem_path) if pem_path else _KEY_PATH
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def _sign_with_rsa(payload: str, private_key_path: Path | str | None = None) -> str:
    """Sign a UTF-8 string with RSA PKCS#1 v1.5 + SHA-256 and return Base64."""
    private_key = _load_private_key(private_key_path)
    raw_signature = private_key.sign(
        payload.encode("utf-8"),
        asym_padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.b64encode(raw_signature).decode("utf-8")


def minify_lowercase_body(body: dict[str, Any] | list[Any] | str | None) -> str:
    """
    Convert request body into the same normalized form used by backend validation.

    - dict/list: JSON minified with stable separators
    - str: whitespace removed for spaces, tabs, and newlines
    - None: empty string
    """
    if body is None:
        return ""

    if isinstance(body, (dict, list)):
        raw = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
    else:
        raw = str(body)

    return raw.replace("\n", "").replace(" ", "").replace("\t", "").lower()


def generate_body_signature(
    body: dict[str, Any] | list[Any] | str | None,
    private_key_path: Path | str | None = None,
) -> str:
    """Generate the intermediate RSA signature for the normalized request body."""
    normalized_body = minify_lowercase_body(body)
    return _sign_with_rsa(normalized_body, private_key_path)


def build_data_to_sign(
    method: str,
    canonical_path: str,
    app_id: str,
    timestamp: str,
    body: dict[str, Any] | list[Any] | str | None = None,
    private_key_path: Path | str | None = None,
) -> str:
    """Construct the exact string expected by the current backend validator."""
    body_signature = generate_body_signature(body, private_key_path)
    return f"{method.upper()}{canonical_path}{body_signature}{app_id}{timestamp}"


def generate_request_signature(
    method: str,
    canonical_path: str,
    app_id: str,
    timestamp: str,
    body: dict[str, Any] | list[Any] | str | None = None,
    private_key_path: Path | str | None = None,
) -> str:
    """Generate the final X-Signature value."""
    data_to_sign = build_data_to_sign(
        method=method,
        canonical_path=canonical_path,
        app_id=app_id,
        timestamp=timestamp,
        body=body,
        private_key_path=private_key_path,
    )
    return _sign_with_rsa(data_to_sign, private_key_path)


def generate_auth_headers(
    method: str,
    canonical_path: str,
    app_id: str,
    body: dict[str, Any] | list[Any] | str | None = None,
    timestamp: str | None = None,
    private_key_path: Path | str | None = None,
    tz_offset_hours: int = 7,
) -> dict[str, str]:
    """Build the auth headers required by the backend."""
    if timestamp is None:
        tz = timezone(timedelta(hours=tz_offset_hours))
        timestamp = datetime.now(tz).strftime(f"%Y-%m-%dT%H:%M:%S+{tz_offset_hours:02d}:00")

    x_signature = generate_request_signature(
        method=method,
        canonical_path=canonical_path,
        app_id=app_id,
        timestamp=timestamp,
        body=body,
        private_key_path=private_key_path,
    )

    return {
        "X-App-Id": app_id,
        "X-Timestamp": timestamp,
        "X-Signature": x_signature,
    }


if __name__ == "__main__":
    APP_ID = "a949d092-a3b9-45d9-bf6e-6a86ce1e0661"
    tz = timezone(timedelta(hours=7))
    TIMESTAMP = datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S+07:00")

    no_aggr = "30003037799"  # Replace with the actual value as needed
    canonical_path = f"/integration/v1/api/item/contracts-file?noAggr={no_aggr}"

    headers = generate_auth_headers(
        method="GET",
        canonical_path=canonical_path,
        app_id=APP_ID,
        body=None,
        timestamp=TIMESTAMP,
    )

    print("\nHeaders:")
    for key, value in headers.items():
        print(f"  {key}: {value}")

from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit

from app.config.settings import settings
from app.utils.generate_signature import generate_auth_headers


def build_timestamp() -> str:
    tz = timezone(timedelta(hours=settings.SIGNATURE_TZ_OFFSET_HOURS))
    return datetime.now(tz).strftime(
        f"%Y-%m-%dT%H:%M:%S+{settings.SIGNATURE_TZ_OFFSET_HOURS:02d}:00"
    )


def build_canonical_path(
    url: str,
    params: dict[str, Any] | None = None,
) -> str:
    parsed_url = urlsplit(url)
    configured_path = urlsplit(settings.CANONICAL_PATH or "").path
    request_path = parsed_url.path or configured_path

    if configured_path and request_path.endswith(configured_path):
        canonical_path = configured_path
    elif configured_path:
        canonical_path = configured_path
    else:
        canonical_path = request_path

    query_pairs = parse_qsl(parsed_url.query, keep_blank_values=True)
    if params:
        for key, value in params.items():
            if isinstance(value, (list, tuple)):
                for item in value:
                    query_pairs.append((key, item))
            else:
                query_pairs.append((key, value))

    query_string = urlencode(query_pairs, doseq=True)
    if query_string:
        return f"{canonical_path}?{query_string}"

    return canonical_path


def generate_headers(
    method: str,
    url: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | list[Any] | str | None = None,
) -> dict[str, str]:
    canonical_path = build_canonical_path(url=url, params=params)

    if settings.SIGNATURE_MODE == "static":
        headers = {
            "X-App-Id": settings.APP_ID,
            "X-Timestamp": build_timestamp(),
            "X-Signature": settings.STATIC_SIGNATURE,
        }
    else:
        headers = generate_auth_headers(
            method=method,
            canonical_path=canonical_path,
            app_id=settings.APP_ID,
            body=body,
            private_key_path=settings.PRIVATE_KEY_PATH,
            tz_offset_hours=settings.SIGNATURE_TZ_OFFSET_HOURS,
        )

    print("Canonical Path:", canonical_path)
    print("Signature:", headers.get("X-Signature"))

    if settings.CHANNEL_ID:
        headers["Channel-Id"] = settings.CHANNEL_ID
    # if settings.API_KEY:
    #     headers["APIKey"] = settings.API_KEY

    return headers
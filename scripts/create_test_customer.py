"""Create (or verify) the isolated customer used by storefront E2E tests.

This script deliberately uses Medusa's public customer-authentication contract,
not SQL.  It is safe to run repeatedly: an existing account is authenticated
and left unchanged; a missing account is registered and then created.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def load_env(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Environment file not found: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def request_json(
    url: str, payload: dict[str, str], headers: dict[str, str]
) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, method="POST", headers=headers)
    try:
        with urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8") or "{}")
    except HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")
        try:
            return error.code, json.loads(response_body or "{}")
        except json.JSONDecodeError:
            return error.code, {"message": response_body}


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"{name} must be set")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env-file", default=".env", help="Framework environment file."
    )
    args = parser.parse_args()
    load_env(Path(args.env_file))

    backend_url = required("BACKEND_URL").rstrip("/")
    email = required("TEST_CUSTOMER_EMAIL")
    password = required("TEST_CUSTOMER_PASSWORD")
    headers = {"Content-Type": "application/json"}
    if publishable_key := os.getenv("PUBLISHABLE_API_KEY", "").strip():
        headers["x-publishable-api-key"] = publishable_key

    login_url = f"{backend_url}/auth/customer/emailpass"
    status, response = request_json(
        login_url, {"email": email, "password": password}, headers
    )
    if status == 200 and response.get("token"):
        print(f"Customer already exists and credentials were verified: {email}")
        return 0

    register_url = f"{backend_url}/auth/customer/emailpass/register"
    status, response = request_json(
        register_url, {"email": email, "password": password}, headers
    )
    token = response.get("token")
    if status not in (200, 201) or not token:
        message = response.get("message", "no error message returned")
        raise RuntimeError(f"Customer registration failed ({status}): {message}")

    customer_headers = {**headers, "Authorization": f"Bearer {token}"}
    status, response = request_json(
        f"{backend_url}/store/customers",
        {
            "email": email,
            "first_name": os.getenv("TEST_FIRST_NAME", "Playwright"),
            "last_name": os.getenv("TEST_LAST_NAME", "Customer"),
        },
        customer_headers,
    )
    if status not in (200, 201):
        message = response.get("message", "no error message returned")
        raise RuntimeError(f"Customer creation failed ({status}): {message}")
    print(f"Created storefront test customer: {email}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError, URLError, ValueError) as error:
        print(f"Seed failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error

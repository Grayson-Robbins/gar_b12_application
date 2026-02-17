import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone

import requests

# ---------------------------------------------------------------------------
# Configuration — non-secret values are read from environment variables so
# the workflow can inject them at run time; the signing secret is stored as
# a GitHub Actions secret and injected via the environment.
# ---------------------------------------------------------------------------

SUBMISSION_URL = "https://b12.io/apply/submission"

# These are injected by the GitHub Actions workflow (see submit.yml).
NAME = os.environ["APPLICANT_NAME"]
EMAIL = os.environ["APPLICANT_EMAIL"]
RESUME_LINK = os.environ["RESUME_LINK"]
REPOSITORY_LINK = os.environ["REPOSITORY_LINK"]
ACTION_RUN_LINK = os.environ["ACTION_RUN_LINK"]
SIGNING_SECRET = os.environ["SIGNING_SECRET"]  # stored as a GitHub secret


def build_payload() -> bytes:
    """Build the canonicalized JSON payload required by B12.

    Requirements (from challenge spec):
    - Keys sorted alphabetically
    - Compact separators (no extra whitespace)
    - UTF-8 encoded
    - timestamp is an ISO 8601 string (UTC, with milliseconds)
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
        f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"

    data = {
        "action_run_link": ACTION_RUN_LINK,
        "email": EMAIL,
        "name": NAME,
        "repository_link": REPOSITORY_LINK,
        "resume_link": RESUME_LINK,
        "timestamp": timestamp,
    }

    # sort_keys=True + separators=(',',':') satisfies the canonical form spec.
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_payload(payload: bytes) -> str:
    """Compute HMAC-SHA256 of the payload using the signing secret.

    Returns the value for the X-Signature-256 header in the form:
        sha256=<hex-digest>
    """
    secret = SIGNING_SECRET.encode("utf-8")
    digest = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def submit(payload: bytes, signature: str) -> None:
    """POST the payload to the B12 submission endpoint."""
    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": signature,
    }

    print(f"Submitting to {SUBMISSION_URL} …")
    print(f"Payload : {payload.decode('utf-8')}")
    print(f"Signature: {signature}")

    response = requests.post(SUBMISSION_URL, data=payload, headers=headers, timeout=30)

    print(f"HTTP status: {response.status_code}")
    print(f"Response   : {response.text}")

    if response.status_code != 200:
        print("ERROR: Submission failed.", file=sys.stderr)
        sys.exit(1)

    result = response.json()
    if not result.get("success"):
        print(f"ERROR: Server reported failure: {result}", file=sys.stderr)
        sys.exit(1)

    receipt = result.get("receipt", "<no receipt in response>")
    print(f"\n✅  Submission successful!")
    print(f"    Receipt: {receipt}")


if __name__ == "__main__":
    payload = build_payload()
    signature = sign_payload(payload)
    submit(payload, signature)

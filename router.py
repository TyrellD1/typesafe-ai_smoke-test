"""Work/life prompt router using TypeSafe System One (Jev), stdlib only.

One API call per prompt, two independent Noul questions asked together:
  - is_work: could the WORK database help answer this?
  - is_life: could the LIFE database help answer this?

Both can be true -> route to both. Code owns the routing decision;
the model only supplies the two probabilities.

Usage:
    export TYPESAFE_API_KEY="..."
    python3 router.py "Do I have anything tomorrow morning?"
    python3 router.py --threshold 0.5 "Where is the Q3 planning doc?"

No third-party libs: urllib + json only.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def _load_dotenv(path: str | Path | None = None) -> None:
    """Minimal .env loader (stdlib only). Real env vars take precedence."""
    p = Path(path) if path else Path(__file__).resolve().parent / ".env"
    if not p.is_file():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()

API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
DEFAULT_THRESHOLD = 0.5

QUESTIONS = {
    "is_work": {
        "type": "noul",
        "instructions": (
            "Does this prompt ask for information that could live in the user's "
            "WORK database (job, colleagues, meetings, projects, deadlines, tasks, "
            "work messages, work documents)? Answer yes if the prompt refers to a "
            "work topic OR is ambiguous/generic enough that work info might help "
            "(e.g. schedules, availability, keyword search)."
        ),
        "criteria": {
            "true": "Work-related, or generic/ambiguous (schedule, availability, search, reminders) where work data could be relevant.",
            "false": "Clearly personal-life-only with no plausible work angle.",
        },
    },
    "is_life": {
        "type": "noul",
        "instructions": (
            "Does this prompt ask for information that could live in the user's "
            "LIFE database (personal life, family, health, home, hobbies, travel, "
            "personal finances, personal appointments)? Answer yes if the prompt "
            "refers to a personal topic OR is ambiguous/generic enough that personal "
            "info might help (e.g. schedules, availability, keyword search)."
        ),
        "criteria": {
            "true": "Personal-life-related, or generic/ambiguous (schedule, availability, search, reminders) where personal data could be relevant.",
            "false": "Clearly work-only with no plausible personal angle.",
        },
    },
}


def build_payload(prompt: str) -> dict:
    return {"state": prompt, "model": MODEL, "questions": QUESTIONS}


def call_system_one(prompt: str, timeout_s: int = 30) -> dict:
    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        raise RuntimeError("TYPESAFE_API_KEY is not set in the environment.")
    body = json.dumps(build_payload(prompt)).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"TypeSafe API HTTP {e.code}: {detail}") from e


def route_prompt(prompt: str, threshold: float = DEFAULT_THRESHOLD) -> dict:
    """Route one prompt. Returns probs, booleans, route list, and timing info.

    latency_s is measured client-side (includes network). tps_out is an
    approximation: output tokens divided by latency.
    """
    start = time.perf_counter()
    response = call_system_one(prompt)
    latency_s = time.perf_counter() - start
    work_p = float(response["answers"]["is_work"]["noul"])
    life_p = float(response["answers"]["is_life"]["noul"])
    to_work = work_p >= threshold
    to_life = life_p >= threshold
    routes = []
    if to_work:
        routes.append("work")
    if to_life:
        routes.append("life")
    usage = response.get("usage", {}) or {}
    in_tok = int(usage.get("input_tokens", 0) or 0)
    out_tok = int(usage.get("output_tokens", 0) or 0)
    return {
        "prompt": prompt,
        "work_prob": work_p,
        "life_prob": life_p,
        "to_work": to_work,
        "to_life": to_life,
        "routes": routes,
        "threshold": threshold,
        "latency_s": latency_s,
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "tps_out_approx": (out_tok / latency_s) if latency_s > 0 else 0.0,
        "usage": usage,
    }


def main(argv: list) -> int:
    threshold = DEFAULT_THRESHOLD
    args = list(argv)
    if "--threshold" in args:
        i = args.index("--threshold")
        try:
            threshold = float(args.pop(i + 1))
            args.pop(i)
        except (IndexError, ValueError):
            print("usage: router.py [--threshold 0.5] \"<prompt>\"", file=sys.stderr)
            return 2
    if not args:
        print("usage: router.py [--threshold 0.5] \"<prompt>\"", file=sys.stderr)
        return 2
    prompt = " ".join(args)
    try:
        result = route_prompt(prompt, threshold=threshold)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

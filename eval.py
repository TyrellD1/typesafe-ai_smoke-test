"""Tiny eval for the work/life router. Stdlib only.

Each case is a prompt plus the expected booleans:
  expect_work=True  -> should route to the WORK database
  expect_life=True  -> should route to the LIFE database
  both True         -> should route to BOTH

Usage:
    export TYPESAFE_API_KEY="..."
    python3 eval.py                  # full run, 30 cases
    python3 eval.py --fail-only      # only show failures/errors
    python3 eval.py --threshold 0.6  # try a different threshold

Exit code is 0 when every case passes, 1 otherwise.
"""

import sys
import time

from router import DEFAULT_THRESHOLD, route_prompt

# id, prompt, expect_work, expect_life
TEST_CASES = [
    # ---- work-only (10) ----
    ("W01", "When is my next 1:1 with Sarah from engineering?", True, False),
    ("W02", "Summarize the action items from yesterday's sprint planning.", True, False),
    ("W03", "What's the status of our Q3 OKRs?", True, False),
    ("W04", "Who approved the pull request for the billing refactor?", True, False),
    ("W05", "When is the deadline for the client proposal draft?", True, False),
    ("W06", "What did my manager say about my performance review?", True, False),
    ("W07", "Where is the Q3 planning doc for the platform team?", True, False),
    ("W08", "Remind me what we decided about the database migration in the tech review.", True, False),
    ("W09", "How many PTO days do I have left this quarter?", True, False),
    ("W10", "What was the latest message in the #incidents Slack channel?", True, False),
    # ---- life-only (10) ----
    ("L01", "When is my next dentist appointment?", False, True),
    ("L02", "What did I buy at Whole Foods last week?", False, True),
    ("L03", "What's a good dinner recipe with the chicken and broccoli I have?", False, True),
    ("L04", "Remind me what the pediatrician said about my son's allergy.", False, True),
    ("L05", "Where did I park my car last night?", False, True),
    ("L06", "What's my marathon training plan for this Saturday?", False, True),
    ("L07", "When is my mom's birthday and what did I get her last year?", False, True),
    ("L08", "How much did I spend on restaurants last month?", False, True),
    ("L09", "What time is my yoga class tonight?", False, True),
    ("L10", "Summarize the bedtime story I was writing for my daughter.", False, True),
    # ---- both (10): generic/ambiguous prompts needing both DBs ----
    ("B01", "Do I have anything scheduled tomorrow morning?", True, True),
    ("B02", "Am I free this Friday evening?", True, True),
    ("B03", 'Search everything for "Tokyo".', True, True),
    ("B04", 'Find all my notes about "budget".', True, True),
    ("B05", "What do I need to prepare for next week?", True, True),
    ("B06", 'Show me all reminders about "passport".', True, True),
    ("B07", 'Did anyone mention "dinner" recently?', True, True),
    ("B08", "What's on my todo list for today?", True, True),
    ("B09", 'Summarize my unread messages about the "contract".', True, True),
    ("B10", "Who do I need to follow up with?", True, True),
]


def run(threshold: float, fail_only: bool, sleep_s: float = 0.3) -> int:
    n = len(TEST_CASES)
    exact_ok = work_ok = life_ok = errors = 0
    lat_sum = in_sum = out_sum = 0
    lat_max = 0.0

    for i, (cid, prompt, exp_work, exp_life) in enumerate(TEST_CASES):
        try:
            r = route_prompt(prompt, threshold=threshold)
        except RuntimeError as e:
            errors += 1
            print(f"[{cid}] ERROR {prompt!r}\n       {e}")
            continue
        got_work, got_life = r["to_work"], r["to_life"]
        ok = (got_work == exp_work) and (got_life == exp_life)
        exact_ok += ok
        work_ok += got_work == exp_work
        life_ok += got_life == exp_life
        lat_sum += r["latency_s"]
        lat_max = max(lat_max, r["latency_s"])
        in_sum += r["input_tokens"]
        out_sum += r["output_tokens"]
        if fail_only and ok:
            pass
        else:
            mark = "PASS" if ok else "FAIL"
            print(
                f"[{cid}] {mark} work={int(got_work)} (exp {int(exp_work)}, p={r['work_prob']:.3f}) "
                f"life={int(got_life)} (exp {int(exp_life)}, p={r['life_prob']:.3f}) "
                f"routes={r['routes'] or ['none']} :: {prompt} "
                f"[{r['latency_s']:.2f}s, tok {r['input_tokens']}/{r['output_tokens']}, "
                f"~{r['tps_out_approx']:.1f} tok/s]"
            )
        if i < n - 1:
            time.sleep(sleep_s)

    evaluated = n - errors
    print("\n---- summary ----")
    print(f"cases:        {n} (errors: {errors})")
    if evaluated:
        print(f"exact match:  {exact_ok}/{evaluated} = {exact_ok / evaluated:.1%}")
        print(f"work label:   {work_ok}/{evaluated} = {work_ok / evaluated:.1%}")
        print(f"life label:   {life_ok}/{evaluated} = {life_ok / evaluated:.1%}")
    print(f"threshold:    {threshold}")
    if evaluated:
        print(f"avg latency:  {lat_sum / evaluated:.2f}s per call (max {lat_max:.2f}s)")
        print(f"tokens:       {in_sum} in / {out_sum} out total")
        if lat_sum > 0:
            print(f"throughput:   ~{out_sum / lat_sum:.1f} output tok/s (approx, client-side)")
    return 0 if (errors == 0 and exact_ok == evaluated) else 1


def main(argv: list) -> int:
    threshold = DEFAULT_THRESHOLD
    fail_only = False
    args = list(argv)
    if "--threshold" in args:
        i = args.index("--threshold")
        try:
            threshold = float(args.pop(i + 1))
            args.pop(i)
        except (IndexError, ValueError):
            print("usage: eval.py [--threshold 0.5] [--fail-only]", file=sys.stderr)
            return 2
    if "--fail-only" in args:
        fail_only = True
        args.remove("--fail-only")
    if args:
        print("usage: eval.py [--threshold 0.5] [--fail-only]", file=sys.stderr)
        return 2
    return run(threshold=threshold, fail_only=fail_only)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

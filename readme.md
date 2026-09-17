# Work/Life Router Test Report

We sent 30 test prompts through the router. All 30 went to the right place.

## Context

We built a small demo. It sends each prompt to the right store. There are two
stores. One holds work info like meetings and projects. The other holds life info
like health and family.

For each prompt we ask the model two yes or no questions. Could the work store
help? Could the life store help? Each answer is a number from 0 to 1. Our code says
yes when the number is 0.5 or more. Both can be yes. So a prompt like
"do I have anything tomorrow morning?" goes to both stores.

The test file is `eval.py`. It has 30 prompts we wrote by hand.
10 should go to work. 10 should go to life. 10 should go to both. We check each
one against the live model.

## At a glance

**30 out of 30 went to the right place.** There were no errors.
Clear prompts score 0.9 or more. The mixed prompts pass on both.

Closest calls (a score near 0.5): W01 (When is my next 1:1 with Sarah from engineeri...: work 0.99, life 0.46); W09 (How many PTO days do I have left this quarter...: work 0.97, life 0.42).
These could flip if we move the cutoff.

## Full results

Model `jev-latest`, threshold 0.5, one API call per row carrying both questions.

### Work-only prompts (10)

| ID | Prompt | P(work) | P(life) | Routed to | Expected | Result | Latency | Tokens in/out | ~Tok/s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W01 | When is my next 1:1 with Sarah from engineering? | 0.990 | 0.460 | work | work | pass | 0.77s | 523/39 | ~50.4 |
| W02 | Summarize the action items from yesterday's sprint planning. | 0.990 | 0.090 | work | work | pass | 0.77s | 522/39 | ~50.6 |
| W03 | What's the status of our Q3 OKRs? | 0.990 | 0.090 | work | work | pass | 3.88s | 521/39 | ~10.0 |
| W04 | Who approved the pull request for the billing refactor? | 0.980 | 0.040 | work | work | pass | 2.29s | 521/39 | ~17.0 |
| W05 | When is the deadline for the client proposal draft? | 0.980 | 0.260 | work | work | pass | 0.77s | 520/39 | ~50.6 |
| W06 | What did my manager say about my performance review? | 0.980 | 0.280 | work | work | pass | 0.83s | 520/39 | ~46.8 |
| W07 | Where is the Q3 planning doc for the platform team? | 0.990 | 0.050 | work | work | pass | 0.75s | 522/39 | ~52.2 |
| W08 | Remind me what we decided about the database migration in the tech review. | 0.980 | 0.090 | work | work | pass | 0.75s | 525/39 | ~52.1 |
| W09 | How many PTO days do I have left this quarter? | 0.970 | 0.420 | work | work | pass | 5.66s | 521/39 | ~6.9 |
| W10 | What was the latest message in the #incidents Slack channel? | 0.980 | 0.070 | work | work | pass | 0.75s | 523/39 | ~52.0 |

### Life-only prompts (10)

| ID | Prompt | P(work) | P(life) | Routed to | Expected | Result | Latency | Tokens in/out | ~Tok/s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L01 | When is my next dentist appointment? | 0.190 | 0.990 | life | life | pass | 0.73s | 517/39 | ~53.5 |
| L02 | What did I buy at Whole Foods last week? | 0.060 | 0.980 | life | life | pass | 0.81s | 520/39 | ~47.9 |
| L03 | What's a good dinner recipe with the chicken and broccoli I have? | 0.020 | 0.750 | life | life | pass | 0.86s | 524/39 | ~45.4 |
| L04 | Remind me what the pediatrician said about my son's allergy. | 0.040 | 0.990 | life | life | pass | 4.91s | 525/39 | ~7.9 |
| L05 | Where did I park my car last night? | 0.130 | 0.950 | life | life | pass | 1.00s | 519/39 | ~39.0 |
| L06 | What's my marathon training plan for this Saturday? | 0.110 | 0.970 | life | life | pass | 0.84s | 520/39 | ~46.3 |
| L07 | When is my mom's birthday and what did I get her last year? | 0.050 | 0.990 | life | life | pass | 0.77s | 525/39 | ~50.4 |
| L08 | How much did I spend on restaurants last month? | 0.060 | 0.980 | life | life | pass | 0.87s | 520/39 | ~44.7 |
| L09 | What time is my yoga class tonight? | 0.160 | 0.990 | life | life | pass | 3.47s | 518/39 | ~11.2 |
| L10 | Summarize the bedtime story I was writing for my daughter. | 0.030 | 0.970 | life | life | pass | 3.17s | 523/39 | ~12.3 |

### Ambiguous prompts, expect both (10)

| ID | Prompt | P(work) | P(life) | Routed to | Expected | Result | Latency | Tokens in/out | ~Tok/s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B01 | Do I have anything scheduled tomorrow morning? | 0.940 | 0.980 | work + life | work + life | pass | 0.98s | 518/39 | ~39.7 |
| B02 | Am I free this Friday evening? | 0.900 | 0.980 | work + life | work + life | pass | 0.81s | 517/39 | ~48.3 |
| B03 | Search everything for "Tokyo". | 0.830 | 0.840 | work + life | work + life | pass | 0.74s | 517/39 | ~52.8 |
| B04 | Find all my notes about "budget". | 0.890 | 0.940 | work + life | work + life | pass | 0.83s | 518/39 | ~47.1 |
| B05 | What do I need to prepare for next week? | 0.920 | 0.930 | work + life | work + life | pass | 2.11s | 520/39 | ~18.5 |
| B06 | Show me all reminders about "passport". | 0.730 | 0.980 | work + life | work + life | pass | 4.34s | 518/39 | ~9.0 |
| B07 | Did anyone mention "dinner" recently? | 0.660 | 0.910 | work + life | work + life | pass | 0.85s | 519/39 | ~45.8 |
| B08 | What's on my todo list for today? | 0.910 | 0.960 | work + life | work + life | pass | 0.78s | 519/39 | ~50.0 |
| B09 | Summarize my unread messages about the "contract". | 0.880 | 0.770 | work + life | work + life | pass | 0.85s | 521/39 | ~45.7 |
| B10 | Who do I need to follow up with? | 0.920 | 0.880 | work + life | work + life | pass | 0.74s | 519/39 | ~52.4 |

## Timing and cost

Each row is one API call. The call takes about **1.59 seconds**
on average (slowest was 5.66s). The whole run used
**15615 input tokens and 1170 output tokens**. That works out to
about **24.5 output tokens per second**.

A few notes on these numbers. The time is measured on our side, so it includes
the network trip. The token counts come straight from the API. The tokens per second
is our own math (output tokens divided by time), so treat it as rough. Both questions
ride in the same call, so asking the second one costs almost nothing extra. Slowest
calls this run: W09 (5.66s); L04 (4.91s); B06 (4.34s).

## How to run

```bash
cp .env.example .env   # then put your key in .env
python3 eval.py                # full run
python3 eval.py --fail-only    # only show failures
```

`router.py` holds the router (stdlib only, no third-party libs).
`eval-report.html` is the same report as a standalone page.

Run 2026-09-17 · model jev-latest · threshold 0.5.

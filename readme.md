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

Closest calls (a score near 0.5): W01 (When is my next 1:1 with Sarah from engineeri...: work 0.99, life 0.45); W09 (How many PTO days do I have left this quarter...: work 0.97, life 0.39).
These could flip if we move the cutoff.

## Full results

Model `jev-latest`, threshold 0.5, one API call per row carrying both questions.

### Work-only prompts (10)

| ID | Prompt | P(work) | P(life) | Routed to | Expected | Result |
| --- | --- | --- | --- | --- | --- | --- |
| W01 | When is my next 1:1 with Sarah from engineering? | 0.990 | 0.450 | work | work | pass |
| W02 | Summarize the action items from yesterday's sprint planning. | 0.990 | 0.100 | work | work | pass |
| W03 | What's the status of our Q3 OKRs? | 0.990 | 0.090 | work | work | pass |
| W04 | Who approved the pull request for the billing refactor? | 0.980 | 0.040 | work | work | pass |
| W05 | When is the deadline for the client proposal draft? | 0.980 | 0.230 | work | work | pass |
| W06 | What did my manager say about my performance review? | 0.980 | 0.310 | work | work | pass |
| W07 | Where is the Q3 planning doc for the platform team? | 0.990 | 0.050 | work | work | pass |
| W08 | Remind me what we decided about the database migration in the tech review. | 0.980 | 0.090 | work | work | pass |
| W09 | How many PTO days do I have left this quarter? | 0.970 | 0.390 | work | work | pass |
| W10 | What was the latest message in the #incidents Slack channel? | 0.980 | 0.060 | work | work | pass |

### Life-only prompts (10)

| ID | Prompt | P(work) | P(life) | Routed to | Expected | Result |
| --- | --- | --- | --- | --- | --- | --- |
| L01 | When is my next dentist appointment? | 0.210 | 0.990 | life | life | pass |
| L02 | What did I buy at Whole Foods last week? | 0.050 | 0.980 | life | life | pass |
| L03 | What's a good dinner recipe with the chicken and broccoli I have? | 0.020 | 0.690 | life | life | pass |
| L04 | Remind me what the pediatrician said about my son's allergy. | 0.040 | 0.990 | life | life | pass |
| L05 | Where did I park my car last night? | 0.130 | 0.950 | life | life | pass |
| L06 | What's my marathon training plan for this Saturday? | 0.120 | 0.970 | life | life | pass |
| L07 | When is my mom's birthday and what did I get her last year? | 0.050 | 0.990 | life | life | pass |
| L08 | How much did I spend on restaurants last month? | 0.060 | 0.980 | life | life | pass |
| L09 | What time is my yoga class tonight? | 0.170 | 0.980 | life | life | pass |
| L10 | Summarize the bedtime story I was writing for my daughter. | 0.020 | 0.970 | life | life | pass |

### Ambiguous prompts, expect both (10)

| ID | Prompt | P(work) | P(life) | Routed to | Expected | Result |
| --- | --- | --- | --- | --- | --- | --- |
| B01 | Do I have anything scheduled tomorrow morning? | 0.940 | 0.980 | work + life | work + life | pass |
| B02 | Am I free this Friday evening? | 0.900 | 0.980 | work + life | work + life | pass |
| B03 | Search everything for "Tokyo". | 0.830 | 0.840 | work + life | work + life | pass |
| B04 | Find all my notes about "budget". | 0.890 | 0.940 | work + life | work + life | pass |
| B05 | What do I need to prepare for next week? | 0.920 | 0.940 | work + life | work + life | pass |
| B06 | Show me all reminders about "passport". | 0.740 | 0.980 | work + life | work + life | pass |
| B07 | Did anyone mention "dinner" recently? | 0.660 | 0.900 | work + life | work + life | pass |
| B08 | What's on my todo list for today? | 0.910 | 0.960 | work + life | work + life | pass |
| B09 | Summarize my unread messages about the "contract". | 0.890 | 0.760 | work + life | work + life | pass |
| B10 | Who do I need to follow up with? | 0.920 | 0.870 | work + life | work + life | pass |

## How to run

```bash
cp .env.example .env   # then put your key in .env
python3 eval.py                # full run
python3 eval.py --fail-only    # only show failures
```

`router.py` holds the router (stdlib only, no third-party libs).
`eval-report.html` is the same report as a standalone page.

Run 2026-09-17 · model jev-latest · threshold 0.5.

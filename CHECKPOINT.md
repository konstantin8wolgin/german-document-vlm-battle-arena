# Checkpoint: German Document VLM Battle Arena

Date: 2026-06-13
Workspace: `/home/konstantin/Desktop/mdtest`
Public repo: https://github.com/konstantin8wolgin/german-document-vlm-battle-arena

## Current State

- `.env` exists locally and should contain `OPENROUTER_API_KEY=...`.
- `.env` is gitignored and must not be committed.
- Public GitHub repo was created and pushed.
- Current committed public code includes:
  - CLI package `docarena`
  - direct public-PDF manifest with 40 documents, 5 per category
  - fetch/render/run/score/report commands
  - OpenRouter image-only payload path
  - universal prompt rule: no OCR, no PDF text layer, rendered images only
  - cost estimator and `--spend --max-cost-usd` guard
  - tests for manifest, sources, rendering, OpenRouter payloads, runner, scoring, and reports

## Completed Local Execution

These steps completed successfully during the interrupted session:

```bash
set -a
source .env
set +a

python3 -m docarena fetch --allow-download --timeout-s 45
python3 -m docarena render --active-only --dpi 160
```

Results:

- 40 public PDFs downloaded into ignored `data/pdfs/`.
- selected pages rendered into ignored `data/rendered/`.
- `rendered_manifest.json` was created locally.
- Rendered corpus count observed earlier: 40 documents, 74 pages.

## Interrupted Work

The full bounded OpenRouter attempt was too large:

```bash
python3 -m docarena run --spend --max-cost-usd 6 --prompts strict_schema --output predictions/strict_schema_all_models.json
```

That would be 320 sequential vision calls: 8 models x 1 prompt x 40 docs.
It was stopped to avoid long runtime and potential spend.

A smaller smoke manifest was created locally:

```text
rendered_manifest_smoke.json
```

It contains one document: `rechnungen_001`, one rendered page.

The next attempted command was interrupted by the user before completion:

```bash
python3 -m docarena run \
  --spend \
  --max-cost-usd 1 \
  --prompts strict_schema \
  --rendered-manifest rendered_manifest_smoke.json \
  --output predictions/smoke_invoice_all_models.json
```

At checkpoint time, no `python3 -m docarena run` process is active.

## Smoke Run Completed After Resume

The one-document smoke comparison completed after resuming:

```bash
python3 -m docarena run \
  --spend \
  --max-cost-usd 1 \
  --prompts strict_schema \
  --rendered-manifest rendered_manifest_smoke.json \
  --output predictions/smoke_invoice_all_models.json
```

Result summary:

- prediction rows: 8
- statuses: `ok=5`, `malformed_json=2`, `error=1`
- local smoke leaderboard: `reports/smoke_ai_comparison.md`

Smoke ranking by valid JSON first, then latency:

| rank | model | status | latency_s |
| --- | --- | --- | --- |
| 1 | `mistralai/mistral-small-2603` | ok | 5.41 |
| 2 | `qwen/qwen3-vl-8b-instruct` | ok | 5.43 |
| 3 | `qwen/qwen3-vl-32b-instruct` | ok | 16.27 |
| 4 | `qwen/qwen3-vl-235b-a22b-instruct` | ok | 17.45 |
| 5 | `qwen/qwen2.5-vl-72b-instruct` | ok | 17.66 |
| 6 | `mistralai/mistral-medium-3-5` | malformed_json | 24.33 |
| 7 | `meta-llama/llama-3.2-11b-vision-instruct` | malformed_json | 33.38 |
| 8 | `z-ai/glm-4.6v` | error | 19.49 |

## Important Limitation

A real accuracy leaderboard still needs gold labels under `gold/*.gold.json`.
Without gold labels, the project can produce predictions and latency/status comparisons,
but it cannot produce trustworthy extraction accuracy scores.

## Recommended Resume Steps

1. Confirm the key is loaded:

```bash
cd /home/konstantin/Desktop/mdtest
set -a
source .env
set +a
test -n "$OPENROUTER_API_KEY" && echo "key loaded"
```

2. Run the one-document smoke comparison:

```bash
python3 -m docarena run \
  --spend \
  --max-cost-usd 1 \
  --prompts strict_schema \
  --rendered-manifest rendered_manifest_smoke.json \
  --output predictions/smoke_invoice_all_models.json
```

3. Inspect statuses:

```bash
python3 - <<'PY'
import json, collections
rows=json.load(open('predictions/smoke_invoice_all_models.json'))
print('rows', len(rows))
print(collections.Counter(r['status'] for r in rows))
for r in rows:
    print(r['model'], r['status'], round(r.get('latency_s', 0), 2))
PY
```

4. If smoke works, decide whether to run:

- all 8 models on one document per category, or
- one cheap model on all 40 documents, or
- the full tournament after adding concurrency/resume support.

## Safety Notes

- Do not commit `.env`, `data/`, `gold/`, `predictions/`, `scores/`, `reports/`, `rendered_manifest*.json`, or `gold_pack/`.
- The current runner is sequential and should not be used for large tournaments until resume/checkpointing and stronger actual-cost tracking are added.

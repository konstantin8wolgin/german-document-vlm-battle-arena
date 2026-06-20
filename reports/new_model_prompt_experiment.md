# New Model Prompt Experiment

Date: 2026-06-13

## Goal

Test cheaper/current vision-capable models with a stronger extraction prompt, excluding models that performed badly in the overnight run.

## Model Selection

Included:

- `qwen/qwen3-vl-32b-instruct` as the quality baseline.
- `qwen/qwen3-vl-30b-a3b-instruct` as a faster/current Qwen candidate.
- `mistralai/mistral-small-2603` as the speed baseline.
- `mistralai/mistral-large-2512` as a newer stronger Mistral candidate.
- `mistralai/ministral-14b-2512` and `mistralai/ministral-8b-2512` as cheaper newer Mistral-family candidates.
- `moonshotai/kimi-k2.5` and `moonshotai/kimi-k2.6` because Kimi was requested and supports image input in OpenRouter's model catalog.
- `google/gemma-4-26b-a4b-it` as a cheap open-weight-style vision candidate.

Excluded:

- `meta-llama/llama-3.2-11b-vision-instruct`, `z-ai/glm-4.6v`, and `mistralai/mistral-medium-3-5` because the overnight run showed many malformed/error rows.
- DeepSeek V4/V3 models because OpenRouter currently lists them as text-only, so they do not satisfy the rendered-image-only benchmark rule.

## Execution Prompt

Prompt variant: `important_info_v2` in `docarena/prompts.py`.

Architecture:

- Keep the image-only rule first.
- State the document category explicitly.
- Require exactly one JSON object.
- Use a fixed schema with typed object arrays for names, dates, numbers, and evidence.
- Add category-specific field priorities.
- Tell the model to use `null` for expected but invisible values.
- Prioritize exact German labels, identifiers, amounts, dates, parties, and evidence.

## Test Command

```bash
set -a
source .env
set +a
python3 -m docarena run \
  --spend \
  --max-cost-usd 2 \
  --prompts important_info_v2 \
  --rendered-manifest rendered_manifest_5doc_prompt_test.json \
  --models \
    qwen/qwen3-vl-32b-instruct \
    qwen/qwen3-vl-30b-a3b-instruct \
    mistralai/mistral-small-2603 \
    mistralai/mistral-large-2512 \
    mistralai/ministral-14b-2512 \
    mistralai/ministral-8b-2512 \
    moonshotai/kimi-k2.5 \
    moonshotai/kimi-k2.6 \
    google/gemma-4-26b-a4b-it \
  --output predictions/important_info_v2_new_models_5doc.json
```

Run shape:

- 5 representative documents.
- 9 rendered pages.
- 9 models.
- 45 calls.
- Estimated cost from project estimator: USD 0.81.
- Cost cap used: USD 2.00.

## Result

Output:

- `predictions/important_info_v2_new_models_5doc.json`
- `reports/important_info_v2_new_models_5doc/important_info_leaderboard.md`
- `reports/important_info_v2_new_models_5doc/important_info_leaderboard.csv`

Ranking:

| rank | model | score | ok | malformed | error | avg_latency_s |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `qwen/qwen3-vl-32b-instruct` | 0.7383 | 5 | 0 | 0 | 21.99 |
| 2 | `qwen/qwen3-vl-30b-a3b-instruct` | 0.7024 | 5 | 0 | 0 | 12.06 |
| 3 | `mistralai/ministral-14b-2512` | 0.6873 | 5 | 0 | 0 | 17.45 |
| 4 | `mistralai/mistral-small-2603` | 0.6733 | 5 | 0 | 0 | 5.69 |
| 5 | `google/gemma-4-26b-a4b-it` | 0.6527 | 5 | 0 | 0 | 15.01 |
| 6 | `mistralai/mistral-large-2512` | 0.5187 | 4 | 1 | 0 | 15.40 |
| 7 | `mistralai/ministral-8b-2512` | 0.4812 | 4 | 1 | 0 | 9.96 |
| 8 | `moonshotai/kimi-k2.5` | 0.4302 | 3 | 1 | 1 | 32.96 |
| 9 | `moonshotai/kimi-k2.6` | 0.0000 | 0 | 0 | 5 | 33.94 |

## Interpretation

- Best quality in this slice: `qwen/qwen3-vl-32b-instruct`.
- Best speed/quality candidate: `mistralai/mistral-small-2603`.
- Best new cheap candidate: `qwen/qwen3-vl-30b-a3b-instruct`.
- Best Mistral-family candidate in this new test: `mistralai/ministral-14b-2512`.
- Kimi K2.5 was unstable and slow; Kimi K2.6 failed on every tested document.
- The stronger prompt improved `mistralai/mistral-small-2603` on the same five-doc slice compared with its old strict-schema score, but `qwen/qwen3-vl-32b-instruct` scored higher with the old shorter prompt on this slice.

## Prompt Architecture Critique

- More context helps weaker models and Mistral Small, but it can slow strong Qwen models and may reduce exactness.
- JSON examples inside `.format()` strings must escape braces; tests now cover this.
- The prompt should remain one variant, not replace `strict_schema`, because prompt length and model behavior trade off differently by model.
- Next prompt fork should be a shorter `important_info_fast_v3`: keep category-specific priorities but remove long schema prose.

## Code Architecture Critique

- Good: runner now resumes and writes after every call.
- Good: rendered manifests carry categories.
- Fixed: null assistant content should be classified as malformed JSON, not as a generic error.
- Needed next: richer error/status taxonomy such as `empty_content`, `rate_limited`, `provider_error`, and `malformed_json`.
- Needed next: response-format compatibility per model; some providers appear to ignore or mishandle `response_format`.
- Needed next: real cost accounting from provider usage when OpenRouter returns it.

## Recommended Next Run

Do not scale Kimi K2.6. For a larger cheap run, use:

- `qwen/qwen3-vl-32b-instruct`
- `qwen/qwen3-vl-30b-a3b-instruct`
- `mistralai/mistral-small-2603`
- `mistralai/ministral-14b-2512`
- `google/gemma-4-26b-a4b-it`

Run these over all 40 docs with `important_info_v2`, or first test a shorter `important_info_fast_v3` prompt against the same five-doc slice.

## Highest-Quality Follow-Up

After choosing quality over speed, a second 5-document bakeoff tested:

- `qwen/qwen3-vl-235b-a22b-instruct`
- `qwen/qwen3-vl-32b-instruct`
- `qwen/qwen3-vl-30b-a3b-instruct`
- `mistralai/ministral-14b-2512`

Prompts:

- `strict_schema`
- `important_info_v2`

Output:

- `predictions/high_quality_prompt_bakeoff_5doc.json`
- `reports/high_quality_prompt_bakeoff_5doc/important_info_leaderboard.md`

Best model+prompt combinations:

| rank | model | prompt | score | valid rows | avg_latency_s |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | `qwen/qwen3-vl-30b-a3b-instruct` | `strict_schema` | 0.8238 | 5/5 | 13.23 |
| 2 | `qwen/qwen3-vl-235b-a22b-instruct` | `strict_schema` | 0.7239 | 5/5 | 22.48 |
| 3 | `qwen/qwen3-vl-235b-a22b-instruct` | `important_info_v2` | 0.6185 | 5/5 | 23.89 |
| 4 | `mistralai/ministral-14b-2512` | `strict_schema` | 0.6042 | 5/5 | 12.36 |

Decision:

- For highest quality right now, scale `strict_schema`, not `important_info_v2`.
- Primary candidate: `qwen/qwen3-vl-30b-a3b-instruct`.
- Secondary candidate: `qwen/qwen3-vl-235b-a22b-instruct`.
- Backup audit candidate: `mistralai/ministral-14b-2512`.
- Do not scale `qwen/qwen3-vl-32b-instruct` in this exact setup until provider errors are understood; it had 4 errors across 10 bakeoff calls.

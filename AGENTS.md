# German Document VLM Benchmark Guidance

## Goal

Run the German document VLM benchmark safely enough to finish an overnight comparison by tomorrow and produce usable prediction outputs plus the best available leaderboard/report.

## Safety Constraints

- Never print, commit, upload, or expose `.env` or `OPENROUTER_API_KEY`.
- Treat downloaded PDFs, rendered images, predictions, scores, reports, gold labels, and gold packs as local artifacts only.
- Use `--spend` only together with `--max-cost-usd`.
- Do not run unbounded work. Prefer controlled batches with explicit call counts, estimated cost, output path, and expected runtime.
- If a command fails, stop larger scaling, summarize the failure, preserve partial outputs, and fix minimally before retrying.

## Contestant Input Rule

Contestant model calls must use rendered page images only. Do not use OCR, PDF text layers, extracted text, or any other hidden document text as contestant input.

## Resume Behavior

The runner should skip already completed `(model, prompt, doc_id)` rows when an output file already exists. It should write the predictions JSON after every new model call so interrupted runs preserve completed rows.

## If Stuck

Do not retry expensive batches blindly. Preserve partial prediction files, stop larger scaling, and write a short local status file or report explaining:

- what command was running
- which output file contains partial results
- completed row counts and statuses
- the failure or blocker
- the safest next command, if known

## End State

By tomorrow, produce prediction files under `predictions/` and either:

- scores plus `reports/leaderboard.md` when matching `gold/*.gold.json` labels exist, or
- a local AI comparison report based on status, JSON validity, latency, cost when available, and parsed-output availability when gold labels are missing.

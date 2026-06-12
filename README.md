# German Document VLM Battle Arena

`docarena` is a Python CLI benchmark harness for comparing OpenRouter vision-language models on rendered images of German public-source documents.

The repository stores URL manifests and benchmark code only. Downloaded PDFs, rendered PNGs, model predictions, raw responses, scores, reports, and locked gold labels are local/private artifacts ignored by git.

## Core Rules

- Contestant models receive prompt text plus rendered page images only.
- No OCR, PDF text layer, or external text extraction is used in contestant calls.
- Real OpenRouter spending requires `--spend` and `--max-cost-usd`.
- Gold labels are produced separately and stored under local `gold/*.gold.json`.

## Commands

```bash
docarena manifest validate
docarena sources check
docarena fetch --dry-run
docarena fetch --allow-download
docarena render
docarena gold export-pack
docarena run --dry-run
docarena run --spend --max-cost-usd 5
docarena score
docarena report
```

`OPENROUTER_API_KEY` is read from the environment for real model calls.

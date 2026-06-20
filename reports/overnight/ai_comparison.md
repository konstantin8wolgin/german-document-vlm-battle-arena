# AI Comparison

Predictions: `predictions/strict_schema_all_models_overnight.json`
Completed rows: 320
Completed docs: 40
Completed categories: bank_finanzen, behoerdenpost, formulare, medizin, rechnungen, steuer, versicherung, vertraege
Statuses: {'ok': 219, 'error': 25, 'malformed_json': 76}

Accuracy leaderboard unavailable: no `gold/*.gold.json` labels are present.

| model | calls | docs | categories | ok | malformed_json | error | json_valid_rate | parsed_outputs | avg_latency_s | cost_usd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mistralai/mistral-small-2603 | 40 | 40 | 8 | 39 | 1 | 0 | 0.975 | 39 | 5.17 | 0.0 |
| qwen/qwen3-vl-235b-a22b-instruct | 40 | 40 | 8 | 39 | 1 | 0 | 0.975 | 39 | 25.16 | 0.0 |
| qwen/qwen3-vl-32b-instruct | 40 | 40 | 8 | 38 | 1 | 1 | 0.95 | 38 | 13.08 | 0.0 |
| qwen/qwen3-vl-8b-instruct | 40 | 40 | 8 | 37 | 3 | 0 | 0.925 | 37 | 14.2 | 0.0 |
| qwen/qwen2.5-vl-72b-instruct | 40 | 40 | 8 | 37 | 0 | 3 | 0.925 | 37 | 18.38 | 0.0 |
| mistralai/mistral-medium-3-5 | 40 | 40 | 8 | 21 | 19 | 0 | 0.525 | 21 | 13.4 | 0.0 |
| z-ai/glm-4.6v | 40 | 40 | 8 | 8 | 11 | 21 | 0.2 | 8 | 25.42 | 0.0 |
| meta-llama/llama-3.2-11b-vision-instruct | 40 | 40 | 8 | 0 | 40 | 0 | 0.0 | 0 | 2.05 | 0.0 |

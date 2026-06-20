# Important-Information Leaderboard

This evaluator compares each parsed model output with locally extracted reference terms from the selected PDF pages. Contestant model calls used rendered page images only; this report is post-run local evaluation.

Invalid or missing parsed JSON is gated to a zero final score. For valid rows, scoring weights are: important terms 35%, numbers/dates 35%, document type 10%, required output-field presence 10%, valid parsed JSON 10%. Treat this as a practical no-gold-label leaderboard, not a certified accuracy benchmark.

Detailed scored rows: `reports/important_info_v2_new_models_5doc/important_info_scored_rows.csv`

| rank | model | final_score | ok | malformed_json | error | important_term_recall | number_date_recall | field_presence | avg_latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | qwen/qwen3-vl-32b-instruct | 0.7383 | 5 | 0 | 0 | 0.538 | 0.7333 | 0.9333 | 21.99 |
| 2 | qwen/qwen3-vl-30b-a3b-instruct | 0.7024 | 5 | 0 | 0 | 0.4481 | 0.7111 | 0.9667 | 12.06 |
| 3 | mistralai/ministral-14b-2512 | 0.6873 | 5 | 0 | 0 | 0.5589 | 0.5667 | 0.9333 | 17.45 |
| 4 | mistralai/mistral-small-2603 | 0.6733 | 5 | 0 | 0 | 0.5524 | 0.5333 | 0.9333 | 5.69 |
| 5 | google/gemma-4-26b-a4b-it | 0.6527 | 5 | 0 | 0 | 0.4743 | 0.6 | 0.7667 | 15.01 |
| 6 | mistralai/mistral-large-2512 | 0.5187 | 4 | 1 | 0 | 0.5434 | 0.6 | 0.7667 | 15.4 |
| 7 | mistralai/ministral-8b-2512 | 0.4812 | 4 | 1 | 0 | 0.5219 | 0.4667 | 0.7 | 9.96 |
| 8 | moonshotai/kimi-k2.5 | 0.4302 | 3 | 1 | 1 | 0.3902 | 0.5445 | 0.5667 | 32.96 |
| 9 | moonshotai/kimi-k2.6 | 0.0 | 0 | 0 | 5 | 0.0 | 0.0 | 0.0 | 33.94 |

## Category Winners

| category | model | final_score | ok | malformed_json | error | avg_latency_s |
| --- | --- | --- | --- | --- | --- | --- |
| bank_finanzen | qwen/qwen3-vl-32b-instruct | 0.759 | 1 | 0 | 0 | 16.23 |
| formulare | qwen/qwen3-vl-32b-instruct | 0.8143 | 1 | 0 | 0 | 12.94 |
| medizin | qwen/qwen3-vl-30b-a3b-instruct | 0.9058 | 1 | 0 | 0 | 7.82 |
| rechnungen | qwen/qwen3-vl-30b-a3b-instruct | 0.808 | 1 | 0 | 0 | 24.33 |
| vertraege | moonshotai/kimi-k2.5 | 0.7396 | 1 | 0 | 0 | 60.82 |

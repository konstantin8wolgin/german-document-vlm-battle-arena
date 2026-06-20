# Important-Information Leaderboard

This evaluator compares each parsed model output with locally extracted reference terms from the selected PDF pages. Contestant model calls used rendered page images only; this report is post-run local evaluation.

Invalid or missing parsed JSON is gated to a zero final score. For valid rows, scoring weights are: important terms 35%, numbers/dates 35%, document type 10%, required output-field presence 10%, valid parsed JSON 10%. Treat this as a practical no-gold-label leaderboard, not a certified accuracy benchmark.

Detailed scored rows: `reports/high_quality_prompt_bakeoff_5doc/important_info_scored_rows.csv`

| rank | model | final_score | ok | malformed_json | error | important_term_recall | number_date_recall | field_presence | avg_latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | qwen/qwen3-vl-235b-a22b-instruct | 0.6712 | 10 | 0 | 0 | 0.5432 | 0.5556 | 0.8667 | 23.19 |
| 2 | qwen/qwen3-vl-30b-a3b-instruct | 0.6582 | 9 | 1 | 0 | 0.4638 | 0.8 | 0.85 | 13.13 |
| 3 | mistralai/ministral-14b-2512 | 0.5848 | 9 | 1 | 0 | 0.5207 | 0.6778 | 0.3833 | 15.87 |
| 4 | qwen/qwen3-vl-32b-instruct | 0.4435 | 6 | 0 | 4 | 0.3012 | 0.4611 | 0.5667 | 12.08 |

## Category Winners

| category | model | final_score | ok | malformed_json | error | avg_latency_s |
| --- | --- | --- | --- | --- | --- | --- |
| bank_finanzen | qwen/qwen3-vl-30b-a3b-instruct | 0.7431 | 2 | 0 | 0 | 9.14 |
| formulare | qwen/qwen3-vl-30b-a3b-instruct | 0.7696 | 2 | 0 | 0 | 11.01 |
| medizin | mistralai/ministral-14b-2512 | 0.8188 | 2 | 0 | 0 | 9.92 |
| rechnungen | qwen/qwen3-vl-30b-a3b-instruct | 0.7046 | 2 | 0 | 0 | 19.52 |
| vertraege | qwen/qwen3-vl-32b-instruct | 0.676 | 2 | 0 | 0 | 9.41 |

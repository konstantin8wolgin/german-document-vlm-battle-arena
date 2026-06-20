# Important-Information Leaderboard

This evaluator compares each parsed model output with locally extracted reference terms from the selected PDF pages. Contestant model calls used rendered page images only; this report is post-run local evaluation.

Invalid or missing parsed JSON is gated to a zero final score. For valid rows, scoring weights are: important terms 35%, numbers/dates 35%, document type 10%, required output-field presence 10%, valid parsed JSON 10%. Treat this as a practical no-gold-label leaderboard, not a certified accuracy benchmark.

Detailed scored rows: `reports/high_quality_top3_strict_schema_all_docs/important_info_scored_rows.csv`

| rank | model | final_score | ok | malformed_json | error | important_term_recall | number_date_recall | field_presence | avg_latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | qwen/qwen3-vl-30b-a3b-instruct | 0.6789 | 38 | 2 | 0 | 0.5763 | 0.6629 | 0.9042 | 17.33 |
| 2 | qwen/qwen3-vl-235b-a22b-instruct | 0.6434 | 38 | 2 | 0 | 0.5223 | 0.5534 | 0.9042 | 25.14 |
| 3 | mistralai/ministral-14b-2512 | 0.501 | 35 | 5 | 0 | 0.4523 | 0.6029 | 0.1167 | 17.48 |

## Category Winners

| category | model | final_score | ok | malformed_json | error | avg_latency_s |
| --- | --- | --- | --- | --- | --- | --- |
| bank_finanzen | qwen/qwen3-vl-30b-a3b-instruct | 0.7718 | 5 | 0 | 0 | 13.8 |
| behoerdenpost | qwen/qwen3-vl-235b-a22b-instruct | 0.6641 | 5 | 0 | 0 | 35.04 |
| formulare | qwen/qwen3-vl-30b-a3b-instruct | 0.8183 | 5 | 0 | 0 | 16.6 |
| medizin | qwen/qwen3-vl-30b-a3b-instruct | 0.7501 | 5 | 0 | 0 | 19.77 |
| rechnungen | qwen/qwen3-vl-30b-a3b-instruct | 0.7723 | 5 | 0 | 0 | 14.6 |
| steuer | qwen/qwen3-vl-30b-a3b-instruct | 0.5657 | 4 | 1 | 0 | 21.23 |
| versicherung | qwen/qwen3-vl-30b-a3b-instruct | 0.7099 | 5 | 0 | 0 | 22.21 |
| vertraege | qwen/qwen3-vl-235b-a22b-instruct | 0.6486 | 5 | 0 | 0 | 13.65 |

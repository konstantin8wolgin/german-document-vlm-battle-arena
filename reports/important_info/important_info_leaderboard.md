# Important-Information Leaderboard

This evaluator compares each parsed model output with locally extracted reference terms from the selected PDF pages. Contestant model calls used rendered page images only; this report is post-run local evaluation.

Invalid or missing parsed JSON is gated to a zero final score. For valid rows, scoring weights are: important terms 35%, numbers/dates 35%, document type 10%, required output-field presence 10%, valid parsed JSON 10%. Treat this as a practical no-gold-label leaderboard, not a certified accuracy benchmark.

Detailed scored rows: `reports/important_info/important_info_scored_rows.csv`

| rank | model | final_score | ok | malformed_json | error | important_term_recall | number_date_recall | field_presence | avg_latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | qwen/qwen3-vl-32b-instruct | 0.6811 | 38 | 1 | 1 | 0.6081 | 0.5894 | 0.8667 | 13.08 |
| 2 | qwen/qwen3-vl-235b-a22b-instruct | 0.6567 | 39 | 1 | 0 | 0.5383 | 0.5415 | 0.925 | 25.16 |
| 3 | mistralai/mistral-small-2603 | 0.6075 | 39 | 1 | 0 | 0.5012 | 0.4913 | 0.8875 | 5.17 |
| 4 | qwen/qwen3-vl-8b-instruct | 0.5886 | 37 | 3 | 0 | 0.5055 | 0.507 | 0.85 | 14.2 |
| 5 | qwen/qwen2.5-vl-72b-instruct | 0.501 | 37 | 0 | 3 | 0.3228 | 0.3847 | 0.8333 | 18.38 |
| 6 | mistralai/mistral-medium-3-5 | 0.4173 | 21 | 19 | 0 | 0.7577 | 0.746 | 0.4625 | 13.4 |
| 7 | z-ai/glm-4.6v | 0.0988 | 8 | 11 | 21 | 0.1899 | 0.2015 | 0.175 | 25.42 |
| 8 | meta-llama/llama-3.2-11b-vision-instruct | 0.0 | 0 | 40 | 0 | 0.0275 | 0.0616 | 0.0 | 2.05 |

## Category Winners

| category | model | final_score | ok | malformed_json | error | avg_latency_s |
| --- | --- | --- | --- | --- | --- | --- |
| bank_finanzen | qwen/qwen3-vl-235b-a22b-instruct | 0.7809 | 5 | 0 | 0 | 26.19 |
| behoerdenpost | mistralai/mistral-small-2603 | 0.656 | 5 | 0 | 0 | 6.8 |
| formulare | qwen/qwen3-vl-32b-instruct | 0.8457 | 5 | 0 | 0 | 15.22 |
| medizin | mistralai/mistral-medium-3-5 | 0.8176 | 5 | 0 | 0 | 10.49 |
| rechnungen | qwen/qwen3-vl-32b-instruct | 0.799 | 5 | 0 | 0 | 12.94 |
| steuer | qwen/qwen3-vl-32b-instruct | 0.7905 | 5 | 0 | 0 | 14.7 |
| versicherung | qwen/qwen3-vl-32b-instruct | 0.6672 | 5 | 0 | 0 | 12.77 |
| vertraege | qwen/qwen3-vl-32b-instruct | 0.7121 | 5 | 0 | 0 | 11.4 |

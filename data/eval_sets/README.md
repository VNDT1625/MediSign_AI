# Eval Sets

Bo cau hoi test co dinh de danh gia adapter Medical va Psychology truoc khi release.

| File | Records | Schema | Mục đích |
| --- | ---: | --- | --- |
| `demo_safety_eval.jsonl` | 427 | `id`, `input`, `expected_response_type`, `expected_urgency`, `must_include_disclaimer`, `source` | Regression an toan: clarification / self-care / emergency / disclaimer expectations. |

`expected_response_type` co the la mot trong: `clarification`, `analysis`,
`emergency`, `medicine_lookup`, `unsupported_image`. `expected_urgency` ánh
sang ba mức triage: `green`, `yellow`, `red`.

> Khi chay benchmark moi, **giu nguyen** file `demo_safety_eval.jsonl` la stable
> regression set. Cac eval bo sung (Vietnamese medical QA, drug interaction,
> red-flag triage, OARS quality) co the bo sung sau duoi cac file `*.jsonl`
> rieng cung thu muc.

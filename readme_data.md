# MediSign AI Data Inventory

Snapshot generated from the current `data/` directory on 2026-05-20.

This document summarizes what is currently stored under `data/`, what each dataset is for, the observed record counts/schemas, and the main quality or operational caveats.

## High-Level Overview

`data/` is a mixed data workspace containing:

- Raw medical training corpora from MedQuAD, PubMedQA, Chinese medical dialogue data, Wikipedia-derived data, DAV drug registry crawls, HTML/PDF snapshots, and synthetic Vietnamese Q&A.
- Clean training datasets for Qwen 72B and MedGemma 4B fine-tuning.
- A large local knowledge base for RAG: drugs, drug interactions, public guideline chunks, nutrition references, Vietnamese symptom phrases, and common diseases.
- A local SQLite development database used by the FastAPI backend.
- A vendored external package/repo, `brightohir`, for HL7/FHIR interoperability and Vietnamese medical code-system samples.
- Data preparation, crawling, translation, normalization, and merge scripts.

Approximate size by top-level area:

| Path | Purpose | Files | Size |
|---|---:|---:|---:|
| `data/knowledge_base/` | RAG-ready JSON knowledge base and harvested public references | 41 | ~10.57 GB |
| `data/training_raw/` | Raw and intermediate training corpora | 12,124 | ~2.42 GB |
| `data/training_clean/` | Clean train/eval datasets and drug databases | 32 | ~309 MB |
| `data/external/` | Vendored `brightohir` source and wheel | 83 | ~0.9 MB |
| `data/eval_sets/` | Fixed safety/evaluation set | 2 | ~0.24 MB |
| `data/scripts/` | Data pipeline scripts | 32 | ~0.27 MB |
| `data/processed/` | Small processed ICD-10 sample schema | 2 | ~2 KB |
| `data/dev_backend.sqlite3` | Local backend dev DB | 1 | ~0.21 MB |

Important: `.gitignore` excludes `data/training_raw/`, `data/training_clean/`, and `data/knowledge_base/`, so much of this data is local/generated and may not be present in another checkout.

## Directory Map

```text
data/
├── dev_backend.sqlite3
├── eval_sets/
├── external/
│   ├── brightohir/
│   └── pypi_downloads/
├── knowledge_base/
│   └── public/
│       └── raw/
├── processed/
├── scripts/
├── training_clean/
│   ├── medgemma_4b/
│   └── qwen_72b/
└── training_raw/
    ├── MedQuAD/
    ├── Medical-Dialogue-Dataset-Chinese/
    ├── dav_congbothuoc_api/
    ├── dav_congbothuoc_api_paged/
    ├── dav_drug_lookup_html/
    ├── dav_drug_registration_2026/
    ├── pubmedqa/
    └── vietnamese_medical/
```

## `data/eval_sets/`

Fixed evaluation data for safety and response-shape checks.

| File | Records | Schema / Notes |
|---|---:|---|
| `README.md` | n/a | Says this folder contains fixed test questions for med/personal adapters before release. |
| `demo_safety_eval.jsonl` | 427 | JSONL with `id`, `input`, `expected_response_type`, `expected_urgency`, `must_include_disclaimer`, `source`. Covers clarification, self-care, emergency, disclaimer expectations. |

Use this folder for regression evaluation, not training.

## `data/processed/`

Small processed ICD-10 Vietnamese sample data.

| File | Records | Fields |
|---|---:|---|
| `icd10_vn_schema.json` | 5 | `icd_code`, `name_vi`, `name_en`, `category` |
| `icd10_vn_schema.csv` | 5 | Same fields as JSON |

Current examples include `A09`, `E11.9`, `I10`, `J06.9`, `K29.7`. This looks like a schema/example seed, not a full ICD-10 dataset.

## `data/dev_backend.sqlite3`

Local development database for the backend.

Tables observed:

| Table | Rows | Purpose |
|---|---:|---|
| `users` | 1 | Local user account record. Contains password hash and profile identifiers. |
| `user_sessions` | 23 | Refresh-token sessions/device metadata. Contains token hashes and IP/device fields. |
| `community_posts` | 0 | Community post model. |
| `post_comments` | 0 | Comments for community posts. |
| `post_likes` | 0 | Likes for community posts. |
| `user_profiles` | 0 | Health profile data. |
| `triage_history` | 0 | Symptom triage history. |
| `medicine_registry` | 0 | Medicine registry table. |
| `my_medicines` | 0 | User medicine cabinet. |
| `daily_journals` | 0 | Soul garden / journal entries. |
| `family_connections` | 0 | Family account links. |
| `fitness_goals` | 0 | Fitness goal records. |
| `workout_sessions` | 0 | Workout session records. |
| `hospitals` | 0 | Hospital registry records. |
| `email_verifications` | 0 | Email verification tokens. |
| `password_resets` | 0 | Password reset tokens. |

Security note: this DB contains authentication/session material even if hashed. Treat it as local development data and avoid sharing it.

## `data/knowledge_base/`

RAG-oriented canonical JSON knowledge base. Most records share this schema:

```json
{
  "id": "...",
  "type": "...",
  "title": "...",
  "aliases": [],
  "content": "...",
  "structured": {},
  "source": {},
  "last_updated": "...",
  "confidence": "...",
  "needs_medical_review": true
}
```

Top-level files:

| File | Records | Notes |
|---|---:|---|
| `knowledge_base.json` | 128,380 | Merged RAG base. Includes drugs, interactions, nutrition, symptoms, common diseases, guideline chunks. Large: ~747 MB. |
| `drugs.json` | 60,472 | Drug records. Main fields include name, registration number, active ingredient, strength, dosage form, manufacturer, activity/expiry flags. |
| `drug_interactions.json` | 67,493 | Interaction records. Mostly curated seed plus public openFDA/DailyMed label-derived content. Large: ~673 MB. |
| `nutrition_requirements_by_age.json` | 38 | Vietnamese nutrition requirement records by nutrient/age/sex. |
| `vietnamese_symptom_phrases.json` | 11 | Vietnamese symptom phrase normalization/knowledge records. |
| `vietnam_common_diseases.json` | 10 | Small curated common disease knowledge records. |
| `public_guideline_chunks.json` | 356 | Guideline chunks copied from `public/public_guideline_chunks.json`. |
| `build_report.json` | n/a | Build counts and notes. Reports 60,472 drugs, 67,493 interactions, 356 public guideline chunks, 128,380 total KB records. |

Build report caveats:

- DrugBank Clinical is not included because it is paid/licensed.
- Public interaction labels and guideline chunks still need clinical review before production.
- DAV detailed API crawl is reported complete at 53,814/53,814 raw items.

### `data/knowledge_base/public/`

Public harvested references and normalized public datasets.

| File | Records | Notes |
|---|---:|---|
| `openfda_drug_interaction_labels.json` | 67,473 | Public openFDA/DailyMed interaction label records; large normalized JSON, ~673 MB. |
| `nutrition_public_reference.json` | 20 | NIH ODS/public nutrition fallback references. |
| `public_guideline_chunks.json` | 356 | KCB/BYT/NIH public guideline chunks. |
| `public_guideline_manifest.json` | n/a | Visited pages, PDF URLs, chunk count. |
| `openfda_interaction_ranges.json` | 6 | Date/search ranges for openFDA crawl. |
| `openfda_interaction_progress.json` | n/a | Resume/progress state for openFDA interaction crawl. |
| `harvest_report.json` | n/a | Public harvest summary: 67,849 public records total. |

### `data/knowledge_base/public/raw/`

Raw harvested source artifacts.

| Path | Contents |
|---|---|
| `openfda_interaction_labels_raw.jsonl` | 84,948 raw openFDA label records; ~8.38 GB. |
| `drugbank/drugbank.xsd` | DrugBank XML schema only, not DrugBank data. |
| `extracted_text/` | 12 extracted `.txt` documents from KCB/BYT/NIN/nutrition PDFs/pages. |
| `pdfs/` | 12 downloaded public PDFs, ~20.5 MB total. |

Operational note: the raw openFDA JSONL is extremely large. Use streaming reads; do not load it fully into memory.

## `data/training_clean/`

Cleaned data suitable for model training or drug database lookup.

### Drug registry and DAV-derived clean data

| File | Records | Schema / Notes |
|---|---:|---|
| `drug_database.json` | 242 | Simple `name`, `description`, `source` drug DB. |
| `drug_database_expanded.json` | 801 | Expanded simple drug DB. |
| `drug_database_10k.json` | 8,149 | Deduped lookup-style drug database. Despite name, current count is 8,149. |
| `drug_database_10k_full.json` | 12,570 | Less-deduped/full lookup variant. |
| `drug_database_dav_detailed.json` | 13,465 | DAV detailed database converted to simple lookup format. |
| `drug_database_dav_detailed_10k.json` | 64,045 | Large DAV detailed DB, simple lookup format. |
| `dav_lookup_drugs.json` | 11,769 | DAV HTML lookup crawl rows: receipt number/year, name, registrant, registration number, attachment URL. |
| `dav_detailed_drugs.json` | 1,371 | Detailed DAV drug records with ingredient, strength, form, manufacturer, dates, status flags, source query/id. |
| `dav_detailed_drugs_10k.json` | 53,698 | Large detailed DAV API result set. |
| `dav_drug_records.json` | 1,305 | Parsed records from 2026 DAV registration PDFs/HTML. |
| `dav_registered_drugs.json` | 1,253 | Registered subset from parsed DAV records. |
| `dav_registered_drugs_high_confidence.json` | 559 | High-confidence parsed registered drugs. |
| `dav_lookup_crawl_report.json` | n/a | Report for DAV lookup crawl. |
| `dav_detailed_paged_report.json` | n/a | Report for paged DAV API crawl. |
| `dav_detail_enrich_report.json` | n/a | Report for detail enrichment. |
| `dav_drug_parse_report.json` | n/a | Parse-quality/status report for DAV registration documents. |

### Dialogue and model-ready training data

| File | Records | Schema / Notes |
|---|---:|---|
| `medical_dialogue_2010_2020.json` | 5,900 | Instruction-tuning records: `instruction`, `input`, `output`, `source`. |
| `medical_dialogue_checkpoint.json` | 800 | Checkpoint subset. |
| `medical_dialogue_full.json` | 800 | Full translated/converted dialogue subset currently present. |

### `data/training_clean/qwen_72b/`

Instruction-tuning data for Qwen 72B.

| File | Records | Notes |
|---|---:|---|
| `train.json` | 16,888 | Current train split with `instruction`, `input`, `output`, `source`. |
| `eval.json` | 1,876 | Current eval split. |
| `2010_vi.json` | 550 | 2010 Vietnamese dialogue subset. |
| `train.json.backup.json` | 12,513 | Older train backup. |
| `eval.json.backup.json` | 1,390 | Older eval backup. |
| `train_backup.json` | 12,303 | Older train backup. |
| `eval_backup.json` | 1,366 | Older eval backup. |

### `data/training_clean/medgemma_4b/`

Formatted data for MedGemma 4B (Medical + Psychology dual-adapter setup).

| File | Records | Notes |
|---|---:|---|
| `medical_train.jsonl` | 15,693 | Medical adapter — train split (chat-templated JSONL). |
| `medical_eval.jsonl` | 2,770 | Medical adapter — eval split. |
| `psychology_train.jsonl` | 1,201 | Psychology adapter — OARS-style, regenerated via DeepSeek/FPT Cloud (`scripts/regenerate_psychology_data.py`). |
| `psychology_eval.jsonl` | 212 | Psychology adapter — eval split. |
| `train.jsonl` | 17,393 | Legacy combined (Medical + Psychology v1 + OARS) — kept for the `scripts/train_qlora_medgemma.py` default path. |
| `eval.jsonl` | 3,070 | Legacy combined eval. |
| `merged_dataset.json` | 17,263 | Merged instruction/input/output/source dataset (pre-format). |
| `oars_train.jsonl` | 1,700 | Earlier OARS template-only train set. |
| `oars_eval.jsonl` | 300 | Earlier OARS template-only eval. |
| `output_format_train.jsonl` | 1,020 | Output-format training samples (% + Xanh/Vàng/Đỏ + disclaimer). |
| `output_format_eval.jsonl` | 180 | Output-format eval. |
| `psychology_part_0.jsonl` / `psychology_part_1.jsonl` | 750 / 750 | Per-worker raw output from the parallel regeneration run (input to dedup-merge). |
| `merge_stats.json` / `format_stats.json` | n/a | Stats for the medical merge + format pipeline. |
| `psychology_merge_stats.json` | n/a | Per-worker counts (`750 / 750`), dedup, train/eval split. |
| `psychology_regen_stats.json` | n/a | Per-run regeneration stats (model, topic distribution). |
| `oars_stats.json` / `output_format_stats.json` / `rag_training_set_stats.json` | n/a | Other pipeline stats. |

## `data/training_raw/`

Raw and intermediate training data. Existing `README.md` says all data is intended to be Vietnamese JSON, but the file is stale in places: it claims `all_medical_vi.json` has 17,707 records, while the current file has 13,758 records.

### Direct JSON/HTML/JS/archive files

| File | Records / Type | Notes |
|---|---:|---|
| `all_medical_vi.json` | 13,758 | Unified raw Q&A: `question`, `answer`, `source`. |
| `full_medical_vi.json` | 145 | General Vietnamese medical Q&A. |
| `structured_response_training.json` | 67 | JSON-string output examples for structured assistant responses and safety fields. |
| `crawled_drugs_comprehensive.json` | 242 | Crawled drug records: `name`, `description`, `source`. |
| `crawled_drugs_demo.json` | 1 | Tiny demo drug Q&A. |
| `crawled_extended.json` | 362 | Extended crawled Q&A. |
| `crawled_extended_clean.json` | 362 | Instruction-tuning normalized version of extended crawl. |
| `drug_db_qa.json` | 968 | Drug database Q&A: `question`, `answer`, `source`. |
| `drug_medicine_qa.json` | 189 | Drug usage Q&A. |
| `synthetic_data.json` | 116 | Synthetic symptom/disease Q&A. |
| `synthetic_drugs.json` | 100 | Synthetic drug interaction Q&A. |
| `synthetic_v2.json` | 244 | Expanded synthetic medical Q&A. |
| `vn_dialogues.json` | 47 | Vietnamese dialogue-style medical Q&A. |
| `vn_diseases.json` | 126 | Vietnamese disease Q&A. |
| `vn_drugs_commercial.json` | 576 | Commercial/common VN drug instruction-tuning records. |
| `vn_drugs_extended.json` | 230 | Expanded VN drug Q&A, including price/availability style questions. |
| `vn_pharma_bhyt.json` | 63 | VN pharma, BHYT, first-aid, system Q&A. |
| `vn_symptoms_culture.json` | 224 | Vietnamese cultural symptom phrases, instruction-tuning format. |
| `wikipedia_drugs.json` | 56 | Wikipedia drug Q&A. |
| `wikipedia_drugs_clean.json` | 56 | Clean instruction-tuning version of Wikipedia drug Q&A. |
| `dav_congbothuoc_index.html` | HTML | DAV source/index HTML snapshot. |
| `dav_lookup_page1.html` | HTML | DAV lookup first page snapshot. |
| `Common_bundle.js`, `Scripts_bundle.js` | JS | DAV/site JS bundles captured with raw crawl. |
| `Medical-Dialogue-Dataset-Chinese.rar` | Archive | Large original archive, ~363 MB. |
| `.gitkeep` | n/a | Placeholder. |

Most Q&A records include the standard safety note: `⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ.`

### `training_raw/MedQuAD/`

MedQuAD raw XML corpus and converted Vietnamese JSON.

| Path | Files / Records | Notes |
|---|---:|---|
| `medquad_vi.json` | 16,407 | Converted Q&A with `question`, `answer`, `source`, `original_disease`, `original_qtype`. |
| `10_MPlus_ADAM_QA/` | 4,366 XML | MedlinePlus ADAM Q&A. |
| `11_MPlusDrugs_QA/` | 1,312 XML | MedlinePlus drugs Q&A. |
| `12_MPlusHerbsSupplements_QA/` | 99 XML | Herbs/supplements Q&A. |
| `1_CancerGov_QA/` | 116 XML | Cancer.gov Q&A. |
| `2_GARD_QA/` | 2,685 XML | Rare disease Q&A. |
| `3_GHR_QA/` | 1,086 XML | Genetics Home Reference Q&A. |
| `4_MPlus_Health_Topics_QA/` | 981 XML | MedlinePlus health topics. |
| `5_NIDDK_QA/` | 157 XML | NIDDK Q&A. |
| `6_NINDS_QA/` | 277 XML | NINDS Q&A. |
| `7_SeniorHealth_QA/` | 48 XML | SeniorHealth Q&A. |
| `8_NHLBI_QA_XML/` | 88 XML | NHLBI Q&A. |
| `9_CDC_QA/` | 59 XML | CDC Q&A. |

Total XML files observed in MedQuAD subfolders: 11,274.

Quality note: older README says MedQuAD questions are Vietnamese but answers may still contain English. Current translated quality should be checked before using for final supervised fine-tuning.

### `training_raw/Medical-Dialogue-Dataset-Chinese/`

Chinese medical dialogue source and converted samples.

| File / Group | Records / Type | Notes |
|---|---:|---|
| `extracted_dialogues.json` | 1,111,659 | Very large extracted dialogue metadata/content file, ~664 MB. |
| `chinese_medical_vi.json` | 139 | Converted Vietnamese Q&A sample with `question`, `answer`, `source`, `disease_vi`. |
| `*.txt` files | 10 | Large raw department/dialogue text dumps. |
| `Medical-Dialogue-Dataset-Chinese` | no extension | Raw artifact/placeholder file. |

Use streaming reads for `extracted_dialogues.json`.

### `training_raw/pubmedqa/`

PubMedQA source and converted Vietnamese Q&A.

| File | Records | Notes |
|---|---:|---|
| `pubmedqa_vi.json` | 1,000 | Converted Q&A with `question`, `answer`, `source`, `pmid`. |
| `data/ori_pqal.json` | 1,000 | Original PubMedQA records keyed by PMID. |
| `data/test_ground_truth.json` | 500 | Test labels keyed by PMID. |
| `preprocess/`, `*.py`, `README.md` | n/a | Original preprocessing utilities. |

### DAV raw crawls under `training_raw/`

| Path | Contents |
|---|---|
| `dav_congbothuoc_api/raw_details.jsonl` | 2,962 query/detail responses from DAV API. |
| `dav_congbothuoc_api/dav_congbothuoc_api/raw_details.jsonl` | 3,468 query/detail responses; appears duplicated/nested from another run. |
| `dav_congbothuoc_api_paged/raw_pages.jsonl` | 108 paged API responses, ~167 MB. |
| `dav_drug_lookup_html/` | 243 DAV lookup HTML pages. |
| `dav_drug_lookup_html/dav_drug_lookup_html/` | 243 nested duplicate HTML pages. |
| `dav_drug_registration_2026/` | 45 HTML pages, 40 PDFs, `manifest.json`. |
| `dav_drug_registration_2026/extracted_text/` | 40 extracted text files from PDFs. |
| `dav_drug_registration_2026/dav_drug_registration_2026/` | Nested duplicate of the DAV registration crawl, including its own extracted text folder. |

There are duplicate nested folders for some DAV crawls. Be careful not to double-count if merging.

## `data/external/`

### `external/brightohir/`

Vendored source checkout for `brightohir` version `2.1.2`.

Purpose from README: pure-Python healthcare interoperability SDK for HL7 V2.x ↔ FHIR R5, R4 ↔ R5 transforms, PII masking, and Vietnamese healthcare code systems.

Key files:

| Path | Notes |
|---|---|
| `README.md` | Main package docs; describes FHIR R5 coverage, V2 converters, privacy/compliance caveats. |
| `pyproject.toml` | Package metadata; Python >=3.10; depends on `fhir.resources`, `fhir-core`, `hl7apy`, `pyyaml`. |
| `src/brightohir/*.py` | Library implementation: ACK, converters, R5 helpers, registry, security, transport, VN helpers. |
| `src/brightohir/data/vn/*.sample.jsonl` | Small sample Vietnamese code-system data. |
| `src/brightohir/data/vn/SCHEMA.md` | Schema definitions for ICD-10 VN, YHCT, drugs, lab tests, procedures, supplies, blood products, BHYT objects, hospital tiers, provinces. |
| `tests/*.py` | Package tests. |
| `docs/` and `refs/` | Conversion and FHIR R5 resource documentation. |

Sample Vietnamese code-system files currently contain tiny samples only:

| File | Records |
|---|---:|
| `bhyt_objects.sample.jsonl` | 5 |
| `blood_products.sample.jsonl` | 3 |
| `drugs_traditional.sample.jsonl` | 3 |
| `drugs_western.sample.jsonl` | 3 |
| `hospital_tiers.sample.jsonl` | 5 |
| `icd10_vn.sample.jsonl` | 5 |
| `icd10_yhct.sample.jsonl` | 3 |
| `lab_tests.sample.jsonl` | 3 |
| `medical_supplies.sample.jsonl` | 3 |
| `procedures.sample.jsonl` | 3 |
| `provinces.sample.jsonl` | 5 |

Note: `external/brightohir/.git/` is present locally. This is a nested Git repo artifact; it should be treated carefully if packaging or cleaning the project.

### `external/pypi_downloads/`

Contains `brightohir-2.1.2-py3-none-any.whl`, the package wheel for the vendored external library.

## `data/scripts/`

Data preparation scripts. They are not app runtime code; they are ETL/crawl/convert/merge utilities.

| Script | Purpose |
|---|---|
| `build_clean_data.py` | Normalize raw to clean training format, dedupe by input, remove bad rows, ensure disclaimer, split train/eval. |
| `combine_medical.py` | Combine medical data; no top-level docstring. |
| `convert_chinese.py` | Parse Chinese Medical Dialogue into Vietnamese Q&A sample. |
| `convert_drug_db.py` | Convert crawled drugs into JSON database format. |
| `convert_medquad.py` | Parse MedQuAD XML into Vietnamese Q&A. |
| `convert_pubmedqa.py` | Parse PubMedQA into Vietnamese Q&A. |
| `crawl_drug_database.py` | Crawl multiple sources for 200-500 drug records. |
| `crawl_drugs.py` | Crawl Vietnamese Wikipedia drug data. |
| `crawl_extended.py` | Extended crawl from several sources while avoiding duplicates. |
| `final_merge.py` | Merge translated datasets into one unified file and clean them. |
| `fix_and_enhance.py` | Re-translate entries still mostly English using Google Translate with multithreading. |
| `gen_vn_dialogues.py` | Generate doctor-patient dialogue and balanced Q&A. |
| `gen_vn_diseases.py` | Generate Q&A from common Vietnamese diseases. |
| `gen_vn_pharma_bhyt.py` | Generate Q&A about common VN drugs, BHYT, healthcare system, first aid. |
| `generate_drug_data.py` | Generate extra drug and interaction data from knowledge base/synthetic templates. |
| `generate_drugs_more.py` | Generate more synthetic drug/symptom data. |
| `generate_qa_from_db.py` | Generate Q&A from drug DB. |
| `generate_synthetic.py` | Generate non-duplicate synthetic data. |
| `generate_synthetic_v2.py` | Generate more synthetic data toward larger target size. |
| `generate_vn_drugs.py` | Generate VN market drug data. |
| `med_part1.py`, `med_part2.py` | Small hardcoded Q&A generators/helpers; minimal docs. |
| `merge_all_sources.py` | Merge all medical sources, dedupe, convert to train/eval. |
| `merge_all_sources_v2.py` | Merge while preserving answer variants for the same question. |
| `normalize_crawled.py` | Normalize extended crawled data. |
| `normalize_wikipedia_data.py` | Normalize Wikipedia crawled drug data. |
| `translate_medquad.py` | Translate MedQuAD answers in batches with resume/delay. |
| `translate_medquad_fast.py` | Faster concurrent MedQuAD answer translation. |
| `translate_medquad_v2.py` | Debuggable per-entry MedQuAD translation. |
| `translate_medquad_v3.py` | Batch MedQuAD translation, faster. |
| `translate_pubmedqa.py` | Translate PubMedQA answers. |
| `translate_train.py` | Minimal/obfuscated helper; no useful docstring. |

## Data Quality Notes

1. **Mixed maturity.** Some datasets are production-like normalized KB files; others are raw crawl caches, synthetic examples, or old intermediate runs.
2. **Some README counts are stale.** `training_raw/README.md` says `all_medical_vi.json` has 17,707 records, but current observed count is 13,758.
3. **Clinical review is still required.** Many records explicitly set `needs_medical_review: true`, especially guideline chunks and public interaction labels.
4. **Large files require streaming.** Do not load `openfda_interaction_labels_raw.jsonl`, `knowledge_base.json`, `drug_interactions.json`, or `extracted_dialogues.json` casually in app startup code.
5. **DAV folders contain duplicates.** Several raw DAV crawl folders have nested duplicate copies. Merge scripts should dedupe by source URL, registration number, source ID, or normalized drug name.
6. **Synthetic data is mixed with crawled/public data.** Training scripts should preserve `source` metadata and optionally weight curated/official sources higher.
7. **Auth/session data exists in SQLite.** Keep `dev_backend.sqlite3` local and avoid sharing it.
8. **External vendored repo exists inside `data/`.** `data/external/brightohir` contains a nested `.git` folder and package source; it is code/reference, not training data.

## Recommended Usage

For RAG:

- Prefer `data/knowledge_base/knowledge_base.json` if memory/indexing pipeline can stream it.
- For smaller targeted indexes, split by `type` using `drugs.json`, `drug_interactions.json`, `public_guideline_chunks.json`, and small disease/symptom files.

For model fine-tuning:

- Prefer `data/training_clean/medgemma_4b/train.jsonl` and `eval.jsonl` for MedGemma-style text formatting.
- Prefer `data/training_clean/qwen_72b/train.json` and `eval.json` for Qwen-style instruction tuning.
- Keep `source` fields during training data audits.

For drug lookup:

- Prefer `data/training_clean/drug_database_dav_detailed_10k.json` for broad lookup coverage.
- Prefer `data/training_clean/dav_detailed_drugs_10k.json` if structured DAV fields are needed.

For evaluation:

- Use `data/eval_sets/demo_safety_eval.jsonl` as a stable safety regression set.

For future cleanup:

- Remove or archive nested duplicate DAV raw folders after confirming checksums.
- Move `external/brightohir` outside `data/` if the project wants `data/` to mean data only.
- Generate a fresh consolidated manifest with checksums for all large generated files.
- Add clinical validation status per dataset before production use.

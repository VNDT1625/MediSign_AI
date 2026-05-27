import sys, traceback
sys.path.insert(0, r"c:/NDT/PJ/MediSign_AI - Copy/scripts")
try:
    import generate_output_format_samples_v2 as g
    recs = g.generate_records(target=1200)
    stats = g.write_split(recs, dry_run=False)
    import json
    print(json.dumps(stats, ensure_ascii=False, indent=2))
except Exception:
    traceback.print_exc()

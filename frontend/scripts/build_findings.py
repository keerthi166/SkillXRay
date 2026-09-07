"""Build the public, read-only report snapshot from one documented corpus run.
Usage: python3 frontend/scripts/build_findings.py /path/to/results_skillxray
"""
import argparse
import collections
import json
from pathlib import Path


def build(root):
    manifest = json.loads((root / '_manifest64_summary.json').read_text())
    reports, used = [], set()
    for entry in manifest['skills']:
        if not entry.get('record'):
            continue
        # Original records contain machine-specific paths. Keep only the run's
        # relative collection/skill path; never publish original absolute paths.
        parts = Path(entry['record']).parts
        relative = Path(*parts[parts.index('results') + 1:-1])
        path = root / relative / 'step4_harm.json'
        records = json.loads(path.read_text())
        used.add(path)
        findings = []
        for row in records:
            if str(row.get('is_violation')).lower() != 'true':
                continue
            evidence = row.get('evidence') or {}
            ci = row.get('ci') or {}
            findings.append({
                'id': row['move_id'], 'harm': row.get('harm') or 'Unclassified',
                'kind': row.get('kind'), 'data': row.get('info_type'),
                'reason': row.get('reason', ''), 'severity': None,
                'confidence': ci.get('verdict_confidence', 'not recorded'),
                'evidence': {'file': evidence.get('file', ''),
                             'lines': evidence.get('lines', []),
                             'snippet': evidence.get('snippet', '')},
            })
        assert len(records) == entry['moves'], f'Move mismatch: {relative}'
        assert len(findings) == entry['violations'], f'Flag mismatch: {relative}'
        notes = []
        if entry['skill'] == 'xlsx':
            notes.append('Known issue in the run summary: all 42 flags concern Word XML handling outside the stated spreadsheet scope. No personal data was involved in that cluster; the summary identifies these as likely false positives.')
        if entry['skill'] == 'coaching-session-summarizer':
            notes.append('Source-review context: SKILL.md documents the API script as an optional legacy fallback. Normal authentication to Anthropic is not by itself credential theft. These are the original automated flags, not confirmed violations.')
        reports.append({'skill': entry['skill'], 'source': entry['source'],
                        'category': entry['category'], 'record': str(relative / 'step4_harm.json'),
                        'moves': len(records), 'findings': findings, 'notes': notes})
    summary = manifest['summary']
    assert len(reports) == summary['analyzed']
    assert sum(len(x['findings']) for x in reports) == summary['total_violations']
    assert sum(x['moves'] for x in reports) == summary['total_moves']
    assert sum(bool(x['findings']) for x in reports) == summary['with_potential_violation']
    categories = collections.Counter(f['harm'] for r in reports for f in r['findings'])
    return {'schema_version': 1, 'run_date': '2026-08-13',
            'summary': {k: summary[k] for k in ['total','skipped','errored','analyzed','with_potential_violation','total_moves','total_violations']},
            'excluded_result_folders': sorted(str(p.parent.relative_to(root)) for p in root.rglob('step4_harm.json') if p not in used),
            'categories': [{'name': name, 'flags': count, 'skills': sum(any(f['harm']==name for f in r['findings']) for r in reports)} for name,count in categories.most_common()],
            'reports': sorted(reports, key=lambda r: (-len(r['findings']), r['skill']))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results', type=Path)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'findings-data.json')
    args = parser.parse_args()
    snapshot = build(args.results)
    args.output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'summary':snapshot['summary'], 'categories':snapshot['categories'], 'excluded':snapshot['excluded_result_folders']},indent=2))

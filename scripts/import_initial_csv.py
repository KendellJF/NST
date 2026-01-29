"""
Import initial CSV of invited Instagram handles and populate the `Entry` table.

Usage (recommended): run inside your Flask app context so SQLAlchemy is configured.

Example (run from project root):
    set FLASK_APP=app.py
    python -c "from scripts.import_initial_csv import import_csv; import_csv('data/invited.csv')"

The CSV should contain at minimum a username column (header: 'username' or
'instagram_handle' or 'handle'). Criteria columns may be `c1`, `c2`, `c3`, `c4`.
If the file uses a single combined column like `c1c2` with values like `10` or
`1,0`, the importer will try to split them.
"""
import csv
import os
import re
from datetime import datetime


def normalize_handle(raw: str) -> str:
    if not raw:
        return ''
    h = raw.strip()
    if h.startswith('@'):
        h = h[1:]
    h = h.lower().replace(' ', '')
    return h


def parse_bool(val):
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    if s in ('1', 'true', 'yes', 'y', 'on'):
        return True
    return False


def split_combined(value: str, expected_count: int):
    """Try to split a combined criteria value into a list of values.
    Accepts separators like ',', ';', '|', '/', or raw digits (e.g. '1010').
    Returns list of strings or None if cannot split into expected_count parts.
    """
    if value is None:
        return None
    s = str(value).strip()
    # Try common separators
    for sep in (',', ';', '|', '/', ' '):
        if sep in s:
            parts = [p.strip() for p in s.split(sep) if p.strip() != '']
            if len(parts) == expected_count:
                return parts
    # If string length equals expected_count and contains only digits 0/1
    if re.fullmatch(r'[01]{%d}' % expected_count, s):
        return list(s)
    return None


def import_csv(path: str, skip_existing=True):
    """Import CSV at `path` into the `Entry` table.

    This function expects to be run inside a Flask app context where
    `models.db` and `models.Entry` are available.
    """
    try:
        from models import db, Entry
    except Exception as exc:
        raise RuntimeError('Unable to import models. Ensure this script is run inside your Flask project.') from exc

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    added = 0
    skipped = 0
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        headers = [h.strip() for h in reader.fieldnames or []]

        # Determine username column
        username_col = None
        for candidate in ('instagram_handle', 'username', 'handle'):
            if candidate in [h.lower() for h in headers]:
                # find exact header (case-insensitive)
                for h in headers:
                    if h.lower() == candidate:
                        username_col = h
                        break
                if username_col:
                    break
        if not username_col:
            # fallback to first column
            username_col = headers[0] if headers else None

        # Find individual c1..c4 headers if present
        criteria_cols = {}
        for i in range(1, 5):
            key = None
            for h in headers:
                if re.fullmatch(r'c\s*%d' % i, h.lower().replace(' ', '')) or ('c%d' % i) in h.lower():
                    key = h
                    break
            criteria_cols[i] = key

        # If no per-column found, look for combined columns like 'c1c2' or 'criteria'
        combined_header = None
        if not any(criteria_cols.values()):
            for h in headers:
                if re.search(r'c\s*1.*c\s*2.*c\s*3.*c\s*4', h.lower().replace(' ', '')) or 'c1c2' in h.lower() or 'criteria' in h.lower():
                    combined_header = h
                    break

        for row in reader:
            raw_handle = row.get(username_col) if username_col else next(iter(row.values()))
            handle = normalize_handle(raw_handle)
            if not handle:
                skipped += 1
                continue

            # Check duplicate
            if skip_existing and Entry.query.filter_by(instagram_handle=handle).first():
                skipped += 1
                continue

            # Parse criteria
            cvals = {}
            if any(criteria_cols.values()):
                for i in range(1, 5):
                    col = criteria_cols.get(i)
                    cvals[i] = parse_bool(row.get(col)) if col else False
            elif combined_header:
                raw = row.get(combined_header)
                parts = split_combined(raw, 4)
                if parts:
                    for i, p in enumerate(parts, start=1):
                        cvals[i] = parse_bool(p)
                else:
                    # Could not parse combined — default to False
                    for i in range(1, 5):
                        cvals[i] = False
            else:
                # No criteria columns at all — default to False
                for i in range(1, 5):
                    cvals[i] = False

            entry = Entry(
                instagram_handle=handle,
                c1=cvals.get(1, False),
                c2=cvals.get(2, False),
                c3=cvals.get(3, False),
                c4=cvals.get(4, False),
            )
            db.session.add(entry)
            added += 1

        db.session.commit()

    print(f'Imported: {added}, Skipped: {skipped}')
    return {'added': added, 'skipped': skipped}


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python import_initial_csv.py path/to/file.csv')
        sys.exit(2)
    path = sys.argv[1]
    # When run standalone, create app context
    from app import create_app
    app = create_app()
    with app.app_context():
        import_csv(path)

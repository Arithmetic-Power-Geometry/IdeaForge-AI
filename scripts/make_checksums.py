from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_PARTS = {'.git', '.pytest_cache', '__pycache__', 'artifact'}
EXCLUDE_NAMES = {'SHA256SUMS.txt'}

lines = []
for path in sorted(ROOT.rglob('*')):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDE_PARTS for part in rel.parts) or path.name in EXCLUDE_NAMES:
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    lines.append(f'{digest}  {rel.as_posix()}')
(ROOT / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'Wrote {len(lines)} SHA-256 entries.')

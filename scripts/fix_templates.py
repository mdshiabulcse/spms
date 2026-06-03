"""Fix motion typos and ensure valid HTML in templates."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / 'templates'

for f in ROOT.rglob('*.html'):
    t = f.read_text(encoding='utf-8')
    t = t.replace('<motion', '<div').replace('</motion>', '</div>')
    f.write_text(t, encoding='utf-8')
    print('fixed', f)

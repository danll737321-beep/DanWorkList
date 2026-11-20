"""Block pushes that would put personal items or dates on the public site.

Run: python3 scripts/privacy_check.py [--extra "word1,word2"]
--extra adds private words (names, places) that must never appear; the weekly
sync task passes its own list so those words are not stored in this public repo.
Titles that contain a flagged word but are approved for the public site go in
scripts/privacy_allow.txt (one exact title per line).
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORDS = ['family', 'birthday', 'invite', 'itinerary', 'trip', 'vacation', 'travel', 'church',
         'small group', 'bible study', 'medical', 'health', 'doctor', 'finance team', 'household',
         'voting', 'election', 'brief', 'calendar', 'kid', 'son', 'daughter', 'wife', 'husband',
         'salary', 'tax', 'address', 'phone', 'password', 'todo', 'to-do']
DATE = [re.compile(r'\b20\d\d-\d\d-\d\d\b'), re.compile(r'(?<![\w/])\d{1,2}/\d{1,2}(?![\w/])')]

def main():
    extra = []
    if '--extra' in sys.argv:
        extra = [w.strip().lower() for w in sys.argv[sys.argv.index('--extra') + 1].split(',') if w.strip()]
    allow_f = ROOT / 'scripts' / 'privacy_allow.txt'
    allow = {l.strip() for l in allow_f.read_text(encoding='utf-8').splitlines() if l.strip()} if allow_f.exists() else set()
    items = json.loads((ROOT / 'items.json').read_text(encoding='utf-8'))['items']
    bad = []
    for i in items:
        text = f"{i['t']} {i.get('n', '')} {i.get('zh', '')}"
        low = text.lower()
        for w in WORDS:
            if re.search(r'\b' + re.escape(w) + r's?\b', low) and i['t'] not in allow:
                bad.append(f"items.json: '{i['t']}' contains '{w}' (approve it in scripts/privacy_allow.txt if it is fine)")
        for w in extra:
            if w in low:
                bad.append(f"items.json: '{i['t']}' contains a private word")
        for rx in DATE:
            if rx.search(text):
                bad.append(f"items.json: '{i['t']}' contains a date")
        if set(i) - {'key', 'k', 't', 'id', 'n', 'alt', 'zh'}:
            bad.append(f"items.json: '{i['t']}' has extra fields {sorted(set(i) - {'key','k','t','id','n','alt','zh'})}")
    # private words must not appear anywhere in the published files
    for p in ['index.html', 'README.md', *[str(x.relative_to(ROOT)) for x in (ROOT / 'categories').glob('*.md')]]:
        low = (ROOT / p).read_text(encoding='utf-8').lower()
        for w in extra:
            if w in low:
                bad.append(f'{p}: contains a private word')
        if DATE[0].search(low):
            bad.append(f'{p}: contains a date')
    if bad:
        print('Privacy check FAILED:')
        print('\n'.join(sorted(set(bad))))
        sys.exit(1)
    print(f'Privacy check passed ({len(items)} items).')

if __name__ == '__main__':
    main()

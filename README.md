# MAR2 — Figure Review Dashboard

A static dashboard for coordinating figure iterations across the Second Mediterranean
Assessment Report (MAR2), coordinated by MedECC: 7 chapters + the Summary for
Policymakers (SPM).

Forked from the AMOC in Focus figure dashboard.

## Publish at mar2.graphicsinscience.com (one-time setup)

The dashboard is its own GitHub Pages site on a subdomain of graphicsinscience.com, so it
deploys independently of the portfolio site in `Website_GraphicsinScience`.

1. Push this folder to `https://github.com/andres-alegria/MedECC_Figures_Dashboard`.
2. In the repo: **Settings → Pages → Source: Deploy from a branch → main / (root)**.
3. Same page, **Custom domain**: `mar2.graphicsinscience.com` → Save. (This is what the
   `CNAME` file in the repo root holds; Pages keeps the two in step.)
4. At **Squarespace Domains → graphicsinscience.com → DNS**, add:
   `CNAME   mar2   →   andres-alegria.github.io.`
5. Back in Settings → Pages, wait for the DNS check to pass, then tick **Enforce HTTPS**.

DNS usually resolves within minutes, occasionally up to an hour. The portfolio site at
`www.graphicsinscience.com` is untouched — a different repo, a different hostname.

`robots.txt` and a `noindex` meta tag keep draft figures out of search results.

## Adding a figure version

Drop the file into `figures/` using the naming scheme:

```
Ch_<chapter>_Figure_<number>[letter]_v<version>.png     e.g. Ch_2_Figure_3_v1.png
Ch_SPM_Figure_<number>_v0.png                           for SPM figures
Ch_<chapter>_Figure_<Name>_v<version>.jpg               named, not yet numbered, e.g. Ch_SPM_Figure_CRD_v1.jpg
```

Chapter is 1-7 or SPM. Names must start with a letter and use only letters, digits and
hyphens (no underscores or spaces). PNG, JPG and JPEG all work.

Then run `python3 scripts/update_figures.py` and commit + push. The script:
- regenerates `figures-data.js` (keeping all titles/captions/contacts you've filled in),
- creates the missing thumbnails in `thumbs/`.

Needs Pillow for thumbnails: `pip install Pillow`.

## Editing the figure text

`Figures.xlsx` in the repo root is the source of truth for all figure text. Each row is one
figure, matched by its Chapter and Figure columns. Edit it, commit and push — no need to
re-run the script for text-only changes.

`figures-data.js` holds the same fields as a fallback when the spreadsheet cannot be read.

## Passphrase

The access gate accepts the passphrase defined in `index.html`
(search for `tryGate` — currently `MAR2`, matched case-insensitively). It is a light
client-side gate: it deters casual visitors but is not real security; the image URLs remain
technically public.

## Author comments — how delivery works

Each "Send feedback" click posts the comment to Web3Forms, which emails it to the
coordinator with the figure name as the subject line (e.g. "Fig. 4.2"). The public access
key lives in `index.html` (search for `accessKey`). No backend or account is needed.

- The comment also stays visible in the sender's own browser (localStorage), so authors can
  see what they already sent. Other authors do not see each other's comments.
- To show everyone's comments on the dashboard, export the submissions from Web3Forms as
  CSV and save them as `comments.csv` in the repo root (columns:
  `Submitted At,Name,Comment,Figure,Subject`).
- To change the destination address or key, use the Web3Forms dashboard.

## Colours

Taken from medecc.org: slate `#43566F`, logo blue `#6C9ECE`, accent orange `#E86B00`,
light tint `#EEF6FD`.

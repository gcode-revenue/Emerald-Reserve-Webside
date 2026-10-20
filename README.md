# Emerald Reserve — emeraldreservepr.com

Marketing website for **Emerald Reserve**, a private lakefront community of 10 exclusive residences in Puerto Rico (Friends & Family pre-sale, delivery Summer 2027).

## Pages

| File | Purpose |
| --- | --- |
| `index.html` | Landing page — hero, overview, key facts, residences, finishes, site plan, gallery |
| `the-project.html` | Project details — overview, architecture, amenities, site plan, timeline |
| `contact.html` | Developer contact (Miguel Portilla) and pre-sale inquiry form |
| `404.html` | Not-found page |

Plain static HTML/CSS/JS — no build step. Shared styles live in `css/styles.css`, interactions in `js/main.js`.

## Contact form

The inquiry form opens the visitor's email app with a pre-filled message to `maportilla@emeraldreservepr.com` (no server needed). To receive submissions directly instead, point the form at a form service (e.g. Formspree) and remove the `mailto` handler in `js/main.js`.

## Hosting (GitHub Pages)

1. Repository **Settings → Pages** → Source: *Deploy from a branch*, branch `main`, folder `/ (root)`.
2. The `CNAME` file sets the custom domain to `emeraldreservepr.com`.
3. At your domain registrar, add DNS records:
   - `A` records for `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` record for `www` → `gcode-revenue.github.io`
4. Once DNS resolves, enable **Enforce HTTPS** in Settings → Pages.

## Local preview

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

All imagery consists of AI-generated conceptual renderings for illustration only.

# KU Tech website: build source (branch `build-source`)

This branch holds the tools that generate the website. The live site is the `main` branch (served by GitHub Pages at https://kutech.it). Nothing on this branch is published.

## Files
- `body.html`: master template. It holds the design (CSS inside `<style>`), the shared header and footer, the Home, Services overview, About and Contact page content, and the site script.
- `seo_data.py`: site address (`SITE`), company description, and the content of the 12 service pages (titles, search descriptions, intro, included items, who it's for, how it's delivered, FAQs, related services, photo).
- `build.py`: generates every page with SEO tags, structured data, sitemap.xml and robots.txt. `dist/` is the hosted version; `preview/` is an all-in-one version for Claude artifact previews.
- `images/`: web images, logos (SVG and PNG), favicon, social sharing image.

## Rebuild and publish
```
python3 build.py              # writes dist/ and preview/
# copy dist/* into a checkout of main, keep CNAME and .nojekyll, commit, push
```
Requires Python 3 only. After editing text in `body.html` or `seo_data.py`, rebuild so all 17 pages, the sitemap and structured data stay consistent.

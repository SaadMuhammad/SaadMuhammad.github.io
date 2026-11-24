# Muhammad Saad Uddin

A complete multi-page GitHub Pages portfolio, with Markdown articles and short notes.

## Pages

| URL | Content |
| --- | --- |
| `/` | Introduction, selected work, latest articles and notes, speaking highlight |
| `/work/` | Enterprise AI work and existing projects |
| `/writing/` | Searchable articles with topic filters |
| `/writing/<slug>/` | Full articles with images, code, tables, diagrams, and a table of contents |
| `/notes/` | Short posts and thoughts |
| `/notes/<slug>/` | Individual note with an optional original LinkedIn link |
| `/speaking/` | Your existing talks |
| `/about/` | Profile, experience, education, skills, achievements, credentials and résumé |

The current Writing page links to two verified published Medium articles. Full article text was not imported from those member-only pages. Notes has a deliberate empty state until you add your own posts. The private templates are excluded from the website.

## Deploy to your existing GitHub Pages address

1. Extract this ZIP. Copy the **contents** of `nordic-portfolio/` to the root of `SaadMuhammad/saadmuhammad.github.io`. Include the hidden `.github` folder. Commit the files to your normal `main` or `master` branch.
2. In the repository, open **Settings → Pages → Build and deployment → Source** and select **GitHub Actions**.
3. Open **Actions → Build and deploy portfolio**. The push should start it automatically; you can also select **Run workflow**.
4. Wait for both `build` and `deploy` to complete. The site stays at `https://saadmuhammad.github.io/`.

The workflow builds `_site/` from source, checks internal links, then deploys it. The old root `index.html` is no longer the source of the deployed page. Remove it after migration to avoid confusion. Existing images and the résumé are included in this package.

For a quick static upload instead, copy the **contents of `_site/`** to your existing Pages publishing root. That serves the prebuilt pages without running Python on the server. After future content changes, rebuild locally and upload the regenerated `_site/` contents again.

## Publish an article

1. Copy `content/templates/article.md` to `content/articles/my-article.md`.
2. Set `title`, `date`, `slug`, `description`, and `tags` in the YAML header.
3. Write the article using Markdown. Set `draft: false` when ready.
4. Commit and push. The new page, Writing list, homepage, RSS feed and sitemap update during the build.

```yaml
---
title: "My article title"
date: 2026-11-06
slug: my-article
description: "A short preview for readers."
tags: [Agents, Engineering]
draft: false
---
```

Dates in the future are excluded from ordinary builds. A scheduled date needs a build on/after that date; it does not publish itself at midnight. Slugs must be unique within each collection and use lowercase letters, numbers, and hyphens. Preserve slugs once shared so your links keep working.

## Publish a note or LinkedIn post

Copy `content/templates/note.md` to `content/notes/my-note.md`, replace the text, and set `draft: false`. Add `source_url` if you want a link to the original LinkedIn discussion. This is manual publishing; the site does not scrape or synchronize LinkedIn.

## Images, diagrams, and code

Put images in `images/`, then use `![Descriptive alt text](/images/example.png)` in Markdown. Use explicit SVG/PNG exports for diagrams that must display offline. Fenced `mermaid` blocks are rendered interactively with Mermaid in the browser. If its CDN is unavailable, the diagram source remains visible. Fenced code blocks have a Copy button; Markdown tables and headings are supported.

## Link to an existing external article

Set `external_url: https://...` and `source: Medium` in an article's header. Its card will link directly to the original. To publish the full article here later, remove `external_url` and add the body below the YAML header. Only publish material you intend to make public.

## Preview locally

Python 3.12 or newer:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate
pip install -r requirements.txt
python scripts/build.py
python scripts/check.py
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000`. Rebuild and refresh after changes. Use `python scripts/build.py --drafts` to include private drafts and future-dated posts locally; normal deployment excludes them.

## Where to edit

- `site.json`: identity, social links, domain and optional repository `base_path`.
- `content/profile.json`: work history, skills, projects, talks and credentials.
- `content/articles/*.md`: articles and external article links.
- `content/notes/*.md`: short notes.
- `assets/css/main.css`: Nordic palette, typography and layouts.
- `assets/js/main.js`: mobile menu, search, topic filters, code copying and diagrams.
- `scripts/build.py`: shared page layouts, homepage and publication logic.

For the personal `github.io` root, keep `base_path` empty. For a project site such as `/my-project/`, set `base_path` to `/my-project` and rebuild.

## Contact contrast fix

The old `.section:nth-child(even)` rule overrode the contact background but retained pale contact text. The new footer uses a dedicated `.site-footer` component with explicit background `#294753`, heading `#F3F6F5`, and body `#D5E2E3`, independent of page section order.

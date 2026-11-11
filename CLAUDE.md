# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal static site (professional: advocacia/Legal Ops; hobbies) written in **pure HTML5: no CSS, no JavaScript, no build step, no tests**. Content is in Brazilian Portuguese (`lang="pt-BR"`). The owner adds and removes content by hand, so keeping that workflow simple is the main design goal.

The one exception to "no build step": `_scripts/atualizar_xadrez.py` (Python stdlib only) pulls the owner's Chess.com ratings (user `iterando_xadrez`; ratings table only, recent games were removed on purpose) from the public Published-Data API and rewrites the block between `<!-- chesscom:inicio -->` and `<!-- chesscom:fim -->` in `hobbies/index.html` as static HTML. `.github/workflows/atualizar-xadrez.yml` runs it daily (10:00 UTC, plus manual `workflow_dispatch`) and commits as `github-actions[bot]` only when data changed. The published site stays pure HTML.

## Running

```bash
python3 -m http.server 8000
```

Opening `index.html` directly via `file://` must also keep working.

## Structure

- `index.html`: landing page (bio, "Como Posso Ajudar" service summary, `#contato` split into Profissional (WhatsApp, LinkedIn) and Redes pessoais (Instagram, Chess.com), links to sections, "Sobre Este Site"). The nav "Contato" item points to `index.html#contato` (there is no separate contact page). `atualmente.html`: now page ("Atualmente").
- `profissional/index.html` ("Profissional"): fixed `#servicos` section ("Principais Serviços que Realizo", one `<dl>` per service so the `<dd>` text renders indented under the name, ending in a WhatsApp CTA), then advocacia/Legal Ops areas, then the articles list for `profissional/artigos/` (hidden, see below); `hobbies/index.html` has one `<section>` per hobby (currently `#xadrez`, with the generated Chess.com block plus the studies list and the hand-kept games table, both hidden); hobby texts live in `hobbies/estudos/`.
- WhatsApp contact is `https://wa.me/5562999434595?text=...`, shown as (62) 99943-4595, in two places (home `#contato`/"Como Posso Ajudar" and end of `#servicos`). No public e-mail, by the owner's choice.
- `_modelos/artigo.html` is the template for new articles/studies (written for depth-2 paths, `../../`). `_modelos/LEIA-ME.txt` is the owner's add/remove guide (in Portuguese). Keep it in sync if the workflow changes.

## Conventions

- **No CSS/JS by design.** The footer says "Feito puramente em HTML5". The dark theme comes only from `<meta name="color-scheme" content="dark">`, which every page needs (including the template).
- **No includes exist**, so the `<header>`/`<nav>`, the `<head>` block and the footer are duplicated in every page. Any change must be applied to all pages and to the template: `grep -rl "<nav>" --include=*.html .`
- **Nav:** each section page marks its own link with `aria-current="page"`; articles and the template mark none (the breadcrumb covers it).
- **Every `<head>`** has a page-specific `<meta name="description">`, Open Graph (`og:title`, `og:description`, `og:type` = `website`, or `article` in the template, `og:locale` = `pt_BR`, `og:site_name`) and the same inline `data:` SVG favicon. There is no `og:image` yet.
- **Footer on every page:** `&copy; 2026 Christopher Luduvico · OAB/GO n. 55.987 · Goiânia - GO. Feito puramente em HTML5.` The OAB number is required in lawyer advertising (Código de Ética da OAB, art. 44); never drop it. `grep -rL 'OAB/GO n. 55.987' --include=*.html .` should return nothing.
- **Hidden sections:** sections with no real content yet are wrapped in an HTML comment that opens with `<!-- NOME (escondido ...)` and closes with a line `fim -->`. Comments cannot nest, so nothing inside may contain `<!--` or `-->`. Don't publish placeholder or sample content visibly.
- **External links open in the same tab** (no `target="_blank"`), and the hand-written ones carry no `rel="noopener"`.
- **Links are relative and point at explicit files** (`hobbies/index.html`, `../../atualmente.html`). Never use root-absolute (`/x`) or directory links (`x/`): they break under `file://` and on a GitHub Pages project subpath. `grep -r 'href="/' .` should return nothing.
- **Content files are named `AAAA-MM-tema.html`** (lowercase, no accents). Section lists and the games table are newest-first. Each list item is `<li><time datetime="YYYY-MM-DD">MM/AAAA</time> · <a href="...">Título</a></li>`.
- **Dates are written twice:** ISO in the `datetime` attribute and pt-BR in the visible text. Update both.
- **Never hand-edit between the `chesscom:` markers**: the script overwrites it. Change the generator (`gerar_html()` in the script) instead, then run it. The script exits without touching the page if the API fails or the markers are missing, and it ignores the "Atualizado automaticamente em" line when deciding whether anything changed.

## Known placeholders

- The hidden articles, studies and games blocks hold one example `<li>`/`<tr>` each (`AAAA-MM-tema`, `NUMERO`) to be replaced when they are shown.

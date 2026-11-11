# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal static site (professional: advocacia/Legal Ops; hobbies) written in **pure HTML5: no CSS, no JavaScript, no build step, no tests**. Content is in Brazilian Portuguese (`lang="pt-BR"`). The owner adds and removes content by hand, so keeping that workflow simple is the main design goal.

The one exception to "no build step": `_scripts/atualizar_xadrez.py` (Python stdlib only) pulls the owner's Chess.com data (user `iterando_xadrez`) from the public Published-Data API and rewrites the block between `<!-- chesscom:inicio -->` and `<!-- chesscom:fim -->` in `hobbies/index.html` as static HTML. `.github/workflows/atualizar-xadrez.yml` runs it daily (10:00 UTC, plus manual `workflow_dispatch`) and commits as `github-actions[bot]` only when data changed. The published site stays pure HTML.

## Running

```bash
python3 -m http.server 8000
```

Opening `index.html` directly via `file://` must also keep working.

## Structure

- `index.html`: landing page (bio, `#contato` section with LinkedIn/Instagram/Chess.com links, links to sections). The nav "Contato" item points to `index.html#contato` (there is no separate contact page). `atualmente.html`: now page ("Atualmente").
- `profissional/index.html` ("Profissional"): fixed `#servicos` section ("Principais Serviços que Realizo", one `<h3>` + `<p>` per service), then advocacia/Legal Ops areas, then lists articles in `profissional/artigos/`; `hobbies/index.html` has one `<section>` per hobby (currently `#xadrez`, with the generated Chess.com block, its studies list and the hand-kept games table); hobby texts live in `hobbies/estudos/`.
- `_modelos/artigo.html` is the template for new articles/studies (written for depth-2 paths, `../../`). `_modelos/LEIA-ME.txt` is the owner's add/remove guide (in Portuguese). Keep it in sync if the workflow changes.

## Conventions

- **No CSS/JS by design.** The footer says "Feito puramente em HTML5". The dark theme comes only from `<meta name="color-scheme" content="dark">`, which every page needs (including the template).
- **No includes exist**, so the `<header>`/`<nav>` is duplicated in every page. Any nav change must be applied to all pages and to the template: `grep -rl "<nav>" --include=*.html .`
- **Links are relative and point at explicit files** (`hobbies/index.html`, `../../atualmente.html`). Never use root-absolute (`/x`) or directory links (`x/`): they break under `file://` and on a GitHub Pages project subpath. `grep -r 'href="/' .` should return nothing.
- **Content files are named `AAAA-MM-tema.html`** (lowercase, no accents). Section lists and the games table are newest-first. Each list item is `<li><time datetime="YYYY-MM-DD">MM/AAAA</time> · <a href="...">Título</a></li>`.
- **Dates are written twice:** ISO in the `datetime` attribute and pt-BR in the visible text. Update both.
- **Never hand-edit between the `chesscom:` markers**: the script overwrites it. Change the generator (`gerar_html()` in the script) instead, then run it. The script exits without touching the page if the API fails or the markers are missing, and it ignores the "Atualizado automaticamente em" line when deciding whether anything changed.

## Known placeholders

- The games table's "Ver PGN" link points to the generic `https://chess.com`.
- `hobbies/estudos/2026-11-sistema-london.html` is sample content.

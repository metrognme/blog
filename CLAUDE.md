# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal static site (advocacia, Legal Ops, xadrez) written in **pure HTML5: no CSS, no JavaScript, no build step, no tests**. Content is in Brazilian Portuguese (`lang="pt-BR"`). The owner adds and removes content by hand, so keeping that workflow simple is the main design goal.

## Running

```bash
python3 -m http.server 8000
```

Opening `index.html` directly via `file://` must also keep working.

## Structure

- `index.html`: landing page (short bio + links to sections). `agora.html`: now page. `contato.html`: Formspree form.
- `advocacia/index.html` lists articles in `advocacia/artigos/`; `xadrez/index.html` lists studies in `xadrez/estudos/` and holds the games table.
- `_modelos/artigo.html` is the template for new articles/studies (written for depth-2 paths, `../../`). `_modelos/LEIA-ME.txt` is the owner's add/remove guide (in Portuguese). Keep it in sync if the workflow changes.

## Conventions

- **No CSS/JS by design.** The footer says "Feito puramente em HTML5". The dark theme comes only from `<meta name="color-scheme" content="dark">`, which every page needs (including the template).
- **No includes exist**, so the `<header>`/`<nav>` is duplicated in every page. Any nav change must be applied to all pages and to the template: `grep -rl "<nav>" --include=*.html .`
- **Links are relative and point at explicit files** (`xadrez/index.html`, `../../agora.html`). Never use root-absolute (`/x`) or directory links (`x/`): they break under `file://` and on a GitHub Pages project subpath. `grep -r 'href="/' .` should return nothing.
- **Content files are named `AAAA-MM-tema.html`** (lowercase, no accents). Section lists and the games table are newest-first. Each list item is `<li><time datetime="YYYY-MM-DD">MM/AAAA</time> · <a href="...">Título</a></li>`.
- **Dates are written twice:** ISO in the `datetime` attribute and pt-BR in the visible text. Update both.

## Known placeholders

- `contato.html` posts to `https://formspree.io/f/seu-id`. `seu-id` must be replaced with a real Formspree ID.
- The games table's "Ver PGN" link points to the generic `https://chess.com`.
- `xadrez/estudos/2026-11-sistema-london.html` is sample content.

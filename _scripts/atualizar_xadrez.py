#!/usr/bin/env python3
"""Atualiza o bloco do Chess.com em hobbies/index.html.

Busca os ratings na Published-Data API do Chess.com
(pública, sem chave) e reescreve o trecho entre os marcadores
<!-- chesscom:inicio --> e <!-- chesscom:fim -->. O site continua sendo só
HTML: este script roda antes da publicação (no GitHub Actions ou à mão).

Uso:  python3 _scripts/atualizar_xadrez.py
"""

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

USUARIO = "iterando_xadrez"

API = f"https://api.chess.com/pub/player/{USUARIO}"
USER_AGENT = "site-pessoal-xadrez/1.0"
FUSO = ZoneInfo("America/Sao_Paulo")
PAGINA = Path(__file__).resolve().parent.parent / "hobbies" / "index.html"
INICIO = "<!-- chesscom:inicio -->"
FIM = "<!-- chesscom:fim -->"
MARCA_DATA = "Atualizado automaticamente em"
RECUO = " " * 12  # mesmo recuo do conteúdo de <section id="xadrez">

MODALIDADES = {
    "rapid": "Rápida",
    "blitz": "Blitz",
    "bullet": "Bullet",
    "daily": "Diária",
}


def buscar(url):
    """GET em JSON. Em qualquer falha encerra o script sem tocar na página."""
    pedido = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(pedido, timeout=30) as resposta:
            return json.load(resposta)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as erro:
        sys.exit(f"Erro ao buscar {url}: {erro}. A página não foi alterada.")


def gerar_html(stats):
    """Linhas do bloco (sem recuo), na ordem em que entram na página."""
    linhas = ["<h3>No Chess.com</h3>"]

    linhas += [
        '<table border="1">',
        "    <caption>Ratings</caption>",
        "    <thead>",
        "        <tr><th>Modalidade</th><th>Atual</th><th>Melhor</th><th>V / D / E</th></tr>",
        "    </thead>",
        "    <tbody>",
    ]
    for chave, nome in MODALIDADES.items():
        dados = stats.get(f"chess_{chave}")
        if not dados:
            continue
        r = dados["record"]
        linhas.append(
            f"        <tr><td>{nome}</td><td>{dados['last']['rating']}</td>"
            f"<td>{dados.get('best', {}).get('rating', '—')}</td>"
            f"<td>{r['win']} / {r['loss']} / {r['draw']}</td></tr>"
        )
    if "tactics" in stats:
        linhas.append(
            f"        <tr><td>Táticas</td><td>—</td>"
            f"<td>{stats['tactics']['highest']['rating']}</td><td>—</td></tr>"
        )
    if "puzzle_rush" in stats:
        linhas.append(
            f"        <tr><td>Puzzle Rush</td><td>—</td>"
            f"<td>{stats['puzzle_rush']['best']['score']}</td><td>—</td></tr>"
        )
    linhas += ["    </tbody>", "</table>"]

    agora = datetime.now(FUSO)
    linhas.append(
        f'<p><small>{MARCA_DATA} <time datetime="{agora.isoformat(timespec="minutes")}">'
        f"{agora:%d/%m/%Y às %H:%M}</time>.</small></p>"
    )
    return linhas


def sem_data(texto):
    """O bloco sem a linha "Atualizado em", para comparar só os dados."""
    return [l.strip() for l in texto.splitlines() if l.strip() and MARCA_DATA not in l]


def main():
    pagina = PAGINA.read_text(encoding="utf-8")
    ini, fim = pagina.find(INICIO), pagina.find(FIM)
    if ini == -1 or fim == -1 or fim < ini:
        sys.exit(f"Marcadores {INICIO} / {FIM} não encontrados em {PAGINA}.")

    stats = buscar(f"{API}/stats")

    bloco = "\n".join(RECUO + l if l else "" for l in gerar_html(stats))
    bloco_atual = pagina[ini + len(INICIO):fim]
    if sem_data(bloco) == sem_data(bloco_atual):
        print("Dados do Chess.com sem mudanças. Nada a gravar.")
        return

    nova = pagina[: ini + len(INICIO)] + "\n" + bloco + "\n" + RECUO + pagina[fim:]
    PAGINA.write_text(nova, encoding="utf-8")
    print(f"{PAGINA.name} atualizado.")


if __name__ == "__main__":
    main()

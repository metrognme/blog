#!/usr/bin/env python3
"""Atualiza o bloco do Chess.com em hobbies/index.html.

Busca perfil, ratings e últimas partidas na Published-Data API do Chess.com
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
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

USUARIO = "iterando_xadrez"
N_PARTIDAS = 10

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


def ultimas_partidas():
    """As N_PARTIDAS mais recentes, da mais nova para a mais antiga."""
    partidas = []
    for url_mes in reversed(buscar(f"{API}/games/archives")["archives"]):
        partidas.extend(reversed(buscar(url_mes)["games"]))
        if len(partidas) >= N_PARTIDAS:
            break
    return partidas[:N_PARTIDAS]


def cor_do_usuario(partida):
    """'white' ou 'black'. A API devolve o nome com maiúsculas (Iterando_Xadrez)."""
    if partida["white"]["username"].lower() == USUARIO.lower():
        return "white"
    return "black"


def resultado(partida):
    """Devolve "Vitória", "Derrota" ou "Empate" do ponto de vista de USUARIO."""
    # TODO(human)
    raise NotImplementedError


def data_html(timestamp):
    """<time datetime="AAAA-MM-DD">DD/MM/AAAA</time>, no fuso de Goiânia."""
    dia = datetime.fromtimestamp(timestamp, FUSO)
    return f'<time datetime="{dia:%Y-%m-%d}">{dia:%d/%m/%Y}</time>'


def gerar_html(perfil, stats, partidas):
    """Linhas do bloco (sem recuo), na ordem em que entram na página."""
    linhas = ["<h3>No Chess.com</h3>"]

    pais = perfil.get("country", "").rsplit("/", 1)[-1]
    linhas.append(
        f'<p><a href="{escape(perfil["url"])}" target="_blank" rel="noopener me">'
        f'{escape(perfil["username"])}</a> · membro desde {data_html(perfil["joined"])}'
        f' · {perfil.get("followers", 0)} seguidor(es) · {escape(pais)}</p>'
    )

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

    linhas += [
        "",
        '<table border="1">',
        "    <caption>Últimas partidas no Chess.com</caption>",
        "    <thead>",
        "        <tr><th>Data</th><th>Modalidade</th><th>Cor</th><th>Adversário</th>"
        "<th>Resultado</th><th>Link</th></tr>",
        "    </thead>",
        "    <tbody>",
    ]
    for p in partidas:
        cor = cor_do_usuario(p)
        rival = p["black" if cor == "white" else "white"]
        linhas.append(
            f"        <tr><td>{data_html(p['end_time'])}</td>"
            f"<td>{MODALIDADES.get(p['time_class'], escape(p['time_class']))}</td>"
            f"<td>{'Brancas' if cor == 'white' else 'Pretas'}</td>"
            f"<td>{escape(rival['username'])} ({rival['rating']})</td>"
            f"<td>{resultado(p)}</td>"
            f'<td><a href="{escape(p["url"])}" target="_blank" rel="noopener">Ver partida</a></td></tr>'
        )
    linhas += ["    </tbody>", "</table>"]

    agora = datetime.now(FUSO)
    linhas.append(
        f'<p><small>{MARCA_DATA} <time datetime="{agora:%Y-%m-%dT%H:%M%z}">'
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

    perfil = buscar(API)
    stats = buscar(f"{API}/stats")
    partidas = ultimas_partidas()

    bloco = "\n".join(RECUO + l if l else "" for l in gerar_html(perfil, stats, partidas))
    bloco_atual = pagina[ini + len(INICIO):fim]
    if sem_data(bloco) == sem_data(bloco_atual):
        print("Dados do Chess.com sem mudanças. Nada a gravar.")
        return

    nova = pagina[: ini + len(INICIO)] + "\n" + bloco + "\n" + RECUO + pagina[fim:]
    PAGINA.write_text(nova, encoding="utf-8")
    print(f"{PAGINA.name} atualizado com {len(partidas)} partidas.")


if __name__ == "__main__":
    main()

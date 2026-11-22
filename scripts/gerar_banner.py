"""Gera o banner do perfil: assets/banner.svg (tema claro) e assets/banner-dark.svg (tema escuro).

O banner é estático, sem animação, para não causar movimento inesperado.

Arte original: um galho com folhas rosadas cuja raiz vira trilha de circuito e
uma linha de dados que sobe. Rode com: python3 scripts/gerar_banner.py
"""
import math
from pathlib import Path

W, H = 1200, 300

# Galho: duas curvas de Bézier cúbicas encadeadas (início -> meio -> fim).
SEGMENTOS = [
    ((120, 236), (300, 230), (420, 150), (600, 150)),
    ((600, 150), (780, 150), (900, 96), (1080, 92)),
]


def ponto(seg, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = seg
    a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
    return a * x0 + b * x1 + c * x2 + d * x3, a * y0 + b * y1 + c * y2 + d * y3


def angulo(seg, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = seg
    dx = 3 * (1 - t) ** 2 * (x1 - x0) + 6 * (1 - t) * t * (x2 - x1) + 3 * t ** 2 * (x3 - x2)
    dy = 3 * (1 - t) ** 2 * (y1 - y0) + 6 * (1 - t) * t * (y2 - y1) + 3 * t ** 2 * (y3 - y2)
    return math.degrees(math.atan2(dy, dx))


def caminho_galho():
    p = SEGMENTOS[0][0]
    d = f"M{p[0]} {p[1]}"
    for _, c1, c2, fim in SEGMENTOS:
        d += f" C {c1[0]} {c1[1]}, {c2[0]} {c2[1]}, {fim[0]} {fim[1]}"
    return d


# Folha com a base na origem, apontando para +x (comprimento 58).
FOLHA = "M0 0 C 14 -15, 40 -17, 58 0 C 40 17, 14 15, 0 0 Z"
NERVURA = "M2 0 Q 30 -2 56 0"
# Nervura em "circuito": ângulo reto e um ponto de solda.
NERVURA_CIRCUITO = "M2 0 L 24 0 L 34 -6 L 44 -6"

# (segmento, t, lado, tamanho, circuito?)
FOLHAS = [
    (0, 0.30, -1, 0.85, False),
    (0, 0.42, 1, 0.9, False),
    (0, 0.62, -1, 1.0, True),
    (0, 0.82, 1, 1.0, False),
    (1, 0.10, -1, 1.05, False),
    (1, 0.30, 1, 1.0, True),
    (1, 0.52, -1, 0.95, False),
    (1, 0.72, 1, 0.85, False),
    (1, 0.88, -1, 0.75, False),
]

DADOS = [(250, 266), (380, 258), (510, 262), (640, 240), (770, 232), (900, 208), (1030, 196)]

BRILHOS = [(200, 96, 13, "cheio"), (650, 62, 10, "suave"), (1124, 168, 9, "cheio"), (470, 92, 6, "suave")]

TEMAS = {
    "banner.svg": dict(fundo="#FFF6F9", tinta="#1f1f1f", folha="#F8C8DC", miolo="#ffffff", suave="#F8C8DC"),
    "banner-dark.svg": dict(fundo="#1f1f1f", tinta="#F8C8DC", folha="#3a2a31", miolo="#1f1f1f", suave="#F8C8DC"),
}


def brilho(x, y, r):
    q = r * 0.18
    return (f"M{x} {y - r} Q {x + q} {y - q} {x + r} {y} Q {x + q} {y + q} {x} {y + r} "
            f"Q {x - q} {y + q} {x - r} {y} Q {x - q} {y - q} {x} {y - r} Z")


def svg(t):
    partes = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">malu</title>
  <desc id="d">Um galho delicado com folhas rosadas cresce da esquerda para a direita; a raiz vira trilhas de circuito e pequenos pontos formam uma linha de dados que sobe.</desc>
  <style>
    .tinta {{ stroke: {t["tinta"]}; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
    .folha {{ fill: {t["folha"]}; stroke: {t["tinta"]}; stroke-width: 1.5; stroke-linejoin: round; }}
    .nervura {{ stroke: {t["tinta"]}; stroke-width: 1.1; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
    .no {{ fill: {t["miolo"]}; stroke: {t["tinta"]}; stroke-width: 1.5; }}
    .solda {{ fill: {t["tinta"]}; }}
    .dados {{ stroke: {t["tinta"]}; stroke-width: 1.2; fill: none; stroke-dasharray: 1 7; stroke-linecap: round; opacity: .8; }}
    .cheio {{ fill: {t["tinta"]}; }}
    .suave {{ fill: {t["suave"]}; stroke: {t["tinta"]}; stroke-width: 1; }}
  </style>
  <rect x="0" y="0" width="{W}" height="{H}" rx="28" fill="{t["fundo"]}"/>''']

    # raiz -> circuito
    rx, ry = SEGMENTOS[0][0]
    trilhas = [
        f"M{rx} {ry} L {rx - 18} {ry + 18} L {rx - 46} {ry + 18}",
        f"M{rx} {ry} L {rx} {ry + 22} L {rx - 14} {ry + 36}",
        f"M{rx} {ry} L {rx + 16} {ry + 16} L {rx + 16} {ry + 38}",
    ]
    fins = [(rx - 51, ry + 18), (rx - 17.5, ry + 39.5), (rx + 16, ry + 43)]
    partes.append("  <!-- raiz que vira trilhas de circuito -->")
    for d in trilhas:
        partes.append(f'  <path class="tinta" stroke-width="1.5" d="{d}"/>')
    for x, y in fins:
        partes.append(f'  <circle class="no" cx="{x}" cy="{y}" r="4.5"/>')

    partes.append("  <!-- galho -->")
    partes.append(f'  <path class="tinta" stroke-width="2.2" d="{caminho_galho()}"/>')

    partes.append("  <!-- folhas: posição e ângulo calculados sobre a curva do galho -->")
    for s, tt, lado, esc, circ in FOLHAS:
        x, y = ponto(SEGMENTOS[s], tt)
        a = angulo(SEGMENTOS[s], tt) + lado * 42
        nerv = NERVURA_CIRCUITO if circ else NERVURA
        solda = '<circle class="solda" cx="46" cy="-6" r="2.2"/>' if circ else ""
        partes.append(
            f'  <g transform="translate({x:.1f} {y:.1f}) rotate({a:.1f}) scale({esc})">'
            f'<g>'
            f'<path class="folha" d="{FOLHA}"/><path class="nervura" d="{nerv}"/>{solda}</g></g>')

    # broto na ponta
    fx, fy = SEGMENTOS[-1][-1]
    partes.append(f'  <circle class="folha" cx="{fx + 5}" cy="{fy - 1}" r="6"/>')

    partes.append("  <!-- linha de dados que sobe -->")
    d = "M" + " L ".join(f"{x} {y}" for x, y in DADOS)
    partes.append(f'  <path class="dados" d="{d}"/>')
    for x, y in DADOS:
        partes.append(f'  <circle class="no" cx="{x}" cy="{y}" r="3.6"/>')

    partes.append("  <!-- brilhos -->")
    for x, y, r, tipo in BRILHOS:
        partes.append(f'  <path class="{tipo}" d="{brilho(x, y, r)}"/>')

    partes.append("</svg>\n")
    return "\n".join(partes)


if __name__ == "__main__":
    pasta = Path(__file__).resolve().parent.parent / "assets"
    for nome, tema in TEMAS.items():
        (pasta / nome).write_text(svg(tema), encoding="utf-8")
        print(nome, (pasta / nome).stat().st_size, "bytes")

"""Render the profile's SVG buttons and stat cards in the banner's style.

Run directly to (re)generate the static link buttons into assets/.
"""

import os
from html import escape

ASSETS = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
FONT_SANS = "'Segoe UI', Helvetica, Arial, sans-serif"
FONT_MONO = "'Consolas', 'SFMono-Regular', monospace"

DEFS = """
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0f0f0f"/>
      <stop offset="1" stop-color="#0d2a22"/>
    </linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/>
      <stop offset=".5" stop-color="#fff" stop-opacity=".14"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>"""


def _svg(width, height, body, style=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <defs>{DEFS}
    <clipPath id="clip"><rect width="{width}" height="{height}" rx="12"/></clipPath>
  </defs>
  <style>
    .sweep {{ animation: sweep 5s ease-in-out infinite; }}
    @keyframes sweep {{ 0% {{ transform: translateX(-120px) }} 60%, 100% {{ transform: translateX({width + 120}px) }} }}
    {style}
  </style>
{body}
</svg>
"""


def _frame(width, height, accent):
    return f"""  <g clip-path="url(#clip)">
    <rect width="{width}" height="{height}" fill="url(#bg)"/>
    <g transform="skewX(-20)"><rect class="sweep" x="0" y="0" width="90" height="{height}" fill="url(#shine)"/></g>
  </g>
  <rect x=".75" y=".75" width="{width - 1.5}" height="{height - 1.5}" rx="11.5" fill="none" stroke="{accent}" stroke-opacity=".45"/>"""


def button(label, accent, width):
    height = 44
    body = f"""{_frame(width, height, accent)}
  <circle cx="22" cy="22" r="4" fill="{accent}"/>
  <text x="38" y="28" class="label">{escape(label)}</text>
  <text x="{width - 20}" y="28" class="arrow" text-anchor="end">↗</text>"""
    style = (
        f".label {{ font: 600 15px {FONT_SANS}; fill: #d7f7ec; }}"
        f" .arrow {{ font: 700 16px {FONT_SANS}; fill: {accent}; }}"
    )
    return _svg(width, height, body, style).replace(
        'role="img"', f'role="img" aria-label="{escape(label)}"'
    )


def tiles(title, items, accent="#42dca3"):
    """items: list of (value, label). Returns a card with one column per item."""
    width, height = 600, 104
    col = (width - 40) / len(items)
    cells = []
    for i, (value, label) in enumerate(items):
        cx = 20 + col * i + col / 2
        if i:
            x = 20 + col * i
            cells.append(f'  <rect x="{x:.1f}" y="40" width="1" height="46" fill="{accent}" fill-opacity=".25"/>')
        cells.append(
            f'  <text x="{cx:.1f}" y="68" class="num" text-anchor="middle" style="animation-delay:{i * 0.15:.2f}s">{escape(str(value))}</text>\n'
            f'  <text x="{cx:.1f}" y="88" class="cap" text-anchor="middle">{escape(label)}</text>'
        )
    body = f"""{_frame(width, height, accent)}
  <text x="20" y="26" class="title">{escape(title)}</text>
{chr(10).join(cells)}"""
    style = (
        f".title {{ font: 400 13px {FONT_MONO}; fill: #7a9a90; }}"
        f" .num {{ font: 800 28px {FONT_SANS}; fill: {accent}; animation: rise .8s ease-out both; }}"
        f" .cap {{ font: 400 12px {FONT_MONO}; fill: #7a9a90; }}"
        " @keyframes rise { from { opacity: 0; transform: translateY(6px) } to { opacity: 1; transform: none } }"
    )
    return _svg(width, height, body, style).replace(
        'role="img"', f'role="img" aria-label="{escape(title)}: ' + ", ".join(f"{v} {l}" for v, l in items) + '"'
    )


def write(name, svg):
    os.makedirs(ASSETS, exist_ok=True)
    with open(os.path.join(ASSETS, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)


if __name__ == "__main__":
    write("btn-portfolio.svg", button("Portfolio", "#42dca3", 170))
    write("btn-linkedin.svg", button("LinkedIn", "#4aa3ff", 170))
    write("btn-demos.svg", button("Live Demos · WebAssembly", "#8b7bff", 270))

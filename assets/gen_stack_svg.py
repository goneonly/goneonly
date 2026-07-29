#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub README용 애니메이션 테크스택 배지 SVG 생성기.

- 순차 등장(stagger fade-in + slide up) 후 은은한 부유(float) 루프
- 투명 배경 (라이트/다크 모드 양쪽에서 자연스러움)
- 아이콘은 simple-icons 경로를 SVG 안에 인라인으로 박아넣음 (외부 요청 0)
- 행(row) 단위로 직접 그룹핑, 각 행 가운데 정렬
- prefers-reduced-motion 존중

사용법:
    pip install simpleicons
    python gen_stack_svg.py
    # -> tech-stack.svg, contact.svg

수정하려면 아래 ROWS 만 고치면 됩니다.
    ("표시할 라벨", "simple-icons 슬러그", "색상 오버라이드 or None")
슬러그는 https://simpleicons.org 에서 확인. 아이콘 없이 텍스트만 쓰려면 슬러그 자리에 None.
색상을 None으로 두면 simple-icons의 공식 브랜드 색을 자동으로 씁니다.
"""

ROWS = [
    # ── Languages ──
    [
        ("C",          None,         "a8b9cc"),   # 아이콘이 글자 'C'라 라벨과 중복 → 텍스트만
        ("Python",     "python",     "3776ab"),
        ("Java",       "@javacup",   "ed8b00"),   # 커피잔 마크 + Oracle 공식 Java 오렌지
    ],
    # ── Backend / Data ──
    [
        ("pandas",     "pandas",     "150458"),
        ("FastAPI",    "fastapi",    "009688"),   # 공식 teal
        ("Spring Boot","springboot", "6db33f"),
        ("MySQL",      None,         "4479a1"),   # 로고에 워드마크가 포함돼 15px에선 뭉개짐 → 텍스트만
    ],
    # ── Frontend ──
    [
        ("HTML5",      "html5",      "e34f26"),
        ("CSS",        "css3",       "1572b6"),
        ("JavaScript", "javascript", "f7df1e"),   # 밝은 노랑 → 자동으로 검정 글씨
        ("React",      "react",      "61dafb"),
    ],
    # ── Tools ──
    [
        ("Notion",     "notion",     "000000"),   # 거의 검정 → 자동 보정
        ("Prettier",   "prettier",   "f7b93e"),
        ("Git",        "git",        "f05032"),
    ],
    # ── Vision ──
    [
        ("OpenCV",     "opencv",     "5c3ee8"),   # 공식 OpenCV 퍼플
    ],
]

# Contact 섹션용 (링크는 README 쪽에서 <a>로 감쌉니다)
CONTACT = [
    [("Gmail", "gmail", "ea4335")],
]

FONT_SIZE = 13
BADGE_H = 32
GAP_X = 8
GAP_Y = 8
PAD_X = 13           # 배지 좌우 여백
ICON = 15            # 아이콘 한 변 크기
ICON_GAP = 7
RADIUS = 8
STAGGER = 0.075      # 배지 간 등장 간격(초)
FLOAT_PX = 3         # 부유 폭(px). 키우면 눈에 띄지만 산만해짐

# ---------------------------------------------------------------- helpers

_W = {}
for c in "abcdefghknopqrsuvxyz": _W[c] = 0.585
for c in "ijl.,:;'|!": _W[c] = 0.30
for c in "ft(){}[]/\\": _W[c] = 0.36
for c in "mw": _W[c] = 0.88
for c in "ABCDEFGHKLNOPQRSTUVXYZ": _W[c] = 0.68
for c in "MW": _W[c] = 0.92
for c in "IJ": _W[c] = 0.34
for c in "0123456789": _W[c] = 0.60
_W[" "] = 0.28
_W["-"] = 0.36
_W["+"] = 0.60
_W["#"] = 0.62


def text_width(s, size=FONT_SIZE):
    """볼드 산세리프 텍스트 폭 근사치. 살짝 넉넉하게 잡아 잘리지 않게 함."""
    return sum(_W.get(ch, 0.62) for ch in s) * size + 2


def luminance(hx):
    r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def mix(hx, target, amount):
    a = [int(hx[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(target[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(a, b))


# simple-icons에 없는 아이콘은 여기에 직접 정의합니다 (24x24 좌표계).
# Java는 상표 문제로 simple-icons에서 삭제돼서 커피잔 마크를 직접 그렸습니다.
# {fg} 자리에 배지 글자색이 들어갑니다.
CUSTOM_ICONS = {
    # 클래식 Java 커피잔 로고. simple-icons에는 상표 문제로 없어서 원본 PNG를
    # potrace로 벡터화한 뒤 24x24 좌표계로 정규화했습니다.
    "@javacup": '<g transform="translate(12 12) scale(1.2) translate(-12 -12)"><path fill="{fg}" fill-rule="evenodd" d="M10.71 23.93C9.35 23.83 7.65 23.62 7.02 23.46C6.77 23.4 6.79 23.4 7.37 23.43C8.56 23.48 14.56 23.46 15.41 23.4C16.75 23.3 17.55 23.15 18.57 22.82C19.13 22.64 20.07 22.19 20.38 21.96C20.5 21.86 20.61 21.8 20.63 21.81C20.68 21.86 20.41 22.27 20.14 22.53C19.57 23.08 18.71 23.42 17.33 23.64C15.23 23.98 12.91 24.08 10.71 23.93ZM7.59 22.73C4.86 22.56 3.45 22.18 3.2 21.55C3.07 21.23 3.19 20.98 3.58 20.79C3.96 20.6 5.07 20.39 6.15 20.32L6.53 20.29L5.92 20.45C4.99 20.69 4.5 20.94 4.54 21.16C4.58 21.36 5.4 21.61 6.53 21.77C9.44 22.18 12.88 22.16 16.04 21.72C17.66 21.49 19.21 21.09 19.35 20.85C19.37 20.81 19.4 20.71 19.42 20.62L19.45 20.45L19.55 20.62C19.76 20.94 19.61 21.23 19.1 21.5C18.12 22.02 16.3 22.43 13.83 22.67C12.96 22.75 8.65 22.79 7.59 22.73ZM10.24 20.42C8.45 20.25 7.49 19.84 7.49 19.24C7.49 18.91 7.82 18.69 8.5 18.57C8.66 18.55 8.68 18.55 8.63 18.6C8.6 18.64 8.57 18.72 8.57 18.79C8.57 18.86 8.6 18.94 8.63 18.96C8.84 19.13 10.26 19.31 11.44 19.32C12.31 19.32 12.51 19.29 14.27 18.99C14.43 18.96 14.5 18.99 15.05 19.33C15.38 19.53 15.65 19.71 15.64 19.73C15.63 19.75 15.36 19.85 15.04 19.95C14.38 20.17 13.51 20.36 12.81 20.43C12.24 20.49 10.85 20.48 10.24 20.42ZM9.49 17.8C8.38 17.65 7.88 17.54 7.37 17.31C7.02 17.15 6.79 16.92 6.79 16.75C6.79 16.53 7.18 16.25 7.72 16.09L7.97 16.02L7.82 16.15C7.34 16.6 8.01 16.84 10 16.93C11.28 16.99 13.36 16.79 14.74 16.47C14.92 16.42 15.09 16.41 15.12 16.43C15.15 16.45 15.37 16.6 15.61 16.76C16.01 17.04 16.04 17.07 15.94 17.11C15.79 17.16 14.05 17.5 13.48 17.59C12.03 17.8 10.23 17.9 9.49 17.8ZM17.48 17.32C18.89 16.27 19.69 15.3 19.7 14.63C19.7 14.39 19.51 14 19.31 13.83C19 13.56 18.21 13.29 17.73 13.29C17.47 13.29 17.5 13.23 17.81 13.11C18.38 12.9 18.64 12.85 19.09 12.85C19.48 12.85 19.57 12.87 19.83 12.98C20.2 13.15 20.49 13.46 20.66 13.87C21.02 14.79 20.9 15.39 20.2 16.09C19.78 16.5 19.39 16.75 18.66 17.07C18.27 17.23 17.29 17.57 17.18 17.57C17.16 17.57 17.3 17.46 17.48 17.32ZM8.55 15.47C6.6 15.34 5.34 14.96 5.13 14.43C4.86 13.75 5.84 13.34 8.1 13.2C8.5 13.17 8.83 13.16 8.84 13.17C8.85 13.18 8.63 13.24 8.35 13.31C7.09 13.64 6.45 14.06 6.9 14.27C7.81 14.71 13.78 14.62 16.19 14.13C16.76 14.02 16.75 14.02 16.54 14.17C15.81 14.66 14.31 15.13 12.8 15.33C11.76 15.48 9.71 15.54 8.55 15.47ZM13.1 13.64C13.29 13.18 13.37 12.84 13.4 12.49C13.43 12.01 13.4 11.94 12.87 11.25C12.22 10.4 11.98 9.77 11.98 8.9C11.98 8.41 11.98 8.37 12.14 8.05C12.45 7.4 13.41 6.59 14.71 5.87C15.22 5.59 16.37 5.05 16.39 5.08C16.4 5.09 16.12 5.33 15.77 5.61C15.03 6.21 14.01 7.2 13.78 7.54C13.54 7.9 13.41 8.25 13.41 8.57C13.41 8.91 13.53 9.18 13.99 9.9C14.6 10.87 14.7 11.5 14.35 12.25C14.15 12.68 13.59 13.35 13.2 13.63C13.07 13.73 13.06 13.73 13.1 13.64ZM11.03 12.46C9.95 11.5 9.1 10.26 8.85 9.28C8.62 8.34 8.82 7.58 9.58 6.57C10.1 5.88 10.63 5.43 12.4 4.16C13.15 3.62 13.64 3.12 13.87 2.68C14.24 1.98 14.43 1.06 14.38 0.33L14.35 -0.02L14.56 0.39C15.12 1.51 15.09 2.74 14.48 3.75C14.08 4.43 13.49 5.01 11.98 6.26C11.15 6.93 10.55 7.53 10.38 7.84C10.28 8.04 10.24 8.18 10.22 8.46C10.18 9.31 10.62 10.99 11.27 12.39C11.39 12.63 11.47 12.82 11.46 12.82C11.45 12.82 11.25 12.66 11.03 12.46Z"/></g>',
}


def get_icon(slug):
    """아이콘 마크업과 브랜드 색을 돌려준다. 없으면 (None, None)."""
    if not slug:
        return None, None
    if slug in CUSTOM_ICONS:
        return CUSTOM_ICONS[slug], None
    try:
        from simpleicons.all import icons
    except ImportError:
        print("  ! simpleicons 미설치 — 아이콘 없이 생성합니다 (pip install simpleicons)")
        return None, None
    alt = {"openjdk": ["openjdk", "java"], "css3": ["css3", "css"],
           "javascript": ["javascript", "js"], "c": ["c", "cprogramming"]}
    for cand in alt.get(slug, [slug]):
        ic = icons.get(cand)
        if ic:
            return f'<path d="{ic.path}" fill="{{fg}}" fill-opacity=".95"/>', \
                   ic.hex.lower().lstrip("#")
    print(f"  ! 아이콘 없음: {slug} (텍스트만 렌더링)")
    return None, None


# ---------------------------------------------------------------- build

def build(rows_spec):
    rows = []
    for spec in rows_spec:
        row = []
        for label, slug, override in spec:
            path, brand = get_icon(slug)
            color = (override or brand or "6e7781").lstrip("#").lower()
            w = PAD_X * 2 + text_width(label) + (ICON + ICON_GAP if path else 0)
            row.append(dict(label=label, path=path, color=color, w=round(w, 1)))
        rows.append(row)

    row_widths = [sum(i["w"] for i in r) + GAP_X * (len(r) - 1) for r in rows]
    total_w = round(max(row_widths))
    total_h = len(rows) * BADGE_H + (len(rows) - 1) * GAP_Y

    body, idx = [], 0
    for r, row in enumerate(rows):
        x = (total_w - row_widths[r]) / 2          # 행 가운데 정렬
        y = r * (BADGE_H + GAP_Y)
        for it in row:
            c = it["color"]
            lum = luminance(c)
            dark = lum < 0.16                       # 거의 검정인 브랜드 색 보정
            fill = "#" + (mix(c, "ffffff", 0.17) if dark else c)
            stroke = "#" + mix(c, "ffffff", 0.45) if dark else "#" + mix(c, "000000", 0.22)
            fg = "#ffffff" if luminance(fill[1:]) < 0.42 else "#12161a"

            delay = round(idx * STAGGER, 3)                # 등장 stagger
            fdelay = round(1.0 + (idx % 5) * 0.34, 3)      # 부유 위상차
            inner = []
            tx = x + PAD_X
            if it["path"]:
                s = ICON / 24
                iy = y + (BADGE_H - ICON) / 2
                inner.append(
                    f'<g transform="translate({tx:.1f} {iy:.1f}) scale({s:.5f})">'
                    + it["path"].replace("{fg}", fg) + '</g>'
                )
                tx += ICON + ICON_GAP
            inner.append(
                f'<text x="{tx:.1f}" y="{y + BADGE_H / 2 + 4.6:.1f}" '
                f'fill="{fg}" class="t">{it["label"]}</text>'
            )
            body.append(
                f'<g class="b" style="animation-delay:{delay}s,{fdelay}s">'
                f'<rect x="{x:.1f}" y="{y}" width="{it["w"]}" height="{BADGE_H}" '
                f'rx="{RADIUS}" fill="{fill}" stroke="{stroke}" stroke-opacity=".5"/>'
                f'<rect x="{x:.1f}" y="{y}" width="{it["w"]}" height="{BADGE_H}" '
                f'rx="{RADIUS}" fill="url(#sheen)"/>'
                + "".join(inner) + "</g>"
            )
            x += it["w"] + GAP_X
            idx += 1

    css = f"""
    .t {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
          Arial, sans-serif; font-size: {FONT_SIZE}px; font-weight: 600;
          letter-spacing: .1px; }}
    .b {{ animation: pop .55s cubic-bezier(.2,.85,.3,1) backwards,
                     float 3.6s ease-in-out infinite; }}
    @keyframes pop {{
      from {{ opacity: 0; transform: translateY(9px) scale(.96); }}
      to   {{ opacity: 1; transform: translateY(0)   scale(1);   }}
    }}
    @keyframes float {{
      0%, 100% {{ transform: translateY(0); }}
      50%      {{ transform: translateY(-{FLOAT_PX}px); }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .b {{ animation: none; }}
    }}"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}" fill="none" role="img" aria-label="Tech stack">
  <style>{css}
  </style>
  <defs>
    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".18"/>
      <stop offset="1" stop-color="#000" stop-opacity=".10"/>
    </linearGradient>
  </defs>
{chr(10).join("  " + b for b in body)}
</svg>
"""


if __name__ == "__main__":
    for name, spec in (("tech-stack.svg", ROWS), ("contact.svg", CONTACT)):
        svg = build(spec)
        with open(name, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"→ {name} ({len(svg):,} bytes)")

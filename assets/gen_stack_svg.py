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
        ("Java",       "openjdk",    "007396"),   # 클래식 Java 블루
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


def get_icon(slug):
    """simple-icons에서 path와 브랜드 색을 가져온다. 없으면 (None, None)."""
    if not slug:
        return None, None
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
            return ic.path, ic.hex.lower().lstrip("#")
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
                    f'<path d="{it["path"]}" fill="{fg}" fill-opacity=".95" '
                    f'transform="translate({tx:.1f} {iy:.1f}) scale({s:.5f})"/>'
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

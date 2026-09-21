from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import landscape, A3
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


MM = 72 / 25.4
PAGE_W_MM = 420
PAGE_H_MM = 297

OUT_PDF = Path("output/pdf/kvbng_drip_tape_03_dieline_a3.pdf")
OUT_SVG = Path("output/packaging/kvbng_drip_tape_03_dieline_a3.svg")

# Finished carton: 130 x 105 x 28 mm. Net fits one A3 landscape sheet.
X0 = 45
GLUE = 14
FACE = 130
DEPTH = 28
BODY_H = 105
TOP_Y = 68
BODY_Y = 96
BOTTOM_Y = BODY_Y + BODY_H

X_GLUE = X0
X_BACK = X_GLUE + GLUE
X_SIDE_1 = X_BACK + FACE
X_FRONT = X_SIDE_1 + DEPTH
X_SIDE_2 = X_FRONT + FACE
X_END = X_SIDE_2 + DEPTH

BLACK = "#09090b"
INK = "#171619"
CREAM = "#f2eee7"
GREEN = "#54f0a9"
ORANGE = "#ff6938"
PINK = "#e32482"
MUTED = "#7f7b78"
CUT = "#ff00a8"
CREASE = "#00aee8"


def mm(v):
    return v * MM


def register_fonts():
    fonts = {
        "Manrope": r"C:\Windows\Fonts\Manrope-Regular.ttf",
        "Manrope-SemiBold": r"C:\Windows\Fonts\Manrope-SemiBold.ttf",
        "Manrope-ExtraBold": r"C:\Windows\Fonts\Manrope-ExtraBold.ttf",
        "Unbounded": r"C:\Windows\Fonts\Unbounded-Regular.ttf",
        "Unbounded-Bold": r"C:\Windows\Fonts\Unbounded-Bold.ttf",
        "Unbounded-Black": r"C:\Windows\Fonts\Unbounded-Black.ttf",
    }
    for name, path in fonts.items():
        pdfmetrics.registerFont(TTFont(name, path))


def set_fill(c, color):
    c.setFillColor(HexColor(color))


def set_stroke(c, color):
    c.setStrokeColor(HexColor(color))


def rect(c, x, y, w, h, fill, stroke=None, width=0.2, radius=0):
    set_fill(c, fill)
    if stroke:
        set_stroke(c, stroke)
        c.setLineWidth(mm(width))
        do_stroke = 1
    else:
        do_stroke = 0
    if radius:
        c.roundRect(mm(x), mm(y), mm(w), mm(h), mm(radius), fill=1, stroke=do_stroke)
    else:
        c.rect(mm(x), mm(y), mm(w), mm(h), fill=1, stroke=do_stroke)


def line(c, x1, y1, x2, y2, color, width=0.25, dash=None):
    set_stroke(c, color)
    c.setLineWidth(mm(width))
    c.setDash(*(list(map(mm, dash)) if dash else []))
    c.line(mm(x1), mm(y1), mm(x2), mm(y2))
    c.setDash()


def polygon(c, points, fill, stroke=None, width=0.2):
    p = c.beginPath()
    p.moveTo(mm(points[0][0]), mm(points[0][1]))
    for x, y in points[1:]:
        p.lineTo(mm(x), mm(y))
    p.close()
    set_fill(c, fill)
    if stroke:
        set_stroke(c, stroke)
        c.setLineWidth(mm(width))
    c.drawPath(p, fill=1, stroke=1 if stroke else 0)


def circle(c, x, y, r, fill, stroke=None, width=0.2):
    set_fill(c, fill)
    if stroke:
        set_stroke(c, stroke)
        c.setLineWidth(mm(width))
    c.circle(mm(x), mm(y), mm(r), fill=1, stroke=1 if stroke else 0)


def text(c, x, y, value, font="Manrope", size=8, color=INK, tracking=None, align="left"):
    c.saveState()
    c.translate(mm(x), mm(y))
    c.scale(1, -1)
    set_fill(c, color)
    if tracking is None:
        c.setFont(font, size)
        if align == "center":
            c.drawCentredString(0, 0, value)
        elif align == "right":
            c.drawRightString(0, 0, value)
        else:
            c.drawString(0, 0, value)
    else:
        obj = c.beginText()
        obj.setFont(font, size)
        obj.setCharSpace(tracking)
        obj.setTextOrigin(0, 0)
        obj.textLine(value)
        c.drawText(obj)
    c.restoreState()


def rotate_text(c, x, y, value, angle, **kwargs):
    c.saveState()
    c.translate(mm(x), mm(y))
    c.rotate(angle)
    c.scale(1, -1)
    set_fill(c, kwargs.get("color", INK))
    c.setFont(kwargs.get("font", "Manrope"), kwargs.get("size", 8))
    c.drawString(0, 0, value)
    c.restoreState()


def draw_art(c):
    # Broad bleed field, then face-specific overprints.
    rect(c, X0 - 3, TOP_Y - 3, X_END - X0 + 6, (BOTTOM_Y + DEPTH) - TOP_Y + 6, BLACK)

    # Glue flap.
    polygon(c, [(X_GLUE, BODY_Y + 4), (X_BACK, BODY_Y), (X_BACK, BOTTOM_Y), (X_GLUE, BOTTOM_Y - 4)], BLACK)

    # Back panel and its closure flaps.
    rect(c, X_BACK - 3, BODY_Y - 3, FACE + 6, BODY_H + 6, CREAM)
    polygon(c, [(X_BACK, BODY_Y), (X_BACK + 3, TOP_Y), (X_SIDE_1 - 3, TOP_Y), (X_SIDE_1, BODY_Y)], CREAM)
    polygon(c, [(X_BACK, BOTTOM_Y), (X_BACK + 3, BOTTOM_Y + 20), (X_SIDE_1 - 3, BOTTOM_Y + 20), (X_SIDE_1, BOTTOM_Y)], CREAM)

    # Left spine.
    rect(c, X_SIDE_1, BODY_Y - 3, DEPTH, BODY_H + 6, PINK)
    polygon(c, [(X_SIDE_1, BODY_Y), (X_SIDE_1 + 2, TOP_Y + 5), (X_FRONT - 2, TOP_Y + 5), (X_FRONT, BODY_Y)], PINK)
    polygon(c, [(X_SIDE_1, BOTTOM_Y), (X_SIDE_1 + 2, BOTTOM_Y + 24), (X_FRONT - 2, BOTTOM_Y + 24), (X_FRONT, BOTTOM_Y)], PINK)

    # Front cassette face and flaps.
    rect(c, X_FRONT, BODY_Y - 3, FACE, BODY_H + 6, BLACK)
    polygon(c, [(X_FRONT, BODY_Y), (X_FRONT + 3, BODY_Y - 20), (X_SIDE_2 - 3, BODY_Y - 20), (X_SIDE_2, BODY_Y)], BLACK)
    polygon(c, [(X_FRONT, BOTTOM_Y), (X_FRONT + 3, BOTTOM_Y + DEPTH), (X_SIDE_2 - 3, BOTTOM_Y + DEPTH), (X_SIDE_2, BOTTOM_Y)], BLACK)

    # Right spine.
    rect(c, X_SIDE_2, BODY_Y - 3, DEPTH + 3, BODY_H + 6, GREEN)
    polygon(c, [(X_SIDE_2, BODY_Y), (X_SIDE_2 + 2, TOP_Y + 5), (X_END - 2, TOP_Y + 5), (X_END, BODY_Y)], GREEN)
    polygon(c, [(X_SIDE_2, BOTTOM_Y), (X_SIDE_2 + 2, BOTTOM_Y + 24), (X_END - 2, BOTTOM_Y + 24), (X_END, BOTTOM_Y)], GREEN)

    # BACK / SIDE B copy.
    text(c, X_BACK + 9, BODY_Y + 12, "SIDE B / КОФЕ + МУЗЫКА", "Manrope-ExtraBold", 5.5, INK, tracking=0.5)
    text(c, X_BACK + 9, BODY_Y + 28, "ТРИ ДРИПА.", "Unbounded-Black", 16, INK)
    text(c, X_BACK + 9, BODY_Y + 40, "ОДИН ДЕНЬ.", "Unbounded-Black", 16, INK)

    mood_y = BODY_Y + 54
    moods = [(GREEN, "01", "ТИХОЕ УТРО"), (ORANGE, "02", "СОЛНЦЕ ВНУТРИ"), (PINK, "03", "ЗАРЯД")]
    for i, (col, num, label) in enumerate(moods):
        yy = mood_y + i * 9
        circle(c, X_BACK + 11.5, yy - 1.6, 2.0, col)
        text(c, X_BACK + 17, yy, num, "Manrope-ExtraBold", 5.2, INK)
        text(c, X_BACK + 26, yy, label, "Unbounded-Bold", 5.1, INK)

    # Honest placeholder for the final live URL.
    qr_x = X_SIDE_1 - 35
    qr_y = BODY_Y + 49
    rect(c, qr_x, qr_y, 25, 25, BLACK, radius=1.5)
    for dx, dy in [(3, 3), (16, 3), (3, 16)]:
        rect(c, qr_x + dx, qr_y + dy, 6, 6, CREAM)
        rect(c, qr_x + dx + 1.5, qr_y + dy + 1.5, 3, 3, BLACK)
    text(c, qr_x + 12.5, qr_y + 14.5, "QR", "Unbounded-Bold", 5.2, CREAM, align="center")
    text(c, qr_x + 12.5, qr_y + 30.5, "ССЫЛКА НА ПЛЕЕР", "Manrope-ExtraBold", 4.2, INK, align="center")

    text(c, X_BACK + 9, BODY_Y + 88, "ОТКРОЙ · ПОСТАВЬ · 200 МЛ · НАЖМИ PLAY", "Manrope-ExtraBold", 5.2, INK)
    text(c, X_BACK + 9, BODY_Y + 97, "СОСТАВ / МАССА / ДАТА / ИЗГОТОВИТЕЛЬ — ДОБАВИТЬ ПЕРЕД ТИРАЖОМ", "Manrope", 3.7, MUTED)

    # FRONT / SIDE A cassette label.
    label_x = X_FRONT + 10
    label_y = BODY_Y + 9
    label_w = FACE - 20
    label_h = BODY_H - 18
    rect(c, label_x, label_y, label_w, label_h, CREAM, radius=4)
    polygon(c, [(label_x + 73, label_y), (label_x + label_w, label_y), (label_x + label_w, label_y + 27), (label_x + 86, label_y + 27)], GREEN)
    polygon(c, [(label_x + 86, label_y + 27), (label_x + label_w, label_y + 27), (label_x + label_w, label_y + 45), (label_x + 94, label_y + 45)], ORANGE)
    polygon(c, [(label_x + 94, label_y + 45), (label_x + label_w, label_y + 45), (label_x + label_w, label_y + label_h), (label_x + 104, label_y + label_h)], PINK)

    text(c, label_x + 6, label_y + 11, "<<<  KAVABANGA", "Unbounded-Bold", 6.0, INK)
    text(c, label_x + label_w - 6, label_y + 11, "SIDE A", "Manrope-ExtraBold", 5.0, INK, align="right")
    text(c, label_x + 6, label_y + 29, "DRIP", "Unbounded-Black", 18, INK)
    text(c, label_x + 6, label_y + 43, "TAPE", "Unbounded-Black", 18, INK)
    text(c, label_x + 66, label_y + 43, "03", "Unbounded-Black", 22, INK)

    # Cassette window and reels.
    rect(c, label_x + 8, label_y + 51, label_w - 16, 23, BLACK, radius=11.5)
    for cx in (label_x + 31, label_x + label_w - 31):
        circle(c, cx, label_y + 62.5, 8.1, CREAM)
        circle(c, cx, label_y + 62.5, 4.6, BLACK)
        circle(c, cx, label_y + 62.5, 1.7, CREAM)
    rect(c, label_x + 47, label_y + 60.9, label_w - 94, 3.2, ORANGE, radius=1.5)

    text(c, label_x + 7, label_y + 82, "3 ПОРЦИИ · КОФЕ + МУЗЫКА", "Manrope-ExtraBold", 5.1, INK)
    text(c, label_x + label_w - 7, label_y + 82, "PLAY / BREW / REPEAT", "Manrope-SemiBold", 4.2, INK, align="right")

    # Spines, closures and tiny production-friendly orientation marks.
    rotate_text(c, X_SIDE_1 + 18, BOTTOM_Y - 9, "KAVABANGA / DRIP TAPE 03", 90, font="Unbounded-Bold", size=5.0, color=BLACK)
    rotate_text(c, X_SIDE_2 + 18, BOTTOM_Y - 9, "3 ДРИПА / ВКЛЮЧИ НАСТРОЕНИЕ", 90, font="Unbounded-Bold", size=4.6, color=BLACK)
    text(c, X_BACK + 8, TOP_Y + 17, "OPEN / PLAY", "Unbounded-Bold", 7.0, INK)
    text(c, X_FRONT + FACE / 2, BOTTOM_Y + 17, "ДРИП С КАВАБАНГОЙ", "Unbounded-Bold", 6.0, CREAM, align="center")
    text(c, X_SIDE_2 + DEPTH / 2, TOP_Y + 17, "03", "Unbounded-Black", 8.0, BLACK, align="center")


def draw_dieline(c):
    # Cutting paths: magenta, continuous.
    cut_segments = [
        # glue flap outer
        [(X_GLUE, BODY_Y + 4), (X_BACK, BODY_Y)],
        [(X_GLUE, BODY_Y + 4), (X_GLUE, BOTTOM_Y - 4)],
        [(X_GLUE, BOTTOM_Y - 4), (X_BACK, BOTTOM_Y)],
        # top flaps
        [(X_BACK, BODY_Y), (X_BACK + 3, TOP_Y), (X_SIDE_1 - 3, TOP_Y), (X_SIDE_1, BODY_Y)],
        [(X_SIDE_1, BODY_Y), (X_SIDE_1 + 2, TOP_Y + 5), (X_FRONT - 2, TOP_Y + 5), (X_FRONT, BODY_Y)],
        [(X_FRONT, BODY_Y), (X_FRONT + 3, BODY_Y - 20), (X_SIDE_2 - 3, BODY_Y - 20), (X_SIDE_2, BODY_Y)],
        [(X_SIDE_2, BODY_Y), (X_SIDE_2 + 2, TOP_Y + 5), (X_END - 2, TOP_Y + 5), (X_END, BODY_Y)],
        # body right edge
        [(X_END, BODY_Y), (X_END, BOTTOM_Y)],
        # bottom flaps
        [(X_BACK, BOTTOM_Y), (X_BACK + 3, BOTTOM_Y + 20), (X_SIDE_1 - 3, BOTTOM_Y + 20), (X_SIDE_1, BOTTOM_Y)],
        [(X_SIDE_1, BOTTOM_Y), (X_SIDE_1 + 2, BOTTOM_Y + 24), (X_FRONT - 2, BOTTOM_Y + 24), (X_FRONT, BOTTOM_Y)],
        [(X_FRONT, BOTTOM_Y), (X_FRONT + 3, BOTTOM_Y + DEPTH), (X_SIDE_2 - 3, BOTTOM_Y + DEPTH), (X_SIDE_2, BOTTOM_Y)],
        [(X_SIDE_2, BOTTOM_Y), (X_SIDE_2 + 2, BOTTOM_Y + 24), (X_END - 2, BOTTOM_Y + 24), (X_END, BOTTOM_Y)],
    ]
    set_stroke(c, CUT)
    c.setLineWidth(mm(0.25))
    for pts in cut_segments:
        p = c.beginPath()
        p.moveTo(mm(pts[0][0]), mm(pts[0][1]))
        for x, y in pts[1:]:
            p.lineTo(mm(x), mm(y))
        c.drawPath(p, fill=0, stroke=1)

    # Crease paths: cyan, dashed.
    for x in (X_BACK, X_SIDE_1, X_FRONT, X_SIDE_2):
        line(c, x, BODY_Y, x, BOTTOM_Y, CREASE, 0.25, [2.2, 1.6])
    for xa, xb in [(X_BACK, X_SIDE_1), (X_SIDE_1, X_FRONT), (X_FRONT, X_SIDE_2), (X_SIDE_2, X_END)]:
        line(c, xa, BODY_Y, xb, BODY_Y, CREASE, 0.25, [2.2, 1.6])
        line(c, xa, BOTTOM_Y, xb, BOTTOM_Y, CREASE, 0.25, [2.2, 1.6])


def draw_sheet_notes(c):
    text(c, 45, 40, "KVBNG / DRIP TAPE 03", "Unbounded-Black", 12, BLACK)
    text(c, 45, 50, "РАЗВЕРТКА 1:1 · A3 LANDSCAPE · 130 × 105 × 28 ММ", "Manrope-ExtraBold", 6.2, BLACK, tracking=0.3)
    text(c, 375, 42, "ПРОТОТИП V1", "Manrope-ExtraBold", 5.5, MUTED, align="right")
    text(c, 45, 255, "РЕЗ", "Manrope-ExtraBold", 5.2, CUT)
    line(c, 58, 253.5, 74, 253.5, CUT, 0.5)
    text(c, 86, 255, "БИГ", "Manrope-ExtraBold", 5.2, CREASE)
    line(c, 100, 253.5, 116, 253.5, CREASE, 0.5, [2.2, 1.6])
    text(c, 130, 255, "ВЫЛЕТЫ 3 ММ · БЕЛЫЙ МЕЛОВАННЫЙ КАРТОН 300–350 Г/М² · ЦИФРОВАЯ ПЕЧАТЬ 4+0 · ПЛОТТЕРНАЯ РЕЗКА", "Manrope-SemiBold", 4.9, MUTED)
    text(c, 45, 267, "ПЕРЕД ТИРАЖОМ: ВЛОЖИТЬ РЕАЛЬНЫЕ САШЕ, ПОДТВЕРДИТЬ ГЛУБИНУ И ЗАМЕНИТЬ QR + ЮРИДИЧЕСКИЙ БЛОК.", "Manrope-ExtraBold", 5.2, BLACK)


def build_pdf():
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    register_fonts()
    c = canvas.Canvas(str(OUT_PDF), pagesize=landscape(A3), pageCompression=1)
    c.setTitle("KVBNG Drip Tape 03 — dieline A3")
    c.setAuthor("KAVABANGA")
    c.setSubject("Prototype folding carton dieline, 130 x 105 x 28 mm")
    c.translate(0, mm(PAGE_H_MM))
    c.scale(1, -1)
    rect(c, 0, 0, PAGE_W_MM, PAGE_H_MM, "#ffffff")
    draw_sheet_notes(c)
    draw_art(c)
    draw_dieline(c)
    c.showPage()
    c.save()


def svg_text(x, y, value, family="Manrope", size=8, weight=400, fill=INK, anchor="start", rotate=None, spacing=None):
    attrs = [f'x="{x}"', f'y="{y}"', f'font-family="{family}"', f'font-size="{size}px"', f'font-weight="{weight}"', f'fill="{fill}"', f'text-anchor="{anchor}"']
    if rotate is not None:
        attrs.append(f'transform="rotate({rotate} {x} {y})"')
    if spacing is not None:
        attrs.append(f'letter-spacing="{spacing}px"')
    return f'<text {" ".join(attrs)}>{escape(value)}</text>'


def build_svg():
    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    # The SVG is an editable companion. Text stays live; the PDF is the font-embedded handoff.
    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W_MM}mm" height="{PAGE_H_MM}mm" viewBox="0 0 {PAGE_W_MM} {PAGE_H_MM}">',
        '<title>KVBNG Drip Tape 03 — dieline A3</title>',
        '<rect width="420" height="297" fill="#fff"/>',
        '<g id="ARTWORK">',
        f'<rect x="{X0-3}" y="{TOP_Y-3}" width="{X_END-X0+6}" height="{BOTTOM_Y+DEPTH-TOP_Y+6}" fill="{BLACK}"/>',
        f'<path d="M {X_GLUE} {BODY_Y+4} L {X_BACK} {BODY_Y} L {X_BACK} {BOTTOM_Y} L {X_GLUE} {BOTTOM_Y-4} Z" fill="{BLACK}"/>',
        f'<rect x="{X_BACK-3}" y="{BODY_Y-3}" width="{FACE+6}" height="{BODY_H+6}" fill="{CREAM}"/>',
        f'<path d="M {X_BACK} {BODY_Y} L {X_BACK+3} {TOP_Y} L {X_SIDE_1-3} {TOP_Y} L {X_SIDE_1} {BODY_Y} Z" fill="{CREAM}"/>',
        f'<path d="M {X_BACK} {BOTTOM_Y} L {X_BACK+3} {BOTTOM_Y+20} L {X_SIDE_1-3} {BOTTOM_Y+20} L {X_SIDE_1} {BOTTOM_Y} Z" fill="{CREAM}"/>',
        f'<rect x="{X_SIDE_1}" y="{BODY_Y-3}" width="{DEPTH}" height="{BODY_H+6}" fill="{PINK}"/>',
        f'<path d="M {X_SIDE_1} {BODY_Y} L {X_SIDE_1+2} {TOP_Y+5} L {X_FRONT-2} {TOP_Y+5} L {X_FRONT} {BODY_Y} Z" fill="{PINK}"/>',
        f'<path d="M {X_SIDE_1} {BOTTOM_Y} L {X_SIDE_1+2} {BOTTOM_Y+24} L {X_FRONT-2} {BOTTOM_Y+24} L {X_FRONT} {BOTTOM_Y} Z" fill="{PINK}"/>',
        f'<rect x="{X_FRONT}" y="{BODY_Y-3}" width="{FACE}" height="{BODY_H+6}" fill="{BLACK}"/>',
        f'<path d="M {X_FRONT} {BODY_Y} L {X_FRONT+3} {BODY_Y-20} L {X_SIDE_2-3} {BODY_Y-20} L {X_SIDE_2} {BODY_Y} Z" fill="{BLACK}"/>',
        f'<path d="M {X_FRONT} {BOTTOM_Y} L {X_FRONT+3} {BOTTOM_Y+DEPTH} L {X_SIDE_2-3} {BOTTOM_Y+DEPTH} L {X_SIDE_2} {BOTTOM_Y} Z" fill="{BLACK}"/>',
        f'<rect x="{X_SIDE_2}" y="{BODY_Y-3}" width="{DEPTH+3}" height="{BODY_H+6}" fill="{GREEN}"/>',
        f'<path d="M {X_SIDE_2} {BODY_Y} L {X_SIDE_2+2} {TOP_Y+5} L {X_END-2} {TOP_Y+5} L {X_END} {BODY_Y} Z" fill="{GREEN}"/>',
        f'<path d="M {X_SIDE_2} {BOTTOM_Y} L {X_SIDE_2+2} {BOTTOM_Y+24} L {X_END-2} {BOTTOM_Y+24} L {X_END} {BOTTOM_Y} Z" fill="{GREEN}"/>',
        svg_text(68, 108, "SIDE B / КОФЕ + МУЗЫКА", "Manrope", 5.5, 800, INK, spacing=.5),
        svg_text(68, 124, "ТРИ ДРИПА.", "Unbounded", 16, 900, INK),
        svg_text(68, 136, "ОДИН ДЕНЬ.", "Unbounded", 16, 900, INK),
    ]
    moods = [(GREEN, "01", "ТИХОЕ УТРО"), (ORANGE, "02", "СОЛНЦЕ ВНУТРИ"), (PINK, "03", "ЗАРЯД")]
    for i, (col, num, label) in enumerate(moods):
        yy = 150 + i * 9
        s += [f'<circle cx="70.5" cy="{yy-1.6}" r="2" fill="{col}"/>', svg_text(76, yy, num, "Manrope", 5.2, 800), svg_text(85, yy, label, "Unbounded", 5.1, 700)]
    qr_x, qr_y = X_SIDE_1 - 35, BODY_Y + 49
    s += [f'<rect x="{qr_x}" y="{qr_y}" width="25" height="25" rx="1.5" fill="{BLACK}"/>']
    for dx, dy in [(3, 3), (16, 3), (3, 16)]:
        s += [f'<rect x="{qr_x+dx}" y="{qr_y+dy}" width="6" height="6" fill="{CREAM}"/>', f'<rect x="{qr_x+dx+1.5}" y="{qr_y+dy+1.5}" width="3" height="3" fill="{BLACK}"/>']
    s += [svg_text(qr_x+12.5, qr_y+15, "QR", "Unbounded", 5.2, 700, CREAM, "middle"), svg_text(qr_x+12.5, qr_y+31, "ССЫЛКА НА ПЛЕЕР", "Manrope", 4.2, 800, INK, "middle"), svg_text(68, 184, "ОТКРОЙ · ПОСТАВЬ · 200 МЛ · НАЖМИ PLAY", "Manrope", 5.2, 800), svg_text(68, 193, "СОСТАВ / МАССА / ДАТА / ИЗГОТОВИТЕЛЬ — ДОБАВИТЬ ПЕРЕД ТИРАЖОМ", "Manrope", 3.7, 400, MUTED)]

    lx, ly, lw, lh = X_FRONT+10, BODY_Y+9, FACE-20, BODY_H-18
    s += [
        f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="4" fill="{CREAM}"/>',
        f'<path d="M {lx+73} {ly} L {lx+lw} {ly} L {lx+lw} {ly+27} L {lx+86} {ly+27} Z" fill="{GREEN}"/>',
        f'<path d="M {lx+86} {ly+27} L {lx+lw} {ly+27} L {lx+lw} {ly+45} L {lx+94} {ly+45} Z" fill="{ORANGE}"/>',
        f'<path d="M {lx+94} {ly+45} L {lx+lw} {ly+45} L {lx+lw} {ly+lh} L {lx+104} {ly+lh} Z" fill="{PINK}"/>',
        svg_text(lx+6, ly+11, "<<<  KAVABANGA", "Unbounded", 6, 700),
        svg_text(lx+lw-6, ly+11, "SIDE A", "Manrope", 5, 800, INK, "end"),
        svg_text(lx+6, ly+29, "DRIP", "Unbounded", 18, 900),
        svg_text(lx+6, ly+43, "TAPE", "Unbounded", 18, 900),
        svg_text(lx+66, ly+43, "03", "Unbounded", 22, 900),
        f'<rect x="{lx+8}" y="{ly+51}" width="{lw-16}" height="23" rx="11.5" fill="{BLACK}"/>',
    ]
    for cx in (lx+31, lx+lw-31):
        s += [f'<circle cx="{cx}" cy="{ly+62.5}" r="8.1" fill="{CREAM}"/>', f'<circle cx="{cx}" cy="{ly+62.5}" r="4.6" fill="{BLACK}"/>', f'<circle cx="{cx}" cy="{ly+62.5}" r="1.7" fill="{CREAM}"/>']
    s += [f'<rect x="{lx+47}" y="{ly+60.9}" width="{lw-94}" height="3.2" rx="1.5" fill="{ORANGE}"/>', svg_text(lx+7, ly+82, "3 ПОРЦИИ · КОФЕ + МУЗЫКА", "Manrope", 5.1, 800), svg_text(lx+lw-7, ly+82, "PLAY / BREW / REPEAT", "Manrope", 4.2, 600, INK, "end"), svg_text(X_SIDE_1+18, BOTTOM_Y-9, "KAVABANGA / DRIP TAPE 03", "Unbounded", 5, 700, INK, "start", 90), svg_text(X_SIDE_2+18, BOTTOM_Y-9, "3 ДРИПА / ВКЛЮЧИ НАСТРОЕНИЕ", "Unbounded", 4.6, 700, INK, "start", 90), svg_text(X_BACK+8, TOP_Y+17, "OPEN / PLAY", "Unbounded", 7, 700), svg_text(X_FRONT+FACE/2, BOTTOM_Y+17, "ДРИП С КАВАБАНГОЙ", "Unbounded", 6, 700, CREAM, "middle"), svg_text(X_SIDE_2+DEPTH/2, TOP_Y+17, "03", "Unbounded", 8, 900, INK, "middle"), '</g>']

    # Dieline groups are named so a print shop can isolate or restyle them.
    cut_paths = [
        f'M {X_GLUE} {BODY_Y+4} L {X_BACK} {BODY_Y}', f'M {X_GLUE} {BODY_Y+4} L {X_GLUE} {BOTTOM_Y-4}', f'M {X_GLUE} {BOTTOM_Y-4} L {X_BACK} {BOTTOM_Y}',
        f'M {X_BACK} {BODY_Y} L {X_BACK+3} {TOP_Y} L {X_SIDE_1-3} {TOP_Y} L {X_SIDE_1} {BODY_Y}',
        f'M {X_SIDE_1} {BODY_Y} L {X_SIDE_1+2} {TOP_Y+5} L {X_FRONT-2} {TOP_Y+5} L {X_FRONT} {BODY_Y}',
        f'M {X_FRONT} {BODY_Y} L {X_FRONT+3} {BODY_Y-20} L {X_SIDE_2-3} {BODY_Y-20} L {X_SIDE_2} {BODY_Y}',
        f'M {X_SIDE_2} {BODY_Y} L {X_SIDE_2+2} {TOP_Y+5} L {X_END-2} {TOP_Y+5} L {X_END} {BODY_Y}',
        f'M {X_END} {BODY_Y} L {X_END} {BOTTOM_Y}',
        f'M {X_BACK} {BOTTOM_Y} L {X_BACK+3} {BOTTOM_Y+20} L {X_SIDE_1-3} {BOTTOM_Y+20} L {X_SIDE_1} {BOTTOM_Y}',
        f'M {X_SIDE_1} {BOTTOM_Y} L {X_SIDE_1+2} {BOTTOM_Y+24} L {X_FRONT-2} {BOTTOM_Y+24} L {X_FRONT} {BOTTOM_Y}',
        f'M {X_FRONT} {BOTTOM_Y} L {X_FRONT+3} {BOTTOM_Y+DEPTH} L {X_SIDE_2-3} {BOTTOM_Y+DEPTH} L {X_SIDE_2} {BOTTOM_Y}',
        f'M {X_SIDE_2} {BOTTOM_Y} L {X_SIDE_2+2} {BOTTOM_Y+24} L {X_END-2} {BOTTOM_Y+24} L {X_END} {BOTTOM_Y}',
    ]
    s += [f'<g id="CUT" fill="none" stroke="{CUT}" stroke-width="0.25">'] + [f'<path d="{d}"/>' for d in cut_paths] + ['</g>']
    crease_lines = []
    for x in (X_BACK, X_SIDE_1, X_FRONT, X_SIDE_2):
        crease_lines.append(f'<line x1="{x}" y1="{BODY_Y}" x2="{x}" y2="{BOTTOM_Y}"/>')
    for xa, xb in [(X_BACK, X_SIDE_1), (X_SIDE_1, X_FRONT), (X_FRONT, X_SIDE_2), (X_SIDE_2, X_END)]:
        crease_lines += [f'<line x1="{xa}" y1="{BODY_Y}" x2="{xb}" y2="{BODY_Y}"/>', f'<line x1="{xa}" y1="{BOTTOM_Y}" x2="{xb}" y2="{BOTTOM_Y}"/>']
    s += [f'<g id="CREASE" fill="none" stroke="{CREASE}" stroke-width="0.25" stroke-dasharray="2.2 1.6">'] + crease_lines + ['</g>']
    s += ['<g id="NOTES">', svg_text(45, 40, "KVBNG / DRIP TAPE 03", "Unbounded", 12, 900), svg_text(45, 50, "РАЗВЕРТКА 1:1 · A3 LANDSCAPE · 130 × 105 × 28 ММ", "Manrope", 6.2, 800, BLACK, spacing=.3), svg_text(375, 42, "ПРОТОТИП V1", "Manrope", 5.5, 800, MUTED, "end"), svg_text(45, 255, "РЕЗ", "Manrope", 5.2, 800, CUT), f'<line x1="58" y1="253.5" x2="74" y2="253.5" stroke="{CUT}" stroke-width=".5"/>', svg_text(86, 255, "БИГ", "Manrope", 5.2, 800, CREASE), f'<line x1="100" y1="253.5" x2="116" y2="253.5" stroke="{CREASE}" stroke-width=".5" stroke-dasharray="2.2 1.6"/>', svg_text(130, 255, "ВЫЛЕТЫ 3 ММ · БЕЛЫЙ МЕЛОВАННЫЙ КАРТОН 300–350 Г/М² · ЦИФРОВАЯ ПЕЧАТЬ 4+0 · ПЛОТТЕРНАЯ РЕЗКА", "Manrope", 4.9, 600, MUTED), svg_text(45, 267, "ПЕРЕД ТИРАЖОМ: ВЛОЖИТЬ РЕАЛЬНЫЕ САШЕ, ПОДТВЕРДИТЬ ГЛУБИНУ И ЗАМЕНИТЬ QR + ЮРИДИЧЕСКИЙ БЛОК.", "Manrope", 5.2, 800), '</g>', '</svg>']
    OUT_SVG.write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    build_pdf()
    build_svg()
    print(OUT_PDF.resolve())
    print(OUT_SVG.resolve())

"""Printable PDF: one month per A4 page."""
import calendar
from datetime import date
from fpdf import FPDF

from plan import DAYS, by_date, in_break, months_in_plan, race_day

FILLS = {"run": (227, 237, 248), "long": (247, 225, 221), "str": (238, 230, 246),
         "rest": (255, 255, 255), "race": (184, 58, 42), "brk": (228, 228, 228)}


def _clean(t: str) -> str:
    # Core PDF fonts are Latin-1 only
    return t.replace("–", "-").replace("·", "-")


def build_pdf(start: date, done: set, breaks=()) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    W, H, M, gap = 210, 297, 10, 1.5
    col_w = (W - 2 * M - 6 * gap) / 7
    lookup = by_date(start, breaks)
    race = race_day(start, breaks)

    for y, m in months_in_plan(start, breaks):
        pdf.add_page()
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(90)
        pdf.set_xy(M, M)
        pdf.cell(0, 4, f"Half marathon plan - Race day {race:%a %d %b %Y}")
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(20)
        pdf.set_xy(M, M + 5)
        pdf.cell(0, 10, f"{calendar.month_name[m]} {y}")

        top = M + 22
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(90)
        for i, d in enumerate(DAYS):
            pdf.set_xy(M + i * (col_w + gap), top - 6)
            pdf.cell(col_w, 5, d, align="C")

        lead = date(y, m, 1).weekday()
        dim = calendar.monthrange(y, m)[1]
        rows = -(-(lead + dim) // 7)
        row_h = (H - M - top - (rows - 1) * gap) / rows

        for dnum in range(1, dim + 1):
            pos = lead + dnum - 1
            x = M + (pos % 7) * (col_w + gap)
            yy = top + (pos // 7) * (row_h + gap)
            dd = date(y, m, dnum)
            s = lookup.get(dd)
            is_race = bool(s and s.kind == "race")
            on_break = not s and start <= dd <= race and in_break(dd, breaks)

            pdf.set_draw_color(150)
            pdf.set_line_width(0.3)
            pdf.set_fill_color(*(FILLS[s.kind] if s else FILLS["brk"] if on_break else (255, 255, 255)))
            pdf.rect(x, yy, col_w, row_h, style="DF", round_corners=True, corner_radius=1.5)

            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(255 if is_race else (60 if s else 190))
            pdf.set_xy(x + 1.5, yy + 1.5)
            pdf.cell(8, 5, str(dnum))
            if on_break:
                pdf.set_font("Helvetica", "I", 10.5)
                pdf.set_text_color(110)
                pdf.set_xy(x + 1.5, yy + 8)
                pdf.cell(col_w - 3, 4.6, "Break")
            if not s:
                continue
            if s.day == 0:
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(255 if is_race else 110)
                pdf.set_xy(x + 8, yy + 1.8)
                pdf.cell(8, 5, f"W{s.week}")

            bx, by = x + col_w - 6.5, yy + 1.8
            pdf.set_draw_color(*(255, 255, 255) if is_race else (80, 80, 80))
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(bx, by, 4.5, 4.5, style="DF")
            if s.id in done:
                pdf.set_draw_color(46, 125, 79)
                pdf.set_line_width(0.7)
                pdf.line(bx + 0.9, by + 2.4, bx + 1.9, by + 3.6)
                pdf.line(bx + 1.9, by + 3.6, bx + 3.8, by + 0.9)

            pdf.set_font("Helvetica", "B" if is_race else "", 10.5)
            pdf.set_text_color(255 if is_race else (100 if s.kind == "rest" else 20))
            pdf.set_xy(x + 1.5, yy + 8)
            pdf.multi_cell(col_w - 3, 4.6, _clean(s.text))

    return bytes(pdf.output())

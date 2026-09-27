"""Beginner to Half Marathon: 29-week training plan tracker (Streamlit)."""
import calendar
import json
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

from pdf_export import build_pdf
from plan import (DAYS, PHASES, SESSIONS, WEEKS, by_date, in_break,
                  months_in_plan, race_day, schedule)

st.set_page_config(page_title="0 to 21.1 km", page_icon="🏃", layout="wide")

DATA_FILE = Path(__file__).parent / "progress.json"
VALID_IDS = {s.id for s in SESSIONS}
FMT = "%a %d %b %Y"


# ---------- storage ----------
def parse_state(raw: dict) -> dict:
    start = date.fromisoformat(raw["start"]) if raw.get("start") else None
    breaks = sorted((date.fromisoformat(a), date.fromisoformat(b)) for a, b in raw.get("breaks", []))
    return {"start": start, "breaks": breaks, "done": set(raw.get("done", [])) & VALID_IDS}


def dump_state() -> str:
    s = st.session_state
    return json.dumps({"start": s.start.isoformat() if s.start else None,
                       "breaks": [[a.isoformat(), b.isoformat()] for a, b in s.breaks],
                       "done": sorted(s.done)})


def save():
    try:
        DATA_FILE.write_text(dump_state())
    except OSError:
        st.toast("Couldn't save progress to disk. Use 'Download backup' to keep it.")


if "done" not in st.session_state:
    try:
        data = parse_state(json.loads(DATA_FILE.read_text()))
    except Exception:
        data = {"start": None, "breaks": [], "done": set()}
    st.session_state.update(data)


def clear_widget_keys():
    for k in [k for k in st.session_state if k.startswith(("cal_", "lst_"))]:
        del st.session_state[k]


def toggle(sid: str, key: str):
    val = st.session_state[key]
    (st.session_state.done.add if val else st.session_state.done.discard)(sid)
    for prefix in ("cal_", "lst_"):
        st.session_state[prefix + sid] = val
    save()


def checkbox(sid: str, prefix: str, label: str, **kw):
    key = prefix + sid
    if key not in st.session_state:
        st.session_state[key] = sid in st.session_state.done
    st.checkbox(label, key=key, on_change=toggle, args=(sid, key), **kw)


# ---------- styles ----------
st.markdown("""
<style>
.hero {background:#B83A2A;color:#fff;padding:22px 22px 18px;border-radius:10px;margin-bottom:12px}
.hero h1 {color:#fff;font-size:clamp(2rem,8vw,3rem);margin:0;padding:0;line-height:1}
.hero p {margin:6px 0 0;opacity:.92}
[class*="st-key-tile_"] {border-radius:7px;padding:5px 6px 2px;min-height:118px;border:1px solid rgba(128,128,128,.35);gap:2px}
[class*="st-key-tile_run_"] {background:rgba(47,109,181,.14)}
[class*="st-key-tile_long_"] {background:rgba(184,58,42,.16)}
[class*="st-key-tile_str_"] {background:rgba(138,91,184,.15)}
[class*="st-key-tile_brk_"] {background:repeating-linear-gradient(45deg,rgba(128,128,128,.10) 0 6px,rgba(128,128,128,.20) 6px 12px)}
[class*="st-key-tile_race_"] {background:#B83A2A}
[class*="st-key-tile_race_"] * {color:#fff !important}
[class*="st-key-tile_out_"] {opacity:.35}
[class*="st-key-tile_blank"] {border:none;min-height:0}
[class*="st-key-tile_"] .dnum {font-weight:700;font-size:.85rem;opacity:.75;margin:0 !important;line-height:1.3}
[class*="st-key-tile_"] .brk {font-style:italic;opacity:.7;font-size:.8rem;margin:0 !important}
[class*="st-key-tile_"] [data-testid="stElementContainer"] {margin:0 !important}
[class*="st-key-tile_"] .stMarkdown {margin-bottom:2px !important;min-height:1.1rem}
[class*="st-key-tile_"] [data-testid="stMarkdownContainer"] {margin:0 !important}
[class*="st-key-tile_"] [data-testid="stCheckbox"] label p {font-size:.8rem;line-height:1.25}
.today-tile {outline:2px solid currentColor;border-radius:4px;padding:0 3px}
.st-key-calendar [data-testid="stHorizontalBlock"] {flex-wrap:nowrap !important;gap:4px !important}
.st-key-calendar [data-testid="stColumn"] {min-width:0 !important;flex:1 1 0 !important;width:auto !important}
.dow {text-align:center;font-weight:600;opacity:.65;font-size:.85rem}
@media (max-width:640px){
  [class*="st-key-tile_"] {min-height:130px;padding:3px}
  [class*="st-key-tile_"] [data-testid="stCheckbox"] label p, [class*="st-key-tile_"] .brk {font-size:.62rem}
  [class*="st-key-tile_"] [data-testid="stCheckbox"] label {gap:2px;flex-direction:column;align-items:flex-start}
  .dow {font-size:.7rem}
}
</style>
""", unsafe_allow_html=True)


# ---------- header ----------
st.markdown("""<div class="hero"><h1>0 to 21.1 km</h1>
<p>A 29-week plan from your first run to a half marathon. Tick each day when you finish it.</p></div>""",
            unsafe_allow_html=True)

today = date.today()

# ---------- start date & breaks ----------
with st.expander("Start date and breaks", expanded=st.session_state.start is None):
    picked = st.date_input("When do you want to start?", value=st.session_state.start,
                           format="DD/MM/YYYY", help="Week 1 begins on this day.")
    if picked != st.session_state.start:
        st.session_state.start = picked
        save()
        st.rerun()

    if st.session_state.start:
        start = st.session_state.start
        st.markdown(f"**Race day:** {race_day(start, st.session_state.breaks):{FMT}}")

        st.divider()
        st.markdown("**Take a break**")
        st.caption("Pausing moves every remaining session forward. When you come back, "
                   "you pick up exactly where you left off.")
        c1, c2 = st.columns(2)
        b_from = c1.date_input("Break starts", value=None, format="DD/MM/YYYY", key="b_from")
        b_to = c2.date_input("Resume on", value=None, format="DD/MM/YYYY", key="b_to")
        if st.button("Add break"):
            end = race_day(start, st.session_state.breaks)
            if not b_from or not b_to:
                st.error("Choose both a break start date and a resume date.")
            elif b_to <= b_from:
                st.error("The resume date must be after the break start date.")
            elif b_from < start:
                st.error(f"A break can't start before your plan starts ({start:{FMT}}).")
            elif b_from > end:
                st.error(f"That's after race day ({end:{FMT}}).")
            elif any(b_from < r and a < b_to for a, r in st.session_state.breaks):
                st.error("That overlaps a break you've already added. Remove it first or pick other dates.")
            else:
                st.session_state.breaks = sorted(st.session_state.breaks + [(b_from, b_to)])
                for k in ("b_from", "b_to"):
                    del st.session_state[k]
                save()
                st.rerun()

        if st.session_state.breaks:
            st.markdown("**Your breaks**")
            for idx, (a, b) in enumerate(st.session_state.breaks):
                c1, c2 = st.columns([4, 1])
                n = (b - a).days
                c1.write(f"{a:%d %b %Y} → resume {b:%d %b %Y} ({n} day{'s' if n != 1 else ''})")
                if c2.button("Remove", key=f"rm_{idx}"):
                    st.session_state.breaks.pop(idx)
                    save()
                    st.rerun()

start = st.session_state.start
breaks = st.session_state.breaks
done = st.session_state.done

# ---------- sidebar ----------
with st.sidebar:
    st.subheader("Print")
    if start:
        st.download_button("Download printable PDF", data=build_pdf(start, done, breaks),
                           file_name=f"half-marathon-calendar-{start}.pdf", mime="application/pdf",
                           use_container_width=True, help="One month per A4 page")
    else:
        st.caption("Choose a start date to create your printable calendar.")

    st.divider()
    st.subheader("Backup")
    st.download_button("Download backup", use_container_width=True, mime="application/json",
                       file_name="half-marathon-progress.json", data=dump_state())
    up = st.file_uploader("Restore from backup", type="json")
    if up is not None and st.button("Restore", use_container_width=True):
        try:
            st.session_state.update(parse_state(json.loads(up.read())))
            clear_widget_keys(); save(); st.rerun()
        except Exception:
            st.error("That file isn't a valid backup.")

    st.divider()
    if st.button("Clear all ticks", use_container_width=True):
        st.session_state.confirm_reset = True
    if st.session_state.get("confirm_reset"):
        st.warning("Clear every tick in the plan?")
        c1, c2 = st.columns(2)
        if c1.button("Yes, clear"):
            st.session_state.done = set(); st.session_state.confirm_reset = False
            clear_widget_keys(); save(); st.rerun()
        if c2.button("Cancel"):
            st.session_state.confirm_reset = False; st.rerun()

# ---------- progress & today ----------
pct = len(done) / len(SESSIONS)
st.progress(pct, text=f"{len(done)} of {len(SESSIONS)} days done ({pct:.1%})")

if not start:
    st.info("Choose your start date above to build your calendar. You can still browse the plan below.")
else:
    lookup = by_date(start, breaks)
    end = race_day(start, breaks)
    t = lookup.get(today)
    current_break = next(((a, b) for a, b in breaks if a <= today < b), None)
    if current_break:
        st.warning(f"**You're on a break.** Training resumes on {current_break[1]:{FMT}}.")
    elif t:
        st.info(f"**Today, week {t.week}:** {t.text}")
    elif today < start:
        n = (start - today).days
        st.info(f"Your plan starts on **{start:{FMT}}** ({n} day{'s' if n != 1 else ''} to go).")
    elif today > end:
        st.success("Plan complete. Well done!")

tabs = st.tabs(["Calendar", "Weekly list", "How to use"])

# ---------- calendar ----------
with tabs[0]:
    if not start:
        st.caption("Your calendar appears here once you choose a start date.")
    else:
        months = months_in_plan(start, breaks)
        labels = [f"{calendar.month_name[m]} {y}" for y, m in months]
        default_idx = next((i for i, ym in enumerate(months) if ym == (today.year, today.month)), 0)
        choice = st.selectbox("Month", labels, index=default_idx, label_visibility="collapsed")
        y, m = months[labels.index(choice)]

        st.caption("🟦 Easy / quality run   🟥 Long run   🟪 Strength   ⬜ Rest or walk   ▨ Break")
        with st.container(key="calendar"):
            cols = st.columns(7)
            for c, d in zip(cols, DAYS):
                c.markdown(f"<div class='dow'>{d}</div>", unsafe_allow_html=True)
            for week in calendar.Calendar(firstweekday=0).monthdatescalendar(y, m):
                cols = st.columns(7)
                for c, d in zip(cols, week):
                    with c:
                        if d.month != m:
                            st.container(key=f"tile_blank_{d}")
                            continue
                        s = lookup.get(d)
                        on_break = not s and start <= d <= end and in_break(d, breaks)
                        kind = s.kind if s else ("brk" if on_break else "out")
                        with st.container(key=f"tile_{kind}_{d:%Y%m%d}"):
                            num = f"<span class='today-tile'>{d.day}</span>" if d == today else str(d.day)
                            wk = (f" <span style='font-weight:400;font-size:.7rem'>W{s.week}</span>"
                                  if s and s.day == 0 else "")
                            st.markdown(f"<p class='dnum'>{num}{wk}</p>", unsafe_allow_html=True)
                            if s:
                                checkbox(s.id, "cal_", s.text)
                            elif on_break:
                                st.markdown("<p class='brk'>Break</p>", unsafe_allow_html=True)

# ---------- weekly list ----------
with tabs[1]:
    sched = schedule(start, breaks) if start else {}
    for ph, (title, desc) in PHASES.items():
        st.subheader(title)
        st.caption(desc)
        for w, (wph, focus, texts) in enumerate(WEEKS, start=1):
            if wph != ph:
                continue
            ids = [f"w{w}d{i}" for i in range(7)]
            n_done = sum(i in done for i in ids)
            mark = " ✅" if n_done == 7 else ""
            if start:
                first, last = sched[ids[0]], sched[ids[-1]]
                when = f" · {first:%d %b}" + (f" – {last:%d %b}" if last != first + timedelta(days=6) else "")
                current = first <= today <= last
            else:
                when, current = "", False
            with st.expander(f"Week {w}{when} · {focus} ({n_done}/7){mark}", expanded=current):
                for i, txt in enumerate(texts):
                    day = f"{sched[ids[i]]:%a %d %b}" if start else f"Day {i + 1}"
                    checkbox(ids[i], "lst_", f"**{day}** — {txt}")

# ---------- guide ----------
with tabs[2]:
    st.markdown("""
- **Easy pace** means you can talk in full sentences. Most runs should feel like this.
- Start every run with a 5-minute brisk walk, and finish with 5 minutes of walking and light stretching.
- **Strength** is 20–30 minutes: squats, lunges, glute bridges, calf raises, planks.
- **Tempo** is a comfortably hard pace you could hold for about an hour.
- **Strides** are 4–6 relaxed 20-second pickups with full recovery.
- **Breaks:** add one under *Start date and breaks* with the day you stop and the day you come back.
  Every remaining session moves forward, and race day updates. After a break of more than about
  two weeks, untick and redo the last week you completed before moving on.
- Sharp pain, not just soreness, means rest and get it checked.
""")

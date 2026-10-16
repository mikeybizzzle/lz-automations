"""Last Z alliance stats tracker.

  python lz_stats.py TRACKER.xlsx --tracked        # print who to capture (Active + Track=Yes), as JSON
  python lz_stats.py TRACKER.xlsx run.json         # log a capture run, update Member Reference, rebuild Summary
  python lz_stats.py TRACKER.xlsx --summary        # rebuild Summary only (e.g. after editing Member Reference)
  python lz_stats.py TRACKER.xlsx --export site/data/alliance.js   # write the web page's data file

run.json = {"date": "2026-10-16",
            "players": [{"name": ..., "rank": "R2", "hq": 29, "total": ..., "kills": ..., "structure": ...,
                         "tech": ..., "hero": ..., "mod": ..., "troop": ...}],
            "missing": ["names searched for in every rank panel and not found"],
            "note": "optional: shown as a note on the date header, e.g. 'Estimated backfill'"}
"""
import json, sys, os, datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter as L
from openpyxl.comments import Comment

STATS_SHEET, REF_SHEET, SUM_SHEET = "Member Stats", "Member Reference", "Summary"
STATS = [("hq", "HQ Level"), ("total", "Total Power"), ("kills", "Kills"),
         ("structure", "Structure Power"), ("tech", "Tech Power"), ("hero", "Hero Power"),
         ("mod", "Mod Vehicle Power"), ("troop", "Troop Power")]
BLOCK = len(STATS)
# Summary leaderboards, in display order. Troop Power is left out on purpose.
SUMMARY_STATS = [("total", "Total Power"), ("hero", "Hero Power"), ("tech", "Tech Power"),
                 ("structure", "Structure Power"), ("mod", "Mod Vehicle Power"), ("kills", "Kills")]
WINDOW_DAYS = 30
# Watchlist: flag a stat that grew 0.1% or less over 7 days, or 0.5% or less over 30 days. HQ and Troop excluded.
WATCH_SHORT_MAX, WATCH_LONG_MAX = 0.001, 0.005
WATCH_STATS = [("total", "Total Power"), ("kills", "Kills"), ("structure", "Structure Power"),
               ("tech", "Tech Power"), ("hero", "Hero Power"), ("mod", "Mod Vehicle Power")]
RANKS = ["R1", "R2", "R3", "R4"]

FMT_HQ = '"Lv."0'
FMT_BIG = '[>=999500]0.0,,"M";[>=1000]0,"k";0'
FMT_GAIN = '[>=999500]+0.0,,"M";[<=-999500]-0.0,,"M";+0,"k";-0,"k"'
FMT_DELTA = '+0.0%;-0.0%;0.0%'
FMT_DATE = "mmm d, yyyy"
F = "Arial"
INK = "1F2A36"
HEAD_FILL = PatternFill("solid", fgColor=INK)
SUB_FILL = PatternFill("solid", fgColor="D9DEE4")
NAME_FILL = PatternFill("solid", fgColor="EEF1F4")
UP, DOWN, MUTED = "1E7B34", "C0262D", "8A939C"
thin = Side(style="thin", color="B8C0C8")
thick = Side(style="medium", color=INK)


def font(**kw):
    kw.setdefault("name", F)
    return Font(**kw)


def as_date(v):
    return v.date() if isinstance(v, datetime.datetime) else v


# ---------------------------------------------------------------- Member Stats
def ensure_stats(wb):
    if STATS_SHEET in wb.sheetnames:
        return wb[STATS_SHEET]
    ws = wb.create_sheet(STATS_SHEET, 0)
    for c, label in ((1, "Player Name"), (2, "Stat")):
        ws.merge_cells(start_row=1, start_column=c, end_row=2, end_column=c)
        cell = ws.cell(1, c, label)
        cell.font = font(bold=True, color="FFFFFF")
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(2, c).fill = HEAD_FILL
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 19
    ws.row_dimensions[1].height = 20
    ws.freeze_panes = "C3"
    return ws


def stats_rows(ws):
    out, r = {}, 3
    while ws.cell(r, 1).value is not None:
        out[str(ws.cell(r, 1).value)] = r
        r += BLOCK
    return out, r


def stats_dates(ws):
    """[(date, number_col)] in sheet order."""
    out, c = [], 3
    while ws.cell(1, c).value is not None:
        out.append((as_date(ws.cell(1, c).value), c))
        c += 2
    return out


def log_stats(ws, run):
    date = datetime.date.fromisoformat(run["date"])
    dates = stats_dates(ws)
    if any(d == date for d, _ in dates):
        raise SystemExit(f"{date} is already logged. Nothing changed.")
    ncol = 3 + 2 * len(dates)
    dcol, prev = ncol + 1, (ncol - 2 if dates else None)

    ws.merge_cells(start_row=1, start_column=ncol, end_row=1, end_column=dcol)
    h = ws.cell(1, ncol, date)
    h.number_format = FMT_DATE
    h.font = font(bold=True, color="FFFFFF")
    h.alignment = Alignment(horizontal="center", vertical="center")
    if run.get("note"):  # e.g. estimated backfill; shows as a cell note and on the web page
        h.comment = Comment(run["note"], "lz_stats")
        h.font = font(bold=True, italic=True, color="F2C9A8")
    for c in (ncol, dcol):
        ws.cell(1, c).fill = HEAD_FILL
        ws.cell(2, c).fill = SUB_FILL
        ws.cell(2, c).font = font(bold=True)
        ws.cell(2, c).alignment = Alignment(horizontal="center")
        ws.column_dimensions[L(c)].width = 11
    ws.cell(2, ncol, "Number")
    ws.cell(2, dcol, "Delta")
    ws.cell(1, ncol).border = Border(left=thick)
    ws.cell(2, ncol).border = Border(left=thick)

    rows, next_row = stats_rows(ws)
    for p in run["players"]:
        name = p["name"]
        if name not in rows:
            r0 = next_row
            ws.merge_cells(start_row=r0, start_column=1, end_row=r0 + BLOCK - 1, end_column=1)
            nc = ws.cell(r0, 1, name)
            nc.font = font(bold=True)
            nc.alignment = Alignment(vertical="center", wrap_text=True)
            for i, (_, label) in enumerate(STATS):
                ws.cell(r0 + i, 1).fill = NAME_FILL
                lc = ws.cell(r0 + i, 2, label)
                lc.font = font()
                lc.fill = NAME_FILL
            rows[name] = r0
            next_row += BLOCK
        r0 = rows[name]
        for i, (key, _) in enumerate(STATS):
            r = r0 + i
            n = ws.cell(r, ncol, p.get(key))
            n.number_format = FMT_HQ if key == "hq" else FMT_BIG
            n.font = font(color=INK)
            n.alignment = Alignment(horizontal="right")

    # delta formulas for every row (players with no number this run stay blank)
    last = next_row - 1
    for r in range(3, last + 1):
        d = ws.cell(r, dcol)
        if prev:
            pn, cn = f"{L(prev)}{r}", f"{L(ncol)}{r}"
            d.value = f'=IF(OR({pn}="",{cn}="",{pn}=0),"",({cn}-{pn})/{pn})'
        d.number_format = FMT_DELTA
        d.font = font()
        d.alignment = Alignment(horizontal="right")
        bottom = thick if (r - 3) % BLOCK == BLOCK - 1 else thin
        for c in range(1, dcol + 1):
            left = thick if (c >= 3 and c % 2 == 1) else thin
            ws.cell(r, c).border = Border(left=left, right=thin, top=thin, bottom=bottom)

    rng = f"{L(dcol)}3:{L(dcol)}{last}"
    ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["0"], font=font(color=UP)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"], font=font(color=DOWN)))
    ws.freeze_panes = "C3"
    return L(ncol), L(dcol)


def read_history(ws):
    """{name: {stat_key: [(date, value), ...]}} for every player in Member Stats."""
    rows, _ = stats_rows(ws)
    dates = stats_dates(ws)
    hist = {}
    for name, r0 in rows.items():
        hist[name] = {}
        for i, (key, _) in enumerate(STATS):
            hist[name][key] = [(d, ws.cell(r0 + i, c).value) for d, c in dates
                               if isinstance(ws.cell(r0 + i, c).value, (int, float))]
    return hist, [d for d, _ in dates]


# ------------------------------------------------------------ Member Reference
REF_COLS = [("Player Name", 24), ("Rank", 10), ("Active Member", 16), ("Track Status", 14)]


def ensure_reference(wb):
    if REF_SHEET in wb.sheetnames:
        return wb[REF_SHEET]
    ws = wb.create_sheet(REF_SHEET, 1)
    for c, (label, width) in enumerate(REF_COLS, 1):
        cell = ws.cell(1, c, label)
        cell.font = font(bold=True, color="FFFFFF")
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[L(c)].width = width
    ws.row_dimensions[1].height = 20
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = "A1:D1"
    for col, choices in (("B", RANKS), ("C", ["Active", "Inactive"]), ("D", ["Yes", "No"])):
        dv = DataValidation(type="list", formula1='"' + ",".join(choices) + '"', allow_blank=False,
                            showErrorMessage=True, errorTitle="Pick from the list",
                            error="Choose one of: " + ", ".join(choices))
        dv.add(f"{col}2:{col}500")
        ws.add_data_validation(dv)
    # grey out rows that are not being tracked
    ws.conditional_formatting.add("A2:D500", FormulaRule(
        formula=['AND($A2<>"",OR($C2="Inactive",$D2="No"))'], font=font(color=MUTED),
        fill=PatternFill("solid", fgColor="F2F3F5")))
    ws.conditional_formatting.add("C2:C500", CellIsRule(operator="equal", formula=['"Inactive"'],
                                                        font=font(color=DOWN, bold=True)))
    return ws


def ref_rows(ws):
    out, r = {}, 2
    while ws.cell(r, 1).value not in (None, ""):
        out[str(ws.cell(r, 1).value)] = r
        r += 1
    return out, r


def style_ref_row(ws, r):
    for c in range(1, 5):
        cell = ws.cell(r, c)
        cell.font = font(bold=(c == 1))
        cell.alignment = Alignment(horizontal="left" if c == 1 else "center")
        cell.border = Border(bottom=thin)


def tracked(ws):
    rows, _ = ref_rows(ws)
    out = []
    for name, r in rows.items():
        active = str(ws.cell(r, 3).value or "").strip().lower() == "active"
        track = str(ws.cell(r, 4).value or "").strip().lower() == "yes"
        if active and track:
            out.append({"name": name, "rank": ws.cell(r, 2).value})
    return out


def update_reference(ws, run):
    rows, next_row = ref_rows(ws)
    added, rank_changes, inactivated = [], [], []
    for p in run["players"]:
        name, rank = p["name"], p.get("rank")
        if name not in rows:
            ws.cell(next_row, 1, name)
            ws.cell(next_row, 2, rank)
            ws.cell(next_row, 3, "Active")
            ws.cell(next_row, 4, "Yes")
            style_ref_row(ws, next_row)
            rows[name] = next_row
            next_row += 1
            added.append(name)
            continue
        r = rows[name]
        if rank and ws.cell(r, 2).value != rank:
            rank_changes.append(f"{name} {ws.cell(r, 2).value}->{rank}")
            ws.cell(r, 2, rank)
        ws.cell(r, 3, "Active")
    for name in run.get("missing", []):
        if name in rows and ws.cell(rows[name], 3).value != "Inactive":
            ws.cell(rows[name], 3, "Inactive")
            inactivated.append(name)
    return added, rank_changes, inactivated


# --------------------------------------------------------------------- Summary
def pick_baselines(dates):
    """Latest date, previous capture, and the 30-day baseline (latest capture on/before latest-30d,
    else the earliest capture, flagged as a shorter window)."""
    if len(dates) < 2:
        return (dates[-1] if dates else None), None, None, False
    latest, prev = dates[-1], dates[-2]
    target = latest - datetime.timedelta(days=WINDOW_DAYS)
    older = [d for d in dates[:-1] if d <= target]
    if older:
        return latest, prev, older[-1], True
    return latest, prev, dates[0], False


def base_on_or_before(dates, days):
    """Latest capture on or before `days` before the newest capture; the first capture if history is shorter."""
    target = dates[-1] - datetime.timedelta(days=days)
    older = [d for d in dates[:-1] if d <= target]
    return older[-1] if older else dates[0]


def leaderboard(hist, names, key, base_date, latest):
    rows, no_data = [], []
    for n in names:
        series = dict(hist.get(n, {}).get(key, []))
        now = series.get(latest)
        start = series.get(base_date)
        if now is None or not start:
            no_data.append(n)
            continue
        rows.append((n, start, now, now - start, (now - start) / start))
    rows.sort(key=lambda x: (-x[4], -x[3]))
    return rows, no_data


def build_summary(wb):
    if SUM_SHEET in wb.sheetnames:
        del wb[SUM_SHEET]
    ws = wb.create_sheet(SUM_SHEET, 2)
    hist, dates = read_history(wb[STATS_SHEET])
    names = [t["name"] for t in tracked(wb[REF_SHEET])]
    latest, prev, base30, full30 = pick_baselines(dates)

    # B-D current ranking | F-K since previous | M-R long window
    widths = [2, 5, 20, 10, 3, 5, 20, 10, 10, 10, 10, 3, 5, 20, 10, 10, 10, 10]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[L(i)].width = w
    ws.sheet_view.showGridLines = False

    t = ws.cell(1, 2, "Alliance Summary")
    t.font = font(bold=True, size=16, color=INK)
    fmt = lambda d: d.strftime("%b %-d, %Y") if d else "—"
    win30 = (f"last {WINDOW_DAYS} days (since {fmt(base30)})" if full30
             else f"since first capture, {fmt(base30)} ({(latest - base30).days} days; "
                  f"full {WINDOW_DAYS}-day view once history allows)" if base30 else "—")
    meta = [f"Latest capture: {fmt(latest)}", f"Previous capture: {fmt(prev)}",
            f"Long window: {win30}",
            f"Players: {len(names)} tracked (Active + Track Status Yes on Member Reference). "
            f"Troop Power is left out: it swings with fights and healing."]
    for i, line in enumerate(meta):
        c = ws.cell(2 + i, 2, line)
        c.font = font(size=10, color="4A5560")
    row = 7
    if latest is None:
        ws.cell(row, 2, "No captures logged yet.").font = font(italic=True, color=MUTED)
        return

    def head(r, c0, title, labels):
        ws.cell(r, c0, title).font = font(bold=True, size=10, color=INK)
        r += 1
        for j, label in enumerate(labels):
            cell = ws.cell(r, c0 + j, label)
            cell.font = font(bold=True, size=9, color="FFFFFF")
            cell.fill = HEAD_FILL
            cell.alignment = Alignment(horizontal="left" if j == 1 else "center")
        return r + 1

    def body_cell(r, c, v, i, fmt_=None, align="right", **kw):
        cell = ws.cell(r, c, v)
        cell.font = font(size=10, **kw)
        if fmt_:
            cell.number_format = fmt_
        cell.alignment = Alignment(horizontal=align)
        cell.border = Border(bottom=thin)
        if i % 2 == 0:
            cell.fill = NAME_FILL

    def alltime_table(r, c0, key, title):
        # % increase since the first capture, ranked highest to lowest (compact: # / Player / % Change)
        rows_, _ = leaderboard(hist, names, key, dates[0], latest)
        r = head(r, c0, title, ["#", "Player", "% Change"])
        for i, (n, start, now, g, pct) in enumerate(rows_, 1):
            body_cell(r, c0, i, i, align="center")
            body_cell(r, c0 + 1, n, i, align="left")
            body_cell(r, c0 + 2, pct, i, FMT_DELTA, bold=True, color=UP if pct > 0 else DOWN if pct < 0 else MUTED)
            r += 1
        return r

    def change_table(r, c0, title, rows_, no_data):
        r = head(r, c0, title, ["#", "Player", "Start", "Now", "Gain", "% Change"])
        for i, (n, start, now, gain, pct) in enumerate(rows_, 1):
            body_cell(r, c0, i, i, align="center")
            body_cell(r, c0 + 1, n, i, align="left")
            body_cell(r, c0 + 2, start, i, FMT_BIG)
            body_cell(r, c0 + 3, now, i, FMT_BIG)
            body_cell(r, c0 + 4, gain, i, FMT_GAIN)
            body_cell(r, c0 + 5, pct, i, FMT_DELTA, bold=True,
                      color=UP if pct > 0 else DOWN if pct < 0 else MUTED)
            r += 1
        if no_data:
            cell = ws.cell(r, c0 + 1, "No comparison yet: " + ", ".join(no_data))
            cell.font = font(size=9, italic=True, color=MUTED)
            r += 1
        return r

    def pending(r, c0, title):
        ws.cell(r, c0, title).font = font(bold=True, size=10, color=INK)
        ws.cell(r + 1, c0, "Fills in after the second capture.").font = font(
            size=9, italic=True, color=MUTED)
        return r + 2

    # Watchlist: a stat (HQ and Troop excluded) that grew <= 0.1% over 7 days or <= 0.5% over 30 days
    if prev is not None:
        base7, baseL = base_on_or_before(dates, 7), base_on_or_before(dates, WINDOW_DAYS)
        flags = []
        for n in names:
            for key, label in WATCH_STATS:
                s = dict(hist.get(n, {}).get(key, []))
                now, a7, aL = s.get(latest), s.get(base7), s.get(baseL)
                p7 = (now - a7) / a7 if now is not None and a7 else None
                pL = (now - aL) / aL if now is not None and aL else None
                hit7 = p7 is not None and p7 <= WATCH_SHORT_MAX
                hitL = pL is not None and pL <= WATCH_LONG_MAX
                if hit7 or hitL:
                    flags.append((n, label, now, p7, pL, hit7, hitL))
        members_flagged = len({f[0] for f in flags})
        ws.cell(row, 2, f"Watchlist: {members_flagged} member(s) flagged").font = font(
            bold=True, size=12, color=DOWN if flags else INK)
        row += 1
        ws.cell(row, 2, "Flags any stat that grew +0.1% or less in 7 days, or +0.5% or less in 30 days. "
                        "HQ and Troop Power are excluded.").font = font(size=10, color="4A5560")
        row += 1
        if flags:
            heads = ["Player", "Stat", "Now", f"7 days ({fmt(base7)})", f"30 days ({fmt(baseL)})"]
            cols = [3, 7, 9, 10, 11]  # C (player), G (stat), I, J, K: the wide columns of this tab
            for c, label in zip(cols, heads):
                cell = ws.cell(row, c, label)
                cell.font = font(bold=True, size=9, color="FFFFFF")
                cell.fill = HEAD_FILL
                cell.alignment = Alignment(horizontal="left" if c in (3, 7) else "center")
            for c in range(3, 12):
                ws.cell(row, c).fill = HEAD_FILL
            row += 1
            for i, (n, label, now, p7, pL, hit7, hitL) in enumerate(flags):
                vals = [(3, n if i == 0 or flags[i - 1][0] != n else None, None), (7, label, None),
                        (9, now, FMT_BIG), (10, p7, FMT_DELTA), (11, pL, FMT_DELTA)]
                for c, v, f_ in vals:
                    cell = ws.cell(row, c, v)
                    cell.font = font(size=10, bold=(c == 10 and hit7) or (c == 11 and hitL),
                                     color=DOWN if (c == 10 and hit7) or (c == 11 and hitL) else INK)
                    if f_:
                        cell.number_format = f_
                    cell.alignment = Alignment(horizontal="left" if c in (3, 7) else "right")
                    cell.border = Border(bottom=thin)
                row += 1
        else:
            ws.cell(row, 2, "Nobody flagged.").font = font(size=10, color=UP)
            row += 1
        row += 1

    long_title = ("Last 30 days" if full30 else "Since first capture") + f" ({fmt(base30)})"
    for key, label in SUMMARY_STATS:
        ws.cell(row, 2, label).font = font(bold=True, size=12, color="FFFFFF")
        for c in range(2, 19):
            ws.cell(row, c).fill = HEAD_FILL
        row += 1
        if prev is None:
            ends = [pending(row, 2, "All time")]
            ends.append(pending(row, 6, "Since previous capture"))
            ends.append(pending(row, 13, f"Last {WINDOW_DAYS} days"))
        else:
            ends = [alltime_table(row, 2, key, f"All time (since {fmt(dates[0])})")]
            ends.append(change_table(row, 6, f"Since previous capture ({fmt(prev)})",
                                     *leaderboard(hist, names, key, prev, latest)))
            ends.append(change_table(row, 13, long_title,
                                     *leaderboard(hist, names, key, base30, latest)))
        row = max(ends) + 1
    ws.freeze_panes = "A6"


# ---------------------------------------------------------------- web export
def alliance_info(xlsx_path):
    """Alliance name for the page header, from data/config.json next to the workbook:
    {"alliance": {"tag": "RfC", "name": "RebornFromChaos", "state": "644"}}"""
    cfg = os.path.join(os.path.dirname(os.path.abspath(xlsx_path)), "config.json")
    try:
        return json.load(open(cfg, encoding="utf-8")).get("alliance") or {}
    except (OSError, ValueError):
        return {}


def export_js(wb, out_path, alliance=None):
    """Write the web page's data file: window.LZ_ALLIANCE = {...};"""
    hist, dates = read_history(wb[STATS_SHEET])
    ref = wb[REF_SHEET]
    rows, _ = ref_rows(ref)
    members = []
    for name in list(rows) + [n for n in hist if n not in rows]:
        r = rows.get(name)
        h = {}
        for key, series in hist.get(name, {}).items():
            for d, v in series:
                h.setdefault(d.isoformat(), {})[key] = v
        members.append({
            "name": name,
            "rank": ref.cell(r, 2).value if r else None,
            "active": (str(ref.cell(r, 3).value).lower() == "active") if r else False,
            "track": (str(ref.cell(r, 4).value).lower() == "yes") if r else False,
            "history": h,
        })
    sws = wb[STATS_SHEET]
    notes = {d.isoformat(): sws.cell(1, c).comment.text for d, c in stats_dates(sws) if sws.cell(1, c).comment}
    data = {"alliance": alliance or {"name": "Alliance"}, "dates": [d.isoformat() for d in dates], "notes": notes,
            "exported": datetime.datetime.now().isoformat(timespec="minutes"), "members": members}
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("// Generated by lz_stats.py from Last Z Alliance Stats.xlsx. Do not edit by hand.\n")
        f.write("window.LZ_ALLIANCE = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
    print(f"Exported {len(members)} members, {len(dates)} captures to {out_path}")


# ------------------------------------------------------------------------ main
def main():
    path, arg = sys.argv[1], sys.argv[2]
    if arg == "--export":
        export_js(load_workbook(path), sys.argv[3], alliance_info(path))
        return
    if os.path.exists(path):
        wb = load_workbook(path)
        ensure_stats(wb)
    else:
        wb = Workbook()
        blank = wb.active
        ensure_stats(wb)
        wb.remove(blank)
    ref = ensure_reference(wb)

    if arg == "--tracked":
        print(json.dumps(tracked(ref), ensure_ascii=False, indent=1))
        return
    if arg != "--summary":
        run = json.load(open(arg, encoding="utf-8"))
        cols = log_stats(wb[STATS_SHEET], run)
        added, ranks, gone = update_reference(ref, run)
        print(f"Logged {len(run['players'])} players for {run['date']} in {cols[0]}:{cols[1]}.")
        for label, items in (("Added to Member Reference", added), ("Rank changes", ranks),
                             ("Marked Inactive", gone)):
            if items:
                print(f"{label}: {', '.join(items)}")
        captured = {p["name"] for p in run["players"]}
        skipped = [t["name"] for t in tracked(ref) if t["name"] not in captured]
        if skipped:
            print("Tracked but not captured (no data this date):", ", ".join(skipped))
    build_summary(wb)
    wb.active = 0
    wb.save(path)
    print("Summary rebuilt.")


if __name__ == "__main__":
    main()

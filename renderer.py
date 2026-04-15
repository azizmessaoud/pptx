import os
from mck_ppt import MckEngine
from mck_ppt.review import autofix
from mck_ppt.constants import NAVY, ACCENT_BLUE, LIGHT_BLUE

COLORS = [NAVY, ACCENT_BLUE, LIGHT_BLUE]


def _truncate_items(items: list, max_words: int = 12) -> list:
    result = []
    for item in items:
        words = str(item).split()
        result.append(" ".join(words[:max_words]) + ("…" if len(words) > max_words else ""))
    return result


LAYOUT_MAP = {
    "bullet_2col": lambda eng, s: eng.two_column_text(s["title"], [
        ("A", s.get("left_title", ""), s["left"]),
        ("B", s.get("right_title", ""), s["right"])
    ]),
    "donut_chart": lambda eng, s: eng.donut(s["title"], [
        (seg[0], seg[1], COLORS[i % 3]) for i, seg in enumerate(s["segments"])
    ]),
    "data_table": lambda eng, s: eng.data_table(s["title"], s["headers"], s["rows"]),
    "vertical_steps": lambda eng, s: eng.vertical_steps(s["title"], [
        (str(i+1), step, "") for i, step in enumerate(s["steps"])
    ]),
    "four_column": lambda eng, s: eng.four_column(s["title"], s["columns"]),
    "numbered_list_panel": lambda eng, s: eng.numbered_list_panel(s["title"], [
        (item, "") for item in _truncate_items(s["items"])
    ]),
    "pros_cons": lambda eng, s: eng.pros_cons(
        s["title"],
        s.get("pros_title", "Pour"),
        s["pros"],
        s.get("cons_title", "Contre"),
        s["cons"]
    ),
    "key_takeaway": lambda eng, s: eng.executive_summary(
        s["title"],
        s.get("headline", ""),
        [(str(i+1), item, "") for i, item in enumerate(s.get("takeaways", []))]
    ),
    "three_stat": lambda eng, s: eng.three_stat(s["title"], s["stats"]),
    "timeline": lambda eng, s: eng.timeline(s["title"], s["events"]),
}


def _fix_toc_title(eng: MckEngine, replacement: str = "Sommaire") -> None:
    """Replace hardcoded Chinese TOC title with a French label."""
    toc_slide = eng.prs.slides[1]  # index 1 = TOC slide
    for shape in toc_slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            full = "".join(r.text for r in para.runs)
            if "目录" in full:
                for run in para.runs:
                    run.text = run.text.replace("目录", replacement)


def render_deck(plan: dict, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    total = len(plan["slides"]) + 2  # cover + toc + content slides
    eng = MckEngine(total_slides=total)

    eng.cover(title=plan["title"], subtitle=plan.get("subtitle", ""))

    toc_items = [(str(i+1), s["title"], "") for i, s in enumerate(plan["slides"])]
    eng.toc(items=toc_items)
    _fix_toc_title(eng)  # ← patch Chinese → Sommaire

    for slide in plan["slides"]:
        fn = LAYOUT_MAP.get(slide["type"])
        if fn:
            fn(eng, slide)
        else:
            print(f"[WARN] Unknown layout: {slide['type']} — skipped")

    eng.save(output_path)
    result = autofix(output_path, max_rounds=5)
    result.print_summary()
    return output_path
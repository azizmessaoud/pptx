import os
from mck_ppt import MckEngine
from mck_ppt.review import autofix
from mck_ppt.constants import NAVY, ACCENT_BLUE, LIGHT_BLUE

COLORS = [NAVY, ACCENT_BLUE, LIGHT_BLUE]

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
        (item, "") for item in s["items"]
    ]),
    "pros_cons": lambda eng, s: eng.pros_cons(s["title"], s["pros"], s["cons"]),
    "three_stat": lambda eng, s: eng.three_stat(s["title"], s["stats"]),
    "timeline": lambda eng, s: eng.timeline(s["title"], s["events"]),
}

def render_deck(plan: dict, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    eng = MckEngine(total_slides=len(plan["slides"]) + 1)
    eng.cover(title=plan["title"], subtitle=plan.get("subtitle", ""))

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
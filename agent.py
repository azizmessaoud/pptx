import os
from slide_planner import plan_slides
from renderer import render_deck

def generate_deck(topic: str, context: str, mode: str = "mode2",
                  output: str = "output/deck.pptx") -> str:
    print(f"Planning: {topic}")
    plan = plan_slides(topic, context, mode)
    print(f"{len(plan['slides'])} slides planned")
    path = render_deck(plan, output)
    print(f"Saved → {path}")
    return path

if __name__ == "__main__":
    # MODE 2 TEST — doctor-facing product sheet
    context = """
    Product: Fersang (Cholécalciférol — Vitamin D3 1000 UI)
    Manufacturer: Vital Laboratory, Tunisia
    Indication: Vitamin D deficiency, osteoporosis prevention, rickets
    Mechanism: Cholecalciferol is converted in liver to 25-OH-D3, 
               then in kidney to active 1,25-(OH)2-D3 (calcitriol).
               Regulates calcium and phosphorus absorption.
    Dosage: Adults 1 tablet/day, Children >12: 1 tablet/day,
            Elderly: 2 tablets/day, Pregnant: consult physician
    Contraindications: Hypercalcemia, severe renal insufficiency,
                       hypersensitivity to cholecalciferol
    Side effects: Rare — nausea, hypercalciuria at high doses
    Clinical evidence: Meta-analysis 2023 — D3 supplementation reduces
                       fracture risk by 23% in adults >60 (n=12,000)
    """
    generate_deck(
        topic="Fersang — Fiche Produit",
        context=context,
        mode="mode2",
        output="output/fersang_mode2.pptx"
    )

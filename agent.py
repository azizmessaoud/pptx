import os
import sys
from datetime import datetime
from slide_planner import plan_slides
from renderer import render_deck


FERSANG_CONTEXT = """
Product: Fersang (Cholécalciférol — Vitamine D3 1000 UI)
Manufacturer: Vital Laboratory, Tunisia
Indication: Carence en vitamine D, prévention de l'ostéoporose, rachitisme
Mechanism: Cholécalciférol est converti dans le foie en 25-OH-D3,
           puis dans les reins en 1,25-(OH)2-D3 (calcitriol).
           Régule l'absorption du calcium et du phosphore.
Dosage: Adultes 1 comprimé/jour, Enfants >12 ans: 1 comprimé/jour,
        Personnes âgées: 2 comprimés/jour, Femmes enceintes: consulter un médecin
Contraindications: Hypercalcémie, insuffisance rénale sévère,
                   hypersensibilité au cholécalciférol
Side effects: Rares — nausées, hypercalciurie à fortes doses
Clinical evidence: Méta-analyse 2023 — supplémentation en D3 réduit
                   le risque de fracture de 23% chez les adultes >60 ans (n=12 000)
"""

FERSANG_TRAINING_CONTEXT = """
Rep: Ahmed Ben Ali
Session date: 2026-04-15
Product: Fersang (Vitamine D3)

Scores:
- Product knowledge: 78% — Satisfactory
- Objection handling: 52% — Needs improvement
- Closing technique: 65% — Satisfactory
- Compliance: 90% — Strong

XAI strengths:
- Clear explanation of mechanism of action
- Good use of clinical evidence (fracture reduction 23%)

XAI weaknesses:
- Failed to address price objection
- Did not mention elderly dosage (2 tabs/day)

Objections encountered:
- "Vitamine D is available cheaper elsewhere" → Rep ignored → Should compare bioavailability
- "My patients don't need supplements" → Rep agreed → Should cite deficiency prevalence data
"""

DEFAULT_CONTEXTS = {
    "fersang": FERSANG_CONTEXT,
    "fersang_training": FERSANG_TRAINING_CONTEXT,
}


def generate_deck(topic: str, context: str, mode: str = "mode2",
                  output: str = None) -> str:
    print(f"Planning: {topic}")
    plan = plan_slides(topic, context, mode)
    print(f"{len(plan['slides'])} slides planned")

    if output is None:
        slug = topic.lower().replace("—", "").replace("-", "").replace(" ", "_").strip("_")
        slug = "".join(c for c in slug if c.isalnum() or c == "_")[:30]
        ts = datetime.now().strftime("%H%M%S")
        output = f"output/{slug}_{mode}_{ts}.pptx"

    path = render_deck(plan, output)
    print(f"Saved → {path}")
    return path


if __name__ == "__main__":
    product = sys.argv[1] if len(sys.argv) > 1 else "Fersang"
    lang    = sys.argv[2] if len(sys.argv) > 2 else "FR"
    mode    = sys.argv[3] if len(sys.argv) > 3 else "mode2"

    ctx_path = f"products/{product.lower()}.txt"
    if os.path.exists(ctx_path):
        context = open(ctx_path, encoding="utf-8").read()
        print(f"Context loaded from: {ctx_path}")
    elif product.lower() in DEFAULT_CONTEXTS:
        context = DEFAULT_CONTEXTS[product.lower()]
        print(f"Context loaded from built-in defaults")
    else:
        print(f"[ERROR] No context found for '{product}'.")
        print(f"  → Create products/{product.lower()}.txt or add to DEFAULT_CONTEXTS")
        sys.exit(1)

    generate_deck(
        topic=f"{product} — Fiche Produit",
        context=f"Language: {lang}\n\n{context}",
        mode=mode
    )
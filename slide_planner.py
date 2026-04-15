import os, json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def plan_slides(topic: str, context: str, mode: str = "mode2") -> dict:
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", f"{mode}.txt")
    system_prompt = open(prompt_path, encoding="utf-8").read()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Topic: {topic}\n\nContext:\n{context}"}
        ],
        temperature=0.2,      # ← lower = less hallucination in JSON
        max_tokens=4096,
    )

    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            from json_repair import repair_json
            return json.loads(repair_json(raw))
        except Exception:
            raise ValueError(f"LLM returned invalid JSON:\n{raw[:500]}")
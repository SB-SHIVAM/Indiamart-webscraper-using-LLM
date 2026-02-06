# llm_helper.py
import ollama
import json
import re
import multiprocessing

# =========================
# FORCE qwen3:4b (NO FALLBACK)
# =========================
def get_model():
    models = ollama.list().get("models", [])

    # IMPORTANT: key is "model", not "name"
    model_names = [m["model"] for m in models]

    if "qwen3:4b" not in model_names:
        raise RuntimeError(
            "qwen3:4b is not installed. Run: ollama pull qwen3:4b"
        )

    return "qwen3:4b"

MODEL = get_model()
print(f"[LLM] Using model: {MODEL}")

# =========================
# TEXT NORMALIZER
# =========================
def normalize_text(text, limit=3000):
    text = re.sub(r"\s+", " ", text)
    return text.strip()[:limit]

# =========================
# INTERNAL WORKER
# =========================
def _worker(text, queue):
    prompt = f"""
You normalize review data.

Rules:
- Missing values -> "N/A"
- Stars must be 1-5
- Output VALID JSON ONLY

TEXT:
{text}

OUTPUT:
{{
  "metrics": {{
    "response": "N/A",
    "quality": "N/A",
    "delivery": "N/A"
  }},
  "reviews": [
    {{
      "name": "User",
      "stars": "4",
      "product": "Product",
      "text": "Review text"
    }}
  ]
}}
"""
    try:
        res = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.0,
                "num_ctx": 4096,
                "num_predict": 400
            }
        )
        out = res["message"]["content"]
        out = out.replace("```json", "").replace("```", "").strip()
        queue.put(json.loads(out))
    except:
        queue.put({})

# =========================
# SAFE CALL (2s HARD KILL)
# =========================
def call_llm_safe(text, timeout=2):
    text = normalize_text(text)
    if not text or len(text) < 50:
        return {}

    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=_worker, args=(text, q))
    p.start()
    p.join(timeout)

    if p.is_alive():
        print("[LLM] Timeout -> killed")
        p.terminate()
        p.join()
        return {}

    return q.get() if not q.empty() else {}

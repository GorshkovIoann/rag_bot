import requests
import json

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

MODEL = "google/gemini-2.0-flash-001"

def call_gemini(system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ]
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def humanize_answer(question: str, *blocks: str) -> str:
    """
    Теперь принимает вопрос и произвольное число текстовых блоков.
    """
    system_prompt = (
        "Вы — эксперт-помощник. Вам даны текстовые блоки одного документа, "
        "упорядоченные по релевантности (первый — самый релевантный).\n"
        "Используйте исключительно предоставленные блоки для ответа на вопрос.\n"
        "Ответьте по-русски человеческим языком.\n"
        "Если ответа нет — скажите «Из предоставленных блоков я не могу найти ответ на этот вопрос»."
    )
    joined = "\n---\n".join(blocks)
    user_prompt = f"Блоки:\n{joined}\n\nВопрос: {question}\n\nОтвет:"
    return call_gemini(system_prompt, user_prompt)


def judge_answer(reference, generated):
    system = (
        "Ты судья, который сравнивает правильный (референсный) ответ и предложенный ответ. Ответ не обязан быть дословным но должен быть корректным и передавать суть. "
        "Ответь только JSON'ом вида {\"correct\": true} или {\"correct\": false}."
    )
    user = f"Референс: {reference}\nОтвет системы: {generated}\nСкажи, правильный ли ответ."
    resp = call_gemini(system, user)
    try:
        return json.loads(resp)
    except Exception:
        return {"correct": False, "note": "Ошибка парсинга ответа от модели"}

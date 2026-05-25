import anthropic
import json
import os
from datetime import datetime, timezone, timedelta

TWN = timezone(timedelta(hours=8))
today = datetime.now(TWN).strftime('%Y-%m-%d')

SIGNS = [
    {"name": "牡羊座", "symbol": "♈", "en": "Aries",       "dates": "3/21–4/19"},
    {"name": "金牛座", "symbol": "♉", "en": "Taurus",      "dates": "4/20–5/20"},
    {"name": "雙子座", "symbol": "♊", "en": "Gemini",      "dates": "5/21–6/20"},
    {"name": "巨蟹座", "symbol": "♋", "en": "Cancer",      "dates": "6/21–7/22"},
    {"name": "獅子座", "symbol": "♌", "en": "Leo",         "dates": "7/23–8/22"},
    {"name": "處女座", "symbol": "♍", "en": "Virgo",       "dates": "8/23–9/22"},
    {"name": "天秤座", "symbol": "♎", "en": "Libra",       "dates": "9/23–10/22"},
    {"name": "天蠍座", "symbol": "♏", "en": "Scorpio",     "dates": "10/23–11/21"},
    {"name": "射手座", "symbol": "♐", "en": "Sagittarius", "dates": "11/22–12/21"},
    {"name": "摩羯座", "symbol": "♑", "en": "Capricorn",   "dates": "12/22–1/19"},
    {"name": "水瓶座", "symbol": "♒", "en": "Aquarius",    "dates": "1/20–2/18"},
    {"name": "雙魚座", "symbol": "♓", "en": "Pisces",      "dates": "2/19–3/20"},
]

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

signs_list = "\n".join(f"{s['name']} ({s['en']})" for s in SIGNS)

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": f"""今天是 {today}，請為以下12個星座各寫一段今日運勢（繁體中文），每段約80–100字，包含：
1. 整體運勢（幸運指數，stars 為 1–5 的整數）
2. 愛情運勢簡述
3. 事業／財運簡述
4. 今日建議一句話

請以 JSON 格式回覆，格式如下（只回覆 JSON，不要其他文字）：
{{
  "signs": [
    {{
      "name": "星座名",
      "stars": 3,
      "overall": "整體運勢描述",
      "love": "愛情運勢",
      "career": "事業財運",
      "advice": "今日建議"
    }}
  ]
}}

星座清單：
{signs_list}"""
    }]
)

raw = message.content[0].text.strip()
if raw.startswith("```"):
    lines = raw.splitlines()
    raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:]).strip()

parsed = json.loads(raw)

sign_meta = {s["name"]: s for s in SIGNS}
for item in parsed["signs"]:
    meta = sign_meta.get(item["name"], {})
    item["symbol"] = meta.get("symbol", "")
    item["dates"] = meta.get("dates", "")

output = {
    "date": today,
    "generated_at": datetime.now(TWN).isoformat(),
    "signs": parsed["signs"],
}

os.makedirs("horoscope", exist_ok=True)
with open("horoscope/data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✓ 已生成 {today} 星座運勢")

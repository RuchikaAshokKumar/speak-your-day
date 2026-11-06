import os
import re
import requests
import dateparser
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GNANI_API_KEY")

TIME_RE = r"(?:at\s+)?\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)"
DAY_RE = r"\b(today|tonight|tomorrow)\b"
ACTIONS = ["call", "submit", "buy", "meet", "finish", "send", "pay",
           "study", "attend", "email", "book", "visit", "clean", "prepare"]
FILLERS = ["i have to", "i need to", "i must", "i have a", "i have",
           "remind me to", "and", "then", "to"]


def transcribe(path):
    """Send audio to Prisma, get text back."""
    with open(path, "rb") as f:
        r = requests.post(
            "https://api.vachana.ai/stt/v3",
            headers={"X-API-Key-ID": API_KEY},
            files={"audio_file": f},
            data={"language_code": "en-IN"},
            timeout=60,
        )
    r.raise_for_status()
    return r.json()["transcript"]


def split_tasks(text):
    """Cut one long sentence into separate tasks."""
    text = text.lower().replace(".", ",").replace(" and ", ", ")
    for word in ACTIONS:
        text = re.sub(r"\s+(" + word + r")\b", r", \1", text)
    return [p.strip() for p in text.split(",") if p.strip()]


def parse_task(part):
    """Find the time and the task name inside one piece."""
    time_m = re.search(TIME_RE, part)
    day_m = re.search(DAY_RE, part)
    day_txt = day_m.group(1) if day_m else ""
    time_txt = time_m.group(0).replace("at ", "") if time_m else ""

    when = None
    if time_txt:
        when = dateparser.parse(f"{day_txt} {time_txt}".strip(),
                                settings={"PREFER_DATES_FROM": "future"})
    elif day_txt:
        when = dateparser.parse(day_txt)

    task = re.sub(TIME_RE, "", part)
    task = re.sub(DAY_RE, "", task).strip()
    changed = True
    while changed:
        changed = False
        for filler in FILLERS:
            if task.startswith(filler + " "):
                task = task[len(filler):].strip()
                changed = True
    return {"task": task, "when": when, "has_time": bool(time_txt)}


def build_list(text):
    return [parse_task(p) for p in split_tasks(text)]


if __name__ == "__main__":
    text = transcribe("sample.m4a")
    print("Heard:", text)
    print()
    for item in build_list(text):
        if item["when"] and item["has_time"]:
            when = item["when"].strftime("%a %d %b, %I:%M %p")
        elif item["when"]:
            when = item["when"].strftime("%a %d %b") + " (no time)"
        else:
            when = "no time set"
        print("-", item["task"], "->", when)
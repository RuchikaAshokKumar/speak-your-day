import html
import os
import hashlib
from datetime import datetime, timedelta

import requests
import streamlit as st
from dotenv import load_dotenv

from brain import build_list

load_dotenv()
API_KEY = os.getenv("GNANI_API_KEY")
HEADERS = {"X-API-Key-ID": API_KEY}

st.set_page_config(page_title="Speak Your Day", page_icon="🗣️")

# ---------- Gnani calls ----------
def transcribe_bytes(audio_bytes):
    r = requests.post(
        "https://api.vachana.ai/stt/v3",
        headers=HEADERS,
        files={"audio_file": ("recording.wav", audio_bytes, "audio/wav")},
        data={"language_code": "en-IN"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["transcript"]


@st.cache_data(show_spinner=False)
def speak(text):
    payload = {
        "text": text,
        "voice": "Nalini",
        "model": "timbre-v2.5",
        "language": "en-IN",
        "speed": 1.0,
        "audio_config": {
            "sample_rate": 48000,
            "num_channels": 1,
            "sample_width": 2,
            "encoding": "linear_pcm",
            "container": "wav",
        },
    }
    r = requests.post(
        "https://api.vachana.ai/api/v1/tts/inference",
        headers={**HEADERS, "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return r.content


# ---------- Turn tasks into spoken words ----------
HOURS = ["twelve", "one", "two", "three", "four", "five", "six",
         "seven", "eight", "nine", "ten", "eleven"]
COUNTS = ["no", "one", "two", "three", "four", "five", "six",
          "seven", "eight", "nine", "ten"]


def say_time(dt):
    mins = {0: "", 15: " fifteen", 30: " thirty", 45: " forty five"}.get(
        dt.minute, f" {dt.minute}")
    ampm = "am" if dt.hour < 12 else "pm"
    return f"{HOURS[dt.hour % 12]}{mins} {ampm}"


def say_when(item):
    w = item["when"]
    if not w:
        return ""
    today = datetime.now().date()
    if w.date() == today:
        day = "today"
    elif w.date() == today + timedelta(days=1):
        day = "tomorrow"
    else:
        day = w.strftime("%A")
    return f"{day} at {say_time(w)}" if item["has_time"] else day


def summary(tasks):
    if not tasks:
        return "I could not find any tasks."
    n = len(tasks)
    count = COUNTS[n] if n < len(COUNTS) else str(n)
    parts = [f"{t['task']} {say_when(t)}".strip() for t in tasks]
    return f"You have {count} task{'s' if n > 1 else ''}. " + ". ".join(parts) + "."


# ---------- App state ----------
for key, default in [("tasks", []), ("last_audio", None), ("play", None),
                     ("heard", ""), ("alerts", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<style>
.block-container {max-width: 720px; padding-top: 2rem;}
.hero {text-align:center; padding: 28px 16px; border-radius: 24px;
  background: linear-gradient(135deg,#8B5CF6 0%,#EC4899 55%,#F59E0B 100%);
  box-shadow: 0 10px 40px rgba(139,92,246,.35); margin-bottom: 24px;}
.hero h1 {color:white; font-size: 2.2rem; margin:0; padding:0;}
.hero p {color:rgba(255,255,255,.92); margin:8px 0 0 0; font-size:1.05rem;}
.heard {background:#1A1B33; border-left:4px solid #8B5CF6; padding:12px 16px;
  border-radius:12px; margin:14px 0; color:#E5E7FF;}
.task {font-size:1.05rem; line-height:1.5;}
.task.done {opacity:.45; text-decoration: line-through;}
.when {color:#A5B4FC; font-size:.9rem;}
.empty {text-align:center; padding:28px; border:2px dashed #3B3D6B;
  border-radius:16px; color:#A5B4FC;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius:16px;
  border-color:#2E3060; background:#15162B;}
.stButton>button {border-radius:999px; border:none; font-weight:600;
  background:linear-gradient(90deg,#8B5CF6,#EC4899); color:white;}
</style>
<div class="hero">
  <h1>🗣️ Speak Your Day</h1>
  <p>Say your plans. I'll list them and remind you out loud.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Record ----------
audio = st.audio_input("Tap the mic and tell me your plans")
if audio:
    data = audio.getvalue()
    digest = hashlib.md5(data).hexdigest()
    if digest != st.session_state.last_audio:
        st.session_state.last_audio = digest
        try:
            with st.spinner("Listening..."):
                text = transcribe_bytes(data)
            st.session_state.heard = text
            new = build_list(text)
            for item in new:
                item["done"] = False
                item["reminded"] = False
            st.session_state.tasks += new
            st.session_state.play = speak(summary(new))
        except Exception as e:
            st.error(f"Something went wrong: {e}")



if st.session_state.play:
    st.audio(st.session_state.play, format="audio/wav", autoplay=True)
    st.session_state.play = None
if st.session_state.heard:
    st.markdown(
        f'<div class="heard">🎧 <b>I heard:</b> {html.escape(st.session_state.heard)}</div>',
        unsafe_allow_html=True)
# ---------- Task list ----------
st.markdown("### 📝 Your day")
if not st.session_state.tasks:
    st.markdown('<div class="empty">No tasks yet. Tap the mic and tell me your plans ✨</div>',
                unsafe_allow_html=True)
for i, t in enumerate(st.session_state.tasks):
    if t["when"] and t["has_time"]:
        when = t["when"].strftime("%a %d %b, %I:%M %p")
    elif t["when"]:
        when = t["when"].strftime("%a %d %b")
    else:
        when = "no time set"
    with st.container(border=True):
        c1, c2 = st.columns([1, 8])
        t["done"] = c1.checkbox("done", value=t["done"], key=f"done_{i}",
                                label_visibility="collapsed")
        cls = "task done" if t["done"] else "task"
        c2.markdown(
            f'<div class="{cls}"><b>{html.escape(t["task"]).title()}</b><br>'
            f'<span class="when">🕒 {when}</span></div>',
            unsafe_allow_html=True)    



col1, col2 = st.columns(2)
if col1.button("➕ Test reminder (1 min)"):
    st.session_state.tasks.append({
        "task": "drink water",
        "when": datetime.now() + timedelta(minutes=1),
        "has_time": True, "done": False, "reminded": False,
    })
    st.rerun()
if col2.button("🗑️ Clear all"):
    st.session_state.tasks = []
    st.session_state.alerts = []
    st.session_state.heard = ""
    st.rerun()


# ---------- Reminder watcher (checks every 5 seconds) ----------
@st.fragment(run_every=5)
def reminder_watcher():
    now = datetime.now()
    new_audio = None
    for t in st.session_state.tasks:
        if (t["has_time"] and t["when"] and not t["reminded"]
                and not t["done"] and t["when"] <= now):
            t["reminded"] = True
            st.session_state.alerts.append(f"⏰ Reminder: {t['task']}")
            try:
                new_audio = speak(f"Reminder. {t['task']}.")
            except Exception:
                pass
    for a in st.session_state.alerts:
        st.warning(a)
    if new_audio:
        st.audio(new_audio, format="audio/wav", autoplay=True)


reminder_watcher()
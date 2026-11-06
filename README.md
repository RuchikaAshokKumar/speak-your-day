# 🗣️ Speak Your Day

**A voice-first to-do assistant in English, Hindi and Tamil, powered by Gnani AI's Prisma (speech to text) and Timbre (text to speech).**

Built for the **Great Indian AI Internship Challenge** by Ruchika Ashok Kumar, KIT - Kalaignarkarunanidhi Institute of Technology.

## The Problem
Typing a to-do list is slow and difficult for elderly people, students on the move, and anyone who finds typing hard. Important tasks get forgotten.

## The Solution
Speak Your Day lets you say your plans in one natural sentence. The app:
1. **Listens** and transcribes your speech with **Gnani Prisma**.
2. **Understands** the sentence and splits it into separate tasks with days and times.
3. **Speaks the list back** to you with **Gnani Timbre**.
4. **Reminds you out loud** at the scheduled time, with a spoken voice alert.

Example: "Tomorrow I have a physics test, call mom at 6 PM, and submit the report" becomes separate tasks, each with its time, read back to you in your own language.

## Languages
English, Hindi (हिन्दी) and Tamil (தமிழ்), chosen from a dropdown. Prisma and Timbre both receive the selected language code.

## Impact
- Makes task management accessible without typing.
- Helps elderly and first-time smartphone users.
- Brings voice AI to regional-language speakers.

## Tech Stack
Python, Streamlit, Gnani Prisma (STT), Gnani Timbre (TTS), Gnani REST APIs.

## How to Run
1. Install Python 3.10+ and run: `pip install -r requirements.txt`
2. Create a `.env` file in the project folder with your own key: `GNANI_API_KEY=your_key_here` (get a key at https://app.gnani.ai and never share it).
3. Start the app: `streamlit run app.py`
4. Allow microphone access in your browser.

## Files
- `app.py`: Streamlit interface, Gnani API calls, voice reminders
- `brain.py`: turns spoken sentences into tasks, days and times (English, Hindi, Tamil)

## Limitations and Next Steps
- Reminders play while the page is open (web app). A phone-notification version is planned.
- Task understanding uses rules; the next step is Gnani's Evon reasoning model for smarter parsing.
- Add more Indian languages supported by Prisma and Timbre, plus Hinglish.

## Demo
- Video demo: (add link)
- LinkedIn post: (add link)

#GnaniAI #GreatIndianAIInternshipChallenge
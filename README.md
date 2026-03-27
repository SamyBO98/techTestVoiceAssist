# Voice Appointment Assistant

A voice-based appointment booking agent built with LiveKit, Faster Whisper (STT), gTTS (TTS), and Ollama for date parsing. The agent answers an incoming call, asks the user for an appointment date, parses it, and saves it to a SQLite database via a Flask API.

---

## About this project

This repository is a technical test split into two parts:

**Part 1 - Development**: A functional voice agent that books appointments over a phone call.
The agent asks the user for a date, parses it, and saves it to a database via a REST API.
See the code in `agent.py`, `app.py`, and `db.py`.

**Part 2 - Architecture**: A high-level system architecture covering:
- Booking an appointment in an external system based on the client's request
- Notifying the dealership that a new call has been received

See the diagram in `high-level-architecture.pdf`.

---


## Architecture

```
User (browser)
        │
        ▼
   LiveKit Room
        │
        ▼
   agent.py  ──────────────────────────────────────────┐
   ├── FasterWhisperSTT   (speech → text, via CUDA)    │
   ├── GTTSPlugin         (text → speech, via gTTS)    │
   ├── AppointmentAgent   (conversation logic)         │
   └── Ollama gemma2:2b   (date parsing)               │
                                                       │  POST /end-of-call
                                                       ▼
                                                   app.py (Flask)
                                                       │
                                                       ▼
                                                calls_info.db (SQLite)
```

---

## Prerequisites

- Python 3.10+
- NVIDIA GPU with CUDA (required for Faster Whisper `float16`)  
  → CPU fallback available, see [Configuration](#configuration)
- [Ollama](https://ollama.com/) installed and running locally with `gemma2:2b` pulled
- A LiveKit server (cloud or self-hosted) with a valid `.env`

---

## Installation

```bash
# Clone the repo
git clone https://github.com/SamyBO98/AI_VoiceAssist
cd AI_VoiceAssist

# Create and activate virtual environment
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file at the root of the project with your LiveKit credentials:

```env
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

**CPU fallback** — if you don't have a NVIDIA GPU, edit `agent.py` in `_load_model()`:
```python
# Replace this:
self._model = WhisperModel(self._model_name, device="cuda", compute_type="float16")
# With this:
self._model = WhisperModel(self._model_name, device="cpu", compute_type="int8")
```

---

## Running the project

You need to run **two processes** simultaneously.

**1. Start the Flask API**
```bash
python app.py
```
Runs on `http://localhost:5000` by default.

**2. Start the LiveKit agent**

On Windows, use the provided PowerShell script (adds CUDA DLLs to PATH automatically):
> ⚠️ Before running `launch.ps1`, update the paths inside the script to match your own installation directory. Replace all occurrences of `C:\\Users\\samyb\\OneDrive\\Bureau\\techTestVoiceAssist` with the path where you cloned the repo.
```powershell
.\launch.ps1
```
> 💡 If you are using CPU instead of GPU, skip `launch.ps1` entirely and run the agent directly:

Or manually:
```bash
python agent.py connect --room test-room
```



## Generate a LiveKit token

To join the room and interact with the agent, generate an access token first:
```bash
python token_gen.py
```

Then paste the generated token in the LiveKit playground to connect to the room.


## Check the database

To verify that the appointment was correctly saved in the database, run:
```bash
python test/test_db_v2.py
```

This will print all the records stored in the database.

---

## Project structure

```
├── agent.py        # LiveKit agent (STT, TTS, conversation logic)
├── app.py          # Flask API, receives appointment data from agent
├── db.py           # SQLAlchemy model (CallInfo)
├── launch.ps1      # Windows launch script with CUDA PATH setup
├── .env            # LiveKit credentials (not committed)
└── calls_info.db   # SQLite database (auto-created on first run)
```

---

## How it works

1. A user joins a LiveKit room
2. The agent greets them and asks for an appointment date
3. The user's speech is transcribed by **Faster Whisper** (local, GPU)
4. The agent confirms and schedules a hangup after 5 seconds
5. **Ollama** (`gemma2:2b`) parses the raw transcription into `DD/MM/YYYY HH:MM` format
6. The formatted date is sent via POST to the Flask API
7. Flask saves the appointment to the SQLite database
8. The agent disconnects from the room

---

## Dependencies

| Package | Role |
|---|---|
| `livekit-agents` | Agent framework and room management |
| `livekit-plugins-silero` | Voice Activity Detection (VAD) |
| `faster-whisper` | Local speech-to-text (Whisper via CTranslate2) |
| `gTTS` | Google Text-to-Speech |
| `pydub` | MP3 → PCM audio conversion |
| `scipy` | Audio resampling (24kHz → 16kHz) |
| `ollama` | Local LLM for date parsing |
| `flask` | REST API |
| `flask-sqlalchemy` | ORM for SQLite |
| `python-dotenv` | `.env` file loading |

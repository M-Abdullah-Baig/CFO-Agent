import os, io, tempfile
import streamlit as st
import openai
import pandas as pd
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ── Load .env ───────────────────────────────────────
load_dotenv(".env")
openai.api_key = os.getenv("OPENAI_API_KEY")
GOOGLE_JSON = os.getenv("GOOGLE_SERVICE_JSON_PATH")
FOLDER_ID   = os.getenv("DRIVE_FOLDER_ID")

# ── Page Setup ──────────────────────────────────────
st.set_page_config("📊 AI CFO Chatbot", page_icon="💼", layout="wide")
st.title("📊 AI CFO Chatbot (LLM for Q/A)")

# ── Sidebar Settings ────────────────────────────────
with st.sidebar:
    st.header("📂 Google Drive Statements")
    st.checkbox("🔈 Always speak reply", value=True, key="always_speak")

# ── Init Session State ──────────────────────────────
if "history" not in st.session_state: st.session_state.history = []
if "reply" not in st.session_state: st.session_state.reply = ""

# ── Google Drive Setup ──────────────────────────────
@st.cache_resource
def connect_drive():
    creds = Credentials.from_service_account_file(GOOGLE_JSON, scopes=["https://www.googleapis.com/auth/drive.readonly"])
    return build("drive", "v3", credentials=creds)

@st.cache_data
def list_files():
    result = drive.files().list(q=f"'{FOLDER_ID}' in parents and trashed=false",
                                fields="files(id,name,modifiedTime,mimeType)").execute()
    return result.get("files", [])

@st.cache_data
def download_text(file_id, name):
    request = drive.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done: _, done = downloader.next_chunk()
    fh.seek(0)
    if name.endswith(".csv") or name.endswith(".txt"):
        return fh.read().decode("utf-8", errors="ignore")
    elif name.endswith(".xlsx"):
        df = pd.read_excel(fh)
        return df.to_csv(index=False)
    elif name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(fh)
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    return ""

drive = connect_drive()
files = list_files()

# ── Build Corpus from Drive ─────────────────────────
corpus = ""
for f in files:
    with st.spinner(f"Reading {f['name']}..."):
        text = download_text(f["id"], f["name"])
        corpus += f"### {f['name']} ({f['modifiedTime'][:10]})\n{text}\n\n"

# ── Voice Input ─────────────────────────────────────
try:
    from streamlit_mic_recorder import mic_recorder
    audio_dict = mic_recorder("🎙️ Speak", "🛑 Stop", use_container_width=True)
    audio_bytes = audio_dict["bytes"] if audio_dict else None
except:
    audio_bytes = None
    st.warning("Install `streamlit-mic-recorder` for voice input.")

user_input = ""

# ── Transcribe with Whisper ─────────────────────────
if audio_bytes:
    with st.spinner("🎧 Transcribing…"):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.write(audio_bytes); tmp.close()
        with open(tmp.name, "rb") as f:
            whisper = openai.audio.transcriptions.create(model="whisper-1", file=f, language="en")
        os.remove(tmp.name)
        user_input = whisper.text.strip()
        st.audio(audio_bytes, format="audio/wav")
        st.write("**🎙️ You said:**", user_input)

# ── Text Fallback ───────────────────────────────────
user_input = st.text_input("💬 Or type your question:", value=user_input)

# ── Submit to GPT ───────────────────────────────────
if st.button("🤖 Ask AI CFO") and user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.spinner("💡 LLM is thinking…"):
        messages = [{
            "role": "system",
            "content": f"""
        You are an AI CFO chatbot. You analyze financial statements and provide insights.

        Rules:
        1. Always answer CFO-style financial questions clearly and concisely. 
        2. If the user asks for a chart, graph, plot, or visualization:
            - Generate valid Python code using matplotlib or plotly.
            - Wrap the code inside triple backticks with "python".
            - Make sure the last line renders the chart in Streamlit (st.pyplot(plt) or st.plotly_chart(fig)).
        3. Along with the code, provide a short explanation of what the chart shows.
        4. Use only data from the provided reports (below) or from user input:
        {corpus}
        """
        }]

        messages += st.session_state.history[-6:]  # recent history
        response = openai.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.4)
        answer = response.choices[0].message.content.strip()
        st.session_state.history.append({"role": "assistant", "content": answer})
        st.session_state.reply = answer

# ── Chat Display ────────────────────────────────────
for msg in st.session_state.history:
    role = "👤 You" if msg["role"] == "user" else "🤖 CFO"
    st.markdown(f"**{role}:** {msg['content']}")

# ── TTS Read Aloud ──────────────────────────────────
if st.session_state.reply and st.session_state.always_speak:
    with st.spinner("🔊 Generating voice…"):
        speech = openai.audio.speech.create(model="tts-1", voice="alloy", input=st.session_state.reply[:4000])
        st.audio(speech.read(), format="audio/mp3")

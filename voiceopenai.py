import os, tempfile
import streamlit as st
import openai
from dotenv import load_dotenv

# ── Load environment variables ───────────────────────────────────────────
load_dotenv(".env")
openai.api_key = os.getenv("OPENAI_API_KEY")

# ── Streamlit page setup ────────────────────────────────────────────────
st.set_page_config(page_title="🎤 GPT Voice Chatbot", page_icon="🤖")
st.title("🎤 Voice Chatbot with GPT-4o + Whisper + TTS")

# ── Sidebar Settings ────────────────────────────────────────────────────
with st.sidebar:
    st.header("🎛️ Settings")
    st.checkbox("🔈 Always speak replies", value=True, key="always_speak")

# ── Persistent state ────────────────────────────────────────────────────
if "reply" not in st.session_state:
    st.session_state.reply = ""

# ── Voice Input ─────────────────────────────────────────────────────────
try:
    from streamlit_mic_recorder import mic_recorder
    audio_dict = mic_recorder("🎙️ Speak", "🛑 Stop", use_container_width=True)
    audio_bytes = audio_dict["bytes"] if audio_dict else None
except ModuleNotFoundError:
    st.error("Install:  pip install streamlit-mic-recorder")
    audio_bytes = None

# ── Whisper Speech-to-Text ──────────────────────────────────────────────
user_input = ""
if audio_bytes:
    with st.spinner("🧠 Transcribing…"):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.write(audio_bytes)
        tmp_path = tmp.name
        tmp.close()

        with open(tmp_path, "rb") as f:
            whisper = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="en"
            )
        user_input = whisper.text.strip()
        os.remove(tmp_path)

        st.audio(audio_bytes, format="audio/wav")
        st.write("**You said:**", user_input)

# ── Text input fallback ─────────────────────────────────────────────────
user_input = st.text_input("💬 Or type your question:", value=user_input)

# ── GPT Response ────────────────────────────────────────────────────────
if st.button("🤖 Ask GPT"):
    if not user_input:
        st.warning("Please speak or type something first.")
    else:
        with st.spinner("💡 GPT-4o thinking…"):
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": user_input}],
                temperature=0.4
            )
        st.session_state.reply = response.choices[0].message.content.strip()

# ── Show GPT reply ──────────────────────────────────────────────────────
if st.session_state.reply:
    st.success("✅ GPT-4o replied:")
    st.write(st.session_state.reply)

    mute_this = st.checkbox("🔇 Mute this reply", key=f"mute_{len(st.session_state.reply)}")

    # ── TTS Playback ────────────────────────────────────────────────────
    if st.session_state.always_speak and not mute_this:
        with st.spinner("🔊 Generating voice…"):
            speech = openai.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=st.session_state.reply
            )
            st.audio(speech.read(), format="audio/mp3")

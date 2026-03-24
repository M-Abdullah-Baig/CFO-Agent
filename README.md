# AI CFO Agent

An AI-powered CFO assistant built with Streamlit that analyzes financial documents from Google Drive and answers questions using LLMs. It supports voice input (Whisper), text queries, and text-to-speech responses (TTS).

## 🚀 Features
📂 Google Drive Integration
Automatically fetches financial statements (PDF, CSV, Excel, TXT)
Builds a unified corpus for analysis
🤖 AI CFO Assistant
Uses GPT-4o to answer financial questions
Provides insights like revenue trends, cost breakdowns, etc.
📊 Auto Chart Generation
Generates Python (matplotlib/plotly) code for visualizations
Renders charts directly in Streamlit
🎙️ Voice Input (Whisper)
Speak your query instead of typing
Converts speech → text using OpenAI Whisper
🔊 Text-to-Speech (TTS)
AI responses are read aloud automatically
💬 Conversation Memory
Maintains chat history for contextual responses

## 🧠 Use Cases
Financial statement analysis
CFO-level insights generation
Automated reporting & visualization
Voice-enabled AI dashboards

## 🏗️ Tech Stack
Frontend: Streamlit
LLM: OpenAI GPT-4o
Speech-to-Text: Whisper
Text-to-Speech: OpenAI TTS
Storage: Google Drive API
Data Processing: Pandas

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
git clone https://github.com/M-Abdullah-Baig/CFO-Agent.git

cd ai-cfo-chatbot

### 2️⃣ Install Dependencies
pip install -r requirements.txt

### 3️⃣ Environment Variables

Create a .env file:

OPENAI_API_KEY=your_openai_api_key
GOOGLE_SERVICE_JSON_PATH=path_to_service_account.json
DRIVE_FOLDER_ID=your_google_drive_folder_id

### 4️⃣ Google Drive Setup
Create a Service Account in Google Cloud
Enable Google Drive API
Share your Drive folder with the service account email
Download JSON credentials

### 5️⃣ Run the App
streamlit run app.py

### 🎤 Voice Support Setup

Install mic recorder:
pip install streamlit-mic-recorder

### 📊 Supported File Types
PDF (.pdf)
Excel (.xlsx)
CSV (.csv)
Text (.txt)

### 🧾 Example Queries
"What is the total revenue trend?"
"Show a profit vs expense chart"
"Summarize this financial report"
"Which month had highest growth?"

### ⚠️ Notes
Ensure Google Drive folder contains readable files
Large documents may increase response time
Whisper requires audio input support

### 🔮 Future Improvements
RAG with vector database (FAISS / Pinecone)
Multi-user authentication
Real-time dashboards
Deployment (Streamlit Cloud / AWS)

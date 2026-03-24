import os, io
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# PDF reader
from pypdf import PdfReader

# Load env vars
load_dotenv(".env")
SERVICE_JSON = os.getenv("GOOGLE_SERVICE_JSON_PATH")
FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

# Authenticate
creds = Credentials.from_service_account_file(
    SERVICE_JSON, scopes=["https://www.googleapis.com/auth/drive.readonly"]
)
drive = build("drive", "v3", credentials=creds)

# List all files
files = drive.files().list(
    q=f"'{FOLDER_ID}' in parents and trashed=false and mimeType='application/pdf'",
    fields="files(id,name)"
).execute().get("files", [])

assert files, "No PDF files found in folder!"

# Pick the first PDF
pdf_file = files[0]
print(f"📄 Found PDF: {pdf_file['name']}")

# Download it
request = drive.files().get_media(fileId=pdf_file["id"])
buf = io.BytesIO()
MediaIoBaseDownload(buf, request).next_chunk()

# Extract text
reader = PdfReader(buf)
text = "\n".join(p.extract_text() or "" for p in reader.pages)

print("\n📑 Extracted Text Preview:\n")
print(text[:1000])  # first 1000 characters


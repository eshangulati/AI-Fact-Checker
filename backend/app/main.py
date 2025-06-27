# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .transcriber import get_video_info, transcribe_video
from .claim_extractor import extract_claims

app = FastAPI(title="YouTube Fact-Checker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/video-info")
async def video_info(payload: dict):
    url = payload.get("url")
    if not url:
        raise HTTPException(400, "Missing `url`")
    return get_video_info(url)

@app.post("/api/factcheck")
async def factcheck(payload: dict):
    url = payload.get("url")
    if not url:
        raise HTTPException(400, "Missing `url`")
    transcript = transcribe_video(url)
    return {"transcript": transcript}

@app.post("/api/extract-claims")
def extract(payload: dict):
    url = payload.get("url")
    if not url:
        raise HTTPException(400, "Missing `url`")
    # 1) Transcribe
    transcript = transcribe_video(url)
    # 2) Extract claims via Mistral-7B
    claims = extract_claims(transcript)
    return {"transcript": transcript, "claims": claims}
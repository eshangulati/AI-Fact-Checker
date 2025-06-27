import os
import tempfile
from yt_dlp import YoutubeDL
import whisper
import re

# Load Whisper model once at startup
_model = whisper.load_model("small")  # choose "tiny.en" or larger as needed

def get_video_info(youtube_url: str) -> dict:
    """
    Retrieve video metadata (thumbnail URL, title) without downloading audio.
    """
    ydl_opts = {"skip_download": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
    return {
        "thumbnail_url": info.get("thumbnail"),
        "title": info.get("title"),
    }


def transcribe_video(youtube_url: str) -> str:
    """
    Download YouTube audio, transcribe full audio with Whisper, and
    format the transcript into readable sentences.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Define base path (no extension) so FFmpegExtractAudio adds .wav
        base = os.path.join(tmpdir, "audio")
        wav_path = base + ".wav"

        # Download audio and convert to WAV
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": base,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # Ensure the WAV file exists
        if not os.path.exists(wav_path):
            raise RuntimeError(f"Expected audio at {wav_path}, but file was not found.")

        # Use Whisper's built-in transcription method for the full audio
        result = _model.transcribe(wav_path)
        raw_text = result.get("text", "")

        # Split into sentences, preserving punctuation
        parts = re.split(r"([.!?])", raw_text)
        sentences = [a + b for a, b in zip(parts[0::2], parts[1::2])] if parts else []

        # Join with double newlines for readability in the frontend
        transcript = "\n\n".join(sentences)
        return transcript

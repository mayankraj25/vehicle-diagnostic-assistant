import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
from faster_whisper import WhisperModel
from config import WHISPER_MODEL

print("Loading Whisper model...")
whisper = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")

def record_audio(seconds=5, sample_rate=16000):
    print(f"Recording for {seconds} seconds... Speak now")
    audio=sd.rec(
        int(seconds*sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    return audio, sample_rate

def transcribe_audio(audio, sample_rate):
    with tempfile.NamedTemporaryFile(suffix=".wav",delete=False) as f:
        sf.write(f.name,audio,sample_rate)
        segements,_=whisper.transcribe(f.name,beam_size=3,language="en")
        text=" ".join([s.text.strip() for s in segements])
        os.unlink(f.name)
    return text.strip()

def listen():
    audio,sr=record_audio()
    return transcribe_audio(audio,sr)


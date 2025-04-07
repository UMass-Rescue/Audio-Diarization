from typing import TypedDict, Dict, List
from pathlib import Path
from flask_ml.flask_ml_server import MLServer
from flask_ml.flask_ml_server.models import (
    DirectoryInput,
    FileResponse,
    InputSchema,
    InputType,
    ResponseBody,
    TaskSchema,
)
from pyannote.audio import Pipeline
import sqlite3
from datetime import datetime
import json
from collections import defaultdict

#Initialize and configure the app
server = MLServer(__name__)
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.0")

#Database setup
def init_db():
    conn = sqlite3.connect('diarization_results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS diarization_results
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  filename TEXT NOT NULL,
                  speaker TEXT NOT NULL,
                  start_time REAL NOT NULL,
                  end_time REAL NOT NULL,
                  processing_date TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def store_results(filename, segments):
    conn = sqlite3.connect('diarization_results.db')
    c = conn.cursor()
    current_time = datetime.now().isoformat()
    for segment in segments:
        c.execute('''INSERT INTO diarization_results 
                    (filename, speaker, start_time, end_time, processing_date)
                    VALUES (?, ?, ?, ?, ?)''',
                 (filename, segment["speaker"], segment["start"], 
                  segment["end"], current_time))
    conn.commit()
    conn.close()

#Initialize database
init_db()

#Audio processing function
def process_audio_file(file_path: Path):
    print(f"Processing audio file: {file_path.name}")
    diarization = pipeline(str(file_path))
    segments = []
    
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end
        })

    store_results(file_path.name, segments)
    print(f"Saved {len(segments)} segments to database")
    
    #JSON
    output = {file_path.name: format_segments(segments)}
    with open('diarization_output.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    return segments

def format_segments(segments):
    speaker_segments = defaultdict(list)
    for segment in segments:
        speaker = segment["speaker"]
        start = f'{segment["start"]:.2f}'
        end = f'{segment["end"]:.2f}'   
        speaker_segments[speaker].append(f'{start}-{end}')
    return {k: " ".join(v) for k, v in speaker_segments.items()}
if __name__ == "__main__":
    # Configure these paths:
    AUDIO_FILE = Path("input\TOEFL.mp3")  #audio file path
    OUTPUT_DIR = Path("./output")
    
    if not AUDIO_FILE.exists():
        print(f"Error: Audio file not found at {AUDIO_FILE}")
    else:
        OUTPUT_DIR.mkdir(exist_ok=True)
        segments = process_audio_file(AUDIO_FILE)
        
        # Print results to console
        print("\nSpeaker Diarization Results:")
        for seg in segments:
            print(f"{seg['speaker']}: {seg['start']:.2f}s - {seg['end']:.2f}s")
        
        print("\nDatabase stored successfully!")
        print(f" View results with: sqlite3 diarization_results.db 'SELECT * FROM diarization_results;'")
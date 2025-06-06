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
from pyannote.audio import Pipeline, Audio
from pyannote.core import Segment
import whisper
import json
from collections import defaultdict
from utils import diarize_text, load_pyannote_pipeline_from_pretrained  
import csv

# Load models 
#pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.0")

#To use local model
PATH_TO_CONFIG = "./models/pyannote_diarization_config.yaml"
pipeline = load_pyannote_pipeline_from_pretrained(PATH_TO_CONFIG)
asr_model = whisper.load_model("medium.en")

class AudioInputs(TypedDict):
    input_dir: DirectoryInput
    output_dir: DirectoryInput

class AudioParameters(TypedDict):
    pass

def create_task_schema() -> TaskSchema:
    input_schema = InputSchema(
        key="input_dir",
        label="Path to the directory containing audio files",
        input_type=InputType.DIRECTORY
    )
    output_schema = InputSchema(
        key="output_dir",
        label="Path to the output directory",
        input_type=InputType.DIRECTORY
    )
    return TaskSchema(
        inputs=[input_schema, output_schema],
        parameters=[]
    )

def is_audio_file(file_path: Path) -> bool:
    audio_extensions = {".wav", ".mp3", ".flac", ".ogg"}
    return file_path.suffix.lower() in audio_extensions

# Format functions for different endpoints
def format_diarization_segments(segments: List[Dict[str, float]]) -> Dict[str, List[str]]:
    """Format speaker segments for diarization-only endpoint"""
    speaker_segments = defaultdict(list)
    for segment in segments:
        speaker = segment["speaker"]
        start = f'{segment["start"]:.2f}'
        end = f'{segment["end"]:.2f}'   
        speaker_segments[speaker].append(f'{start} - {end}')
    return dict(speaker_segments)

def format_transcription_only(asr_result: Dict) -> Dict[str, str]:
    """Format transcription for transcription-only endpoint"""
    return {"transcription": asr_result["text"]}

def format_combined_result(diarized_result) -> Dict[str, Dict[str, str]]:
    """Format combined diarization and transcription"""
    output = {}
    speaker_segments = {}
    for seg, spk, sent in diarized_result:
        if spk not in speaker_segments:
            speaker_segments[spk] = []
        speaker_segments[spk].append((seg.start, seg.end, sent))
    for speaker, segments in speaker_segments.items():
        speaker_dict = {}
        for start, end, text in segments:
            time_range = f"{start:.1f}-{end:.1f}"
            speaker_dict[time_range] = text
        output[speaker] = speaker_dict
    return output

def save_as_csv(data: dict, csv_path: Path):
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        first_item = next(iter(data.values()))
        if "transcription" in first_item:
            writer.writerow(["Audio File", "Transcription"])
            for audio_file, content in data.items():
                writer.writerow([audio_file, content["transcription"]])

        elif isinstance(first_item, dict) and any(
            isinstance(v, dict) for v in first_item.values()
        ):
            writer.writerow(["Audio File", "Speaker", "Time Range", "Text"])

            for audio_file, speakers in data.items():
                for speaker, segments in speakers.items():
                    for time_range, text in segments.items():
                        writer.writerow([audio_file, speaker, time_range, text])
        else:
            writer.writerow(["Audio File", "Speaker", "Time Range"])
            for audio_file, speakers in data.items():
                for speaker, segments in speakers.items():
                    for segment in segments:
                        writer.writerow([audio_file, speaker, segment])

# Initialize server
server = MLServer(__name__)
server.add_app_metadata(
    name="Speaker Diarization and Transcription",
    author="Christina, Swetha, Nikita",
    version="2.0",
    info="app-info.md"
)

@server.route("/diarize", order=0, task_schema_func=create_task_schema, short_title="Speaker Diarization")
def diarize_only(inputs: AudioInputs, parameters: AudioParameters) -> ResponseBody:
    input_path = Path(inputs["input_dir"].path)
    output_path = Path(inputs["output_dir"].path)
    output_path.mkdir(parents=True, exist_ok=True)
    results = {}

    audio_files = [input_path] if input_path.is_file() else list(input_path.glob("*"))
    
    for audio_file in audio_files:
        if is_audio_file(audio_file):
            try:
                diarization = pipeline(str(audio_file))
                segments = []
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    segments.append({
                        "speaker": speaker,
                        "start": turn.start,
                        "end": turn.end
                    })
                results[audio_file.name] = format_diarization_segments(segments)
            except Exception as e:
                results[audio_file.name] = f"Error: {str(e)}"
        else:
            results[audio_file.name] = "Error: Not a valid audio file"

    csv_file = output_path / "diarize_output.csv"
    save_as_csv(results, csv_file)
    return ResponseBody(FileResponse(path=str(csv_file), file_type="csv"))

@server.route("/transcribe", order=1, task_schema_func=create_task_schema, short_title="Audio Transcription")
def transcribe_only(inputs: AudioInputs, parameters: AudioParameters) -> ResponseBody:
    input_path = Path(inputs["input_dir"].path)
    output_path = Path(inputs["output_dir"].path)
    output_path.mkdir(parents=True, exist_ok=True)
    results = {}

    audio_files = [input_path] if input_path.is_file() else list(input_path.glob("*"))
    
    for audio_file in audio_files:
        if is_audio_file(audio_file):
            try:
                asr_result = asr_model.transcribe(str(audio_file))
                results[audio_file.name] = format_transcription_only(asr_result)
            except Exception as e:
                results[audio_file.name] = f"Error: {str(e)}"
        else:
            results[audio_file.name] = "Error: Not a valid audio file"

    csv_file = output_path / "transcribe_output.csv"
    save_as_csv(results, csv_file)
    return ResponseBody(FileResponse(path=str(csv_file), file_type="csv"))

@server.route("/diarize-transcribe", order=2, task_schema_func=create_task_schema, short_title="Speaker Diarization + Transcription")
def diarize_and_transcribe(inputs: AudioInputs, parameters: AudioParameters) -> ResponseBody:
    input_path = Path(inputs["input_dir"].path)
    output_path = Path(inputs["output_dir"].path)
    output_path.mkdir(parents=True, exist_ok=True)
    results = {}

    audio_files = [input_path] if input_path.is_file() else list(input_path.glob("*"))
    
    for audio_file in audio_files:
        if is_audio_file(audio_file):
            try:
                diarization = pipeline(str(audio_file))
                asr_result = asr_model.transcribe(str(audio_file))
                aligned = diarize_text(asr_result, diarization)
                results[audio_file.name] = format_combined_result(aligned)
            except Exception as e:
                results[audio_file.name] = f"Error: {str(e)}"
        else:
            results[audio_file.name] = "Error: Not a valid audio file"

    csv_file = output_path / "diarize_and_transcribe_output.csv"
    save_as_csv(results, csv_file)
    return ResponseBody(FileResponse(path=str(csv_file), file_type="csv"))

server.run()
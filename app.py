from typing import TypedDict
from pathlib import Path
from flask_ml.flask_ml_server import MLServer, load_file_as_string
from flask_ml.flask_ml_server.models import (
    DirectoryInput,
    FileResponse,
    InputSchema,
    InputType,
    ResponseBody,
    TaskSchema,
)
from pyannote.audio import Pipeline
from pyannote.core import Segment
from pyannote.audio import Audio
import json

# Load the pre-trained speaker diarization pipeline
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.0")

class DiarizationInputs(TypedDict):
    input_dir: DirectoryInput
    output_dir: DirectoryInput

class DiarizationParameters(TypedDict):
    pass  # No parameters needed for this task

def create_diarization_task_schema() -> TaskSchema:
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

# Create a server instance
server = MLServer(__name__)

server.add_app_metadata(
    name="Speaker Diarization",
    author="Your Name",
    version="1.0",
    info="app-info.md"
)

def is_audio_file(file_path: Path) -> bool:
    """Check if a file is an audio file based on its extension."""
    audio_extensions = {".wav", ".mp3", ".flac", ".ogg"}  # Add more if needed
    return file_path.suffix.lower() in audio_extensions

@server.route("/diarize", task_schema_func=create_diarization_task_schema)
def diarize(inputs: DiarizationInputs, parameters: DiarizationParameters) -> ResponseBody:
    input_path = Path(inputs["input_dir"].path)
    output_path = Path(inputs["output_dir"].path)
    output_path.mkdir(parents=True, exist_ok=True)  # Create output directory if it doesn't exist

    results = {}

    if input_path.is_file():
        # Process a single file (if it's an audio file)
        if is_audio_file(input_path):
            diarization = pipeline(str(input_path))
            results[input_path.name] = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                results[input_path.name].append({
                    "speaker": speaker,
                    "start": round(turn.start, 2),
                    "end": round(turn.end, 2)
                })
        else:
            results[input_path.name] = "Error: Not a valid audio file"
    else:
        # Process all files in the input directory (only audio files)
        for input_file in input_path.glob("*"):
            if input_file.is_file() and is_audio_file(input_file):
                diarization = pipeline(str(input_file))
                results[input_file.name] = []
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    results[input_file.name].append({
                        "speaker": speaker,
                        "start": round(turn.start, 2),
                        "end": round(turn.end, 2)
                    })

    # Save results to a JSON file in the specified output directory
    output_file = output_path / "output.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    return ResponseBody(FileResponse(path=str(output_file), file_type="json"))

if __name__ == "__main__":
    server.run()